import json
import logging
import os
import threading
from dataclasses import dataclass
from importlib import import_module
import re
from typing import Any, Dict, List, Sequence, Tuple
import unicodedata

from django.core.exceptions import ImproperlyConfigured
from PIL import Image, ImageOps

from productos.category_tree import CATEGORY_TREE

# Configurar un logger específico para este módulo
logger = logging.getLogger(__name__)

HYPOTHESIS_TEMPLATE = "Este texto es sobre {}."
MODEL_NAME = "Recognai/bert-base-spanish-wwm-cased-xnli"
IMAGE_MODEL_NAME = "openai/clip-vit-base-patch32"
MAIN_THRESHOLD = 0.40
SUB_THRESHOLD = 0.35
NORMALIZATION_CONFIDENCE = 0.95
MAIN_HIGH_CONFIDENCE = 0.70
MAIN_SCORE_MARGIN = 0.12
MAIN_CANDIDATE_LIMIT = 3
SUB_CANDIDATE_LIMIT = 5
COMBINED_MAIN_WEIGHT = 0.35
COMBINED_SUB_WEIGHT = 0.55
COMBINED_LEXICAL_WEIGHT = 0.10
TEXT_MAIN_BLEND_WEIGHT = 0.70
IMAGE_MAIN_BLEND_WEIGHT = 0.30
MIN_IMAGE_CONFIDENCE_TO_BLEND = 0.30

TOKEN_STOPWORDS = {
    "con",
    "para",
    "por",
    "del",
    "las",
    "los",
    "una",
    "uno",
    "uns",
    "de",
    "el",
    "la",
    "and",
    "for",
    "the",
    "usb",
    "hdmi",
    "vga",
    "rj45",
    "tipo",
    "tipoa",
    "tipoc",
}


def _collect_paths(node: Dict, trail: List[str], acc: List[str], seen: set) -> None:
    """Construye etiquetas de ruta 'Padre > Hijo' asegurando unicidad."""
    base_label = " > ".join(trail + [node["name"]])
    label = base_label
    if label in seen:
        label = f"{base_label} ({node.get('slug', '')})"
    seen.add(label)
    acc.append(label)
    for child in node.get("children") or []:
        _collect_paths(child, trail + [node["name"]], acc, seen)


def _build_category_maps() -> Tuple[List[str], Dict[str, List[str]], Dict[str, str]]:
    """Genera listas de etiquetas a partir del árbol maestro."""
    main_categories: List[str] = []
    subcategories: Dict[str, List[str]] = {}
    generic_by_main: Dict[str, str] = {}

    for root in CATEGORY_TREE:
        main = root["name"]
        main_categories.append(main)
        paths: List[str] = []
        seen: set[str] = set()
        for child in root.get("children", []):
            _collect_paths(child, [main], paths, seen)
        if not paths:
            paths = [main]
        subcategories[main] = paths
        generic_by_main[main] = paths[0]

    return main_categories, subcategories, generic_by_main


def first_path(main_label: str, leaf_name: str) -> str | None:
    """Devuelve la primera ruta que termina con leaf_name para ese main."""
    leaf_lower = leaf_name.lower()
    for path in SUBCATEGORIES.get(main_label, []):
        if path.lower().endswith(leaf_lower):
            return path
    return GENERIC_SUBCATEGORY_BY_MAIN.get(main_label)


def safe_path(main_label: str, leaf_name: str) -> str:
    return first_path(main_label, leaf_name) or GENERIC_SUBCATEGORY_BY_MAIN.get(main_label, leaf_name)


MAIN_CATEGORIES, SUBCATEGORIES, GENERIC_SUBCATEGORY_BY_MAIN = _build_category_maps()

MAIN_CATEGORY_BY_SLUG: Dict[str, str] = {root["slug"]: root["name"] for root in CATEGORY_TREE if root.get("slug")}


def _build_node_name_index() -> Dict[tuple[str, str], str]:
    index: Dict[tuple[str, str], str] = {}
    for root in CATEGORY_TREE:
        main_slug = root.get("slug")
        if not main_slug:
            continue
        stack = list(root.get("children") or [])
        while stack:
            node = stack.pop()
            node_slug = node.get("slug")
            if node_slug:
                index[(main_slug, node_slug)] = node["name"]
            stack.extend(node.get("children") or [])
    return index


def _path_by_slug(main_slug: str, leaf_slug: str) -> str | None:
    for root in CATEGORY_TREE:
        if root.get("slug") != main_slug:
            continue
        stack: list[tuple[Dict, List[str]]] = [(root, [root["name"]])]
        while stack:
            node, trail = stack.pop()
            if node.get("slug") == leaf_slug:
                return " > ".join(trail)
            for child in node.get("children") or []:
                stack.append((child, trail + [child["name"]]))
    return None


NODE_NAME_BY_SLUG: Dict[tuple[str, str], str] = _build_node_name_index()


def safe_path_from_slugs(main_slug: str, leaf_slug: str) -> str:
    main_label = MAIN_CATEGORY_BY_SLUG.get(main_slug, main_slug)
    path = _path_by_slug(main_slug, leaf_slug)
    if path:
        return path
    leaf_name = NODE_NAME_BY_SLUG.get((main_slug, leaf_slug), leaf_slug)
    return safe_path(main_label, leaf_name)

_pipeline = None
_image_pipeline = None
_image_pipeline_load_failed = False


def get_pipeline():
    """
    Carga perezosa del pipeline de zero-shot classification de forma segura para cada proceso.
    El pipeline se carga una vez por proceso de worker cuando se llama por primera vez.
    """
    global _pipeline
    if _pipeline is None:
        logger.info("Pipeline no está cargado en este proceso. Iniciando la carga...")
        try:
            transformers = import_module("transformers")
            logger.info(f"Cargando el modelo '{MODEL_NAME}' en la CPU. Esto puede tardar la primera vez...")
            
            _pipeline = transformers.pipeline(
                "zero-shot-classification",
                model=MODEL_NAME,
                device="cpu",
            )
            logger.info("¡Pipeline de Transformers cargado y listo en este proceso!")
        except (ModuleNotFoundError, ImproperlyConfigured) as exc:
            logger.error(
                "El paquete 'transformers' no está instalado o falta una configuración. "
                "La clasificación AI no funcionará.",
                exc_info=True
            )
            raise  # Relanzar para que la tarea falle explícitamente
        except Exception as e:
            logger.error(f"Error inesperado al cargar el pipeline: {e}", exc_info=True)
            raise

    return _pipeline


def get_image_pipeline():
    """
    Carga opcional del clasificador visual.
    Si falla (modelo no disponible, dependencias, etc.), devuelve None y la
    clasificación continúa solo con texto.
    """
    global _image_pipeline, _image_pipeline_load_failed
    if _image_pipeline_load_failed:
        return None
    if _image_pipeline is None:
        logger.info("Pipeline de visión no está cargado. Intentando inicializar...")
        try:
            transformers = import_module("transformers")
            _image_pipeline = transformers.pipeline(
                "zero-shot-image-classification",
                model=IMAGE_MODEL_NAME,
                device="cpu",
            )
            logger.info("Pipeline de visión inicializado correctamente.")
        except (ModuleNotFoundError, ImproperlyConfigured):
            logger.warning(
                "No se pudo cargar el pipeline de visión por dependencias/configuración. "
                "Se usará solo clasificación textual.",
                exc_info=True,
            )
            _image_pipeline_load_failed = True
            return None
        except Exception:
            logger.warning(
                "No se pudo cargar el pipeline de visión. Se usará solo clasificación textual.",
                exc_info=True,
            )
            _image_pipeline_load_failed = True
            return None
    return _image_pipeline


@dataclass
class ClassificationResult:
    main: str
    sub: str | None
    main_score: float
    sub_score: float | None


class NormalizationRule:
    def __init__(
        self,
        keywords: Sequence[str],
        main: str | Sequence[str],
        sub: str | Dict[str, str | None],
    ) -> None:
        self.keywords = tuple(k.lower() for k in keywords)
        self.main_targets = main if isinstance(main, Sequence) and not isinstance(main, str) else (main,)
        self.sub_targets = sub

    def matches(self, text: str) -> bool:
        lower = text.lower()
        return any(keyword in lower for keyword in self.keywords)

    def resolve_main(self, predicted: str) -> str:
        if predicted in self.main_targets:
            return predicted
        return self.main_targets[0]  # type: ignore[index]

    def resolve_sub(self, main_label: str) -> str | None:
        if isinstance(self.sub_targets, dict):
            return self.sub_targets.get(main_label) or next(iter(self.sub_targets.values()))
        return self.sub_targets  # type: ignore[return-value]



HARDWARE_SLUG = "computo-hardware"
PRINT_SLUG = "impresion-y-copiado"
AUDIO_VIDEO_SLUG = "audio-y-video"
HARDWARE_MAIN = MAIN_CATEGORY_BY_SLUG.get(HARDWARE_SLUG, "Computo (Hardware)")
PRINT_MAIN = MAIN_CATEGORY_BY_SLUG.get(PRINT_SLUG, "Impresion y Copiado")
AUDIO_VIDEO_MAIN = MAIN_CATEGORY_BY_SLUG.get(AUDIO_VIDEO_SLUG, "Audio y Video")

MAIN_IMAGE_PROMPTS_BY_SLUG = {
    "computo-hardware": "computer hardware and peripherals",
    "audio-y-video": "audio and video electronics like projectors and screens",
    "energia": "power equipment, batteries, ups or chargers",
    "impresion-y-copiado": "printers, copiers and printing supplies",
    "punto-de-venta-pos": "point of sale equipment and POS terminals",
    "seguridad-y-vigilancia": "security cameras and surveillance equipment",
    "software-y-servicios": "software license or digital service product",
}


def _build_image_prompt_map() -> Dict[str, str]:
    prompt_map: Dict[str, str] = {}
    for main in MAIN_CATEGORIES:
        slug = next(
            (root.get("slug") for root in CATEGORY_TREE if root.get("name") == main and root.get("slug")),
            None,
        )
        if slug:
            prompt_map[main] = MAIN_IMAGE_PROMPTS_BY_SLUG.get(slug, f"{main} product")
        else:
            prompt_map[main] = f"{main} product"
    return prompt_map


MAIN_IMAGE_PROMPTS = _build_image_prompt_map()
IMAGE_PROMPT_TO_MAIN: Dict[str, str] = {prompt: main for main, prompt in MAIN_IMAGE_PROMPTS.items()}


def _hardware_leaf_rules() -> Tuple[NormalizationRule, ...]:
    hardware_root = next((root for root in CATEGORY_TREE if root.get("slug") == HARDWARE_SLUG), None)
    if not hardware_root:
        return tuple()

    rules: List[NormalizationRule] = []
    stack = list(hardware_root.get("children") or [])
    while stack:
        node = stack.pop()
        children = node.get("children") or []
        if children:
            stack.extend(children)
            continue
        slug = node.get("slug") or node["name"]
        keywords = {node["name"].lower()}
        if isinstance(slug, str):
            keywords.add(slug.replace("-", " "))
        rules.append(
            NormalizationRule(
                tuple(keywords),
                HARDWARE_MAIN,
                safe_path_from_slugs(HARDWARE_SLUG, slug),
            )
        )
    return tuple(rules)


MANUAL_NORMALIZATION_RULES: Tuple[NormalizationRule, ...] = (
    NormalizationRule(
        ("proyector", "projector", "powerlite", "viewsonic"),
        AUDIO_VIDEO_MAIN,
        safe_path_from_slugs(AUDIO_VIDEO_SLUG, "proyectores"),
    ),
    NormalizationRule(
        ("router gamer", "gaming router"),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "routers-gamer"),
    ),
    NormalizationRule(
        ("router",),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "router"),
    ),
    NormalizationRule(
        ("switch",),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "switches"),
    ),
    NormalizationRule(
        ("access point", "punto de acceso", "ap "),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "access-points"),
    ),
    NormalizationRule(
        ("firewall",),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "firewall"),
    ),
    NormalizationRule(
        ("modem", "módem"),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "modems"),
    ),
    NormalizationRule(
        ("monitor gamer", "monitor gaming"),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "monitores-gamer"),
    ),
    NormalizationRule(
        ("monitor", "pantalla"),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "monitores-desktop"),
    ),
    NormalizationRule(
        ("monitores portátiles", "monitor portátil", "monitor portatil"),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "monitores-portatiles"),
    ),
    NormalizationRule(
        ("impresora", "printer"),
        PRINT_MAIN,
        safe_path_from_slugs(PRINT_SLUG, "impresoras"),
    ),
    NormalizationRule(
        ("cartucho", "tóner", "toner", "ink"),
        PRINT_MAIN,
        safe_path_from_slugs(PRINT_SLUG, "toner"),
    ),
    NormalizationRule(
        (
            "ssd externo",
            "ssd externa",
            "ssd externos",
            "ssd externas",
            "external ssd",
            "portable ssd",
            "unidad de estado solido externa",
            "unidad de estado sólido externa",
            "disco ssd externo",
        ),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "ssd-externos"),
    ),
    NormalizationRule(
        ("ssd", "m.2", "nvme"),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "ssd"),
    ),
    NormalizationRule(
        ("disco duro externo", "hdd externo"),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "hdd-externos"),
    ),
    NormalizationRule(
        ("disco duro", "hdd"),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "hdd-interno-pc"),
    ),
    NormalizationRule(
        ("gabinete gamer", "case gamer"),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "gabinetes-gamer"),
    ),
    NormalizationRule(
        ("gabinete", "case atx"),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "gabinetes"),
    ),
    NormalizationRule(
        ("fuente", "psu", "power supply"),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "fuentes-poder-pc"),
    ),
    NormalizationRule(
        ("pc gamer", "pc gaming"),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "pcs-gamer"),
    ),
    NormalizationRule(
        ("laptop gamer", "gaming laptop"),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "laptops-gamer"),
    ),
    NormalizationRule(
        ("silla gamer",),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "sillas-gamer"),
    ),
    NormalizationRule(
        ("escritorio gamer",),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "escritorios-gamer"),
    ),
    NormalizationRule(
        ("auriculares", "headset", "diadema", "audifonos", "audífonos"),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "audifonos-gamer-pc-gaming"),
    ),
    NormalizationRule(
        ("mouse gamer", "gaming mouse"),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "mouse-gamer"),
    ),
    NormalizationRule(
        ("mousepad", "mouse pad"),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "mousepad-gamer"),
    ),
    NormalizationRule(
        ("teclado gamer", "keyboard gamer"),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "kit-gamer-teclado-mouse"),
    ),
    NormalizationRule(
        ("kit teclado", "kit teclado y mouse"),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "kits-teclado-mouse"),
    ),
    NormalizationRule(
        ("teclado",),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "teclados"),
    ),
    NormalizationRule(
        ("mouse",),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "mouse"),
    ),
    NormalizationRule(
        ("procesador", "cpu"),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "procesadores"),
    ),
    NormalizationRule(
        ("tarjeta madre", "motherboard", "mobo"),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "tarjetas-madre"),
    ),
    NormalizationRule(
        ("tarjeta de video", "tarjeta de vídeo", "gpu", "gráfica", "grafica"),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "tarjetas-de-video"),
    ),
    NormalizationRule(
        ("watercooling", "enfriamiento liquido", "enfriamiento líquido"),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "enfriamiento-liquido"),
    ),
    NormalizationRule(
        ("ventilador", "fan case"),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "ventiladores"),
    ),
    NormalizationRule(
        ("disipador", "cooler cpu"),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "disipadores-cpu"),
    ),
    NormalizationRule(
        ("pasta termica", "pasta térmica"),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "pasta-termica"),
    ),
    NormalizationRule(
        ("ram laptop", "memoria ram laptop"),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "ram-laptop"),
    ),
    NormalizationRule(
        ("ram servidor", "ram servidor", "memoria ecc"),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "ram-servidores"),
    ),
    NormalizationRule(
        ("ram", "memoria ram"),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "ram-pc"),
    ),
    NormalizationRule(
        ("memoria usb", "memorias usb", "usb flash", "flash drive", "pendrive"),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "memorias-usb"),
    ),
    NormalizationRule(
        ("stream deck",),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "stream-decks"),
    ),
    NormalizationRule(
        ("tablet grafica", "tablet gráfica"),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "tablets-graficas"),
    ),
    NormalizationRule(
        ("gamepad", "control de juego", "joystick"),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "controles-juego-pc"),
    ),
    NormalizationRule(
        ("volante", "racing wheel"),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "volantes-simulador"),
    ),
    NormalizationRule(
        ("realidad virtual", "vr headset"),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "lentes-realidad-virtual"),
    ),
    NormalizationRule(
        ("simulador", "asiento simulador"),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "asientos-simuladores"),
    ),
    NormalizationRule(
        ("adaptador hdmi", "adaptador displayport", "display port"),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "adaptadores-video-hdmi"),
    ),
    NormalizationRule(
        ("adaptador audio",),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "adaptadores-audio"),
    ),
    NormalizationRule(
        ("cable hdmi",),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "cables-audio-video-hdmi"),
    ),
    NormalizationRule(
        ("cable displayport", "cable display port"),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "cables-audio-video-displayport"),
    ),
    NormalizationRule(
        ("cable ethernet", "cable red", "patch cord"),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "cables-patch"),
    ),
    NormalizationRule(
        ("cable usb",),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "cables-pc-usb"),
    ),
    NormalizationRule(
        ("bobina",),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "bobinas"),
    ),
    NormalizationRule(
        ("cable coaxial",),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "cables-coaxiales"),
    ),
    NormalizationRule(
        ("cable fibra", "cable fibra optica", "fibra óptica"),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "cables-fibra-optica"),
    ),
    NormalizationRule(
        ("quemador dvd", "lector dvd", "dvd writer"),
        HARDWARE_MAIN,
        safe_path_from_slugs(HARDWARE_SLUG, "quemadores-dvd"),
    ),
)

NORMALIZATION_RULES: Tuple[NormalizationRule, ...] = MANUAL_NORMALIZATION_RULES + _hardware_leaf_rules()


def _strip_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def _tokenize(value: str) -> set[str]:
    normalized = _strip_accents(value).lower()
    tokens = re.findall(r"[a-z0-9]+", normalized)
    out = set()
    for token in tokens:
        if len(token) < 3:
            continue
        if token.isdigit():
            continue
        if token in TOKEN_STOPWORDS:
            continue
        out.add(token)
    return out


def _leaf_from_path(path: str | None) -> str:
    if not path:
        return ""
    return str(path).split(" > ")[-1].strip()


def _lexical_overlap_score(text: str, path_label: str | None) -> float:
    leaf = _leaf_from_path(path_label)
    if not leaf:
        return 0.0
    text_tokens = _tokenize(text)
    leaf_tokens = _tokenize(leaf)
    if not text_tokens or not leaf_tokens:
        return 0.0
    overlap = text_tokens.intersection(leaf_tokens)
    return len(overlap) / len(leaf_tokens)


def _ranked_labels(result: Dict) -> List[tuple[str, float]]:
    labels = result.get("labels") or []
    scores = result.get("scores") or []
    ranked: List[tuple[str, float]] = []
    for index, label in enumerate(labels):
        try:
            score = float(scores[index])
        except (IndexError, TypeError, ValueError):
            continue
        ranked.append((str(label), score))
    return ranked


def _ranked_image_labels(result: Any) -> List[tuple[str, float]]:
    if not isinstance(result, list):
        return []
    best_by_main: Dict[str, float] = {}
    for item in result:
        if not isinstance(item, dict):
            continue
        raw_label = str(item.get("label", "")).strip()
        main_label = IMAGE_PROMPT_TO_MAIN.get(raw_label, raw_label)
        if main_label not in MAIN_CATEGORIES:
            continue
        try:
            score = float(item.get("score", 0.0))
        except (TypeError, ValueError):
            continue
        prev = best_by_main.get(main_label, 0.0)
        if score > prev:
            best_by_main[main_label] = score
    return sorted(best_by_main.items(), key=lambda it: it[1], reverse=True)


def _main_scores_from_image(image: Image.Image | None) -> List[tuple[str, float]]:
    if image is None:
        return []
    image_classifier = get_image_pipeline()
    if image_classifier is None:
        return []
    prompts = [MAIN_IMAGE_PROMPTS[main] for main in MAIN_CATEGORIES]
    try:
        image_result = image_classifier(image, candidate_labels=prompts)
    except Exception:
        logger.warning("Falló la clasificación visual; se continúa con texto.", exc_info=True)
        return []
    ranked = _ranked_image_labels(image_result)
    if not ranked:
        return []
    if ranked[0][1] < MIN_IMAGE_CONFIDENCE_TO_BLEND:
        return []
    return ranked


def _blend_main_rankings(
    text_ranked: List[tuple[str, float]],
    image_ranked: List[tuple[str, float]],
) -> List[tuple[str, float]]:
    if not text_ranked:
        return []
    if not image_ranked:
        return text_ranked

    text_scores = {label: score for label, score in text_ranked}
    image_scores = {label: score for label, score in image_ranked}
    blended: List[tuple[str, float]] = []
    for label in MAIN_CATEGORIES:
        score = (TEXT_MAIN_BLEND_WEIGHT * text_scores.get(label, 0.0)) + (
            IMAGE_MAIN_BLEND_WEIGHT * image_scores.get(label, 0.0)
        )
        blended.append((label, score))
    blended.sort(key=lambda it: it[1], reverse=True)
    return blended


def _select_main_candidates(main_ranked: List[tuple[str, float]]) -> List[tuple[str, float]]:
    if not main_ranked:
        return []
    top_score = main_ranked[0][1]
    if top_score >= MAIN_HIGH_CONFIDENCE:
        return [main_ranked[0]]
    min_allowed = max(MAIN_THRESHOLD, top_score - MAIN_SCORE_MARGIN)
    candidates: List[tuple[str, float]] = []
    for label, score in main_ranked:
        if len(candidates) >= MAIN_CANDIDATE_LIMIT:
            break
        if score >= min_allowed:
            candidates.append((label, score))
    if not candidates:
        candidates.append(main_ranked[0])
    return candidates


def _combined_score(main_score: float, sub_score: float | None, lexical_score: float) -> float:
    effective_sub = sub_score if sub_score is not None else 0.0
    return (
        (COMBINED_MAIN_WEIGHT * main_score)
        + (COMBINED_SUB_WEIGHT * effective_sub)
        + (COMBINED_LEXICAL_WEIGHT * lexical_score)
    )


def _best_sub_for_main(classifier, text: str, main_label: str, main_score: float) -> tuple[str | None, float | None]:
    sub_candidates = SUBCATEGORIES.get(main_label) or []
    if not sub_candidates:
        return None, None

    sub_result = classifier(
        text,
        sub_candidates,
        multi_label=True,
        hypothesis_template=HYPOTHESIS_TEMPLATE,
    )
    ranked_sub = _ranked_labels(sub_result)
    if not ranked_sub:
        fallback_sub = GENERIC_SUBCATEGORY_BY_MAIN.get(main_label) or (sub_candidates[0] if sub_candidates else None)
        return fallback_sub, None

    best_sub_label: str | None = None
    best_sub_score: float | None = None
    best_score = -1.0
    for sub_label, sub_score in ranked_sub[:SUB_CANDIDATE_LIMIT]:
        lexical = _lexical_overlap_score(text, sub_label)
        combined = _combined_score(main_score, sub_score, lexical)
        if combined > best_score:
            best_score = combined
            best_sub_label = sub_label
            best_sub_score = sub_score

    if not best_sub_label or (best_sub_score is not None and best_sub_score < SUB_THRESHOLD):
        fallback_sub = GENERIC_SUBCATEGORY_BY_MAIN.get(main_label) or (sub_candidates[0] if sub_candidates else None)
        return fallback_sub, best_sub_score

    return best_sub_label, best_sub_score

def _normalize_labels(
    text: str,
    main_label: str,
    sub_label: str | None,
    main_score: float,
    sub_score: float | None,
) -> ClassificationResult:
    for rule in NORMALIZATION_RULES:
        if rule.matches(text):
            resolved_main = rule.resolve_main(main_label)
            resolved_sub = rule.resolve_sub(resolved_main)
            return ClassificationResult(
                main=resolved_main,
                sub=resolved_sub,
                main_score=max(main_score, NORMALIZATION_CONFIDENCE),
                sub_score=max(sub_score or 0.0, NORMALIZATION_CONFIDENCE) if resolved_sub else sub_score,
            )
    return ClassificationResult(
        main=main_label,
        sub=sub_label,
        main_score=main_score,
        sub_score=sub_score,
    )


def _build_category_prompt() -> str:
    """Construye una lista compacta de categorías para el prompt de OpenAI."""
    lines = []
    for main in MAIN_CATEGORIES:
        subs = SUBCATEGORIES.get(main, [])
        sub_names = [s.split(" > ")[-1] for s in subs[:20]]
        lines.append(f"- {main}: {', '.join(sub_names)}")
    return "\n".join(lines)


def _build_full_category_prompt() -> str:
    """Construye el árbol completo de categorías con rutas exactas para LLMs."""
    lines = []
    for main in MAIN_CATEGORIES:
        lines.append(f"\n{main}:")
        for path in SUBCATEGORIES.get(main, []):
            lines.append(f"  - {path}")
    return "\n".join(lines)


_CATEGORY_PROMPT_CACHE: str | None = None
_FULL_CATEGORY_PROMPT_CACHE: str | None = None


def _classify_with_anthropic(text: str) -> ClassificationResult:
    """Clasifica usando Claude Haiku. Más preciso que BERT."""
    global _FULL_CATEGORY_PROMPT_CACHE
    if _FULL_CATEGORY_PROMPT_CACHE is None:
        _FULL_CATEGORY_PROMPT_CACHE = _build_full_category_prompt()

    try:
        import anthropic
    except ImportError:
        raise ImportError("Instala 'anthropic': pip install anthropic")

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    main_list = "\n".join(f"- {m}" for m in MAIN_CATEGORIES)

    system_prompt = (
        "Eres un clasificador experto de productos de tecnología para una tienda en México. "
        "Tu tarea es asignar la categoría principal y subcategoría MÁS ESPECÍFICA posible. "
        "DEBES usar los nombres EXACTAMENTE como aparecen en las listas, respetando tildes, mayúsculas y paréntesis. "
        'Responde ÚNICAMENTE con JSON válido: {"main": "<nombre exacto>", "sub": "<ruta exacta completa>"}'
    )

    user_prompt = (
        f"Producto: {text[:600]}\n\n"
        f"CATEGORÍAS PRINCIPALES (copia el nombre EXACTO):\n{main_list}\n\n"
        f"ÁRBOL COMPLETO DE SUBCATEGORÍAS (usa la ruta completa 'Principal > Sub > Hoja'):\n{_FULL_CATEGORY_PROMPT_CACHE}\n\n"
        "Elige la categoría y subcategoría más específica y apropiada. "
        "Responde solo con JSON."
    )

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=150,
        messages=[{"role": "user", "content": f"{system_prompt}\n\n{user_prompt}"}],
    )

    raw = message.content[0].text.strip()
    # Extraer JSON si viene con texto adicional
    import re as _re
    json_match = _re.search(r'\{[^}]+\}', raw, _re.DOTALL)
    raw = json_match.group(0) if json_match else raw
    data = json.loads(raw)

    main_label = data.get("main", "").strip()
    sub_leaf = data.get("sub", "").strip()

    if main_label not in MAIN_CATEGORIES:
        logger.warning("Anthropic devolvió main desconocido '%s', usando fallback.", main_label)
        main_label = MAIN_CATEGORIES[0]

    sub_label = safe_path(main_label, sub_leaf) if sub_leaf else GENERIC_SUBCATEGORY_BY_MAIN.get(main_label)

    return ClassificationResult(main=main_label, sub=sub_label, main_score=0.97, sub_score=0.95)


def _classify_with_openai(text: str) -> ClassificationResult:
    """Clasifica usando OpenAI gpt-4o-mini. Más rápido y barato que BERT en CPU."""
    global _CATEGORY_PROMPT_CACHE
    if _CATEGORY_PROMPT_CACHE is None:
        _CATEGORY_PROMPT_CACHE = _build_category_prompt()

    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("Instala 'openai': pip install openai")

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    main_list = "\n".join(f"- {m}" for m in MAIN_CATEGORIES)

    system_prompt = (
        "Eres un clasificador de productos para una tienda de tecnología en México. "
        "DEBES usar los nombres de categoría EXACTAMENTE como aparecen en la lista, "
        "sin cambiar tildes, mayúsculas ni paréntesis. "
        "Responde SOLO con JSON válido: "
        '{"main": "<nombre exacto de la lista>", "sub": "<subcategoría exacta>"}'
    )

    user_prompt = (
        f"Producto: {text[:500]}\n\n"
        f"Categorías principales (copia el nombre EXACTO):\n{main_list}\n\n"
        f"Subcategorías por categoría principal:\n{_CATEGORY_PROMPT_CACHE}\n\n"
        "Responde con JSON usando los nombres exactos de las listas."
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0,
        max_tokens=100,
    )

    raw = response.choices[0].message.content or "{}"
    data = json.loads(raw)

    main_label = data.get("main", "").strip()
    sub_leaf = data.get("sub", "").strip()

    # Validar que el main existe, si no usar el primero
    if main_label not in MAIN_CATEGORIES:
        logger.warning("OpenAI devolvió main desconocido '%s', usando fallback.", main_label)
        main_label = MAIN_CATEGORIES[0]

    # Buscar la ruta completa para la subcategoría
    sub_label = safe_path(main_label, sub_leaf) if sub_leaf else GENERIC_SUBCATEGORY_BY_MAIN.get(main_label)

    return _normalize_labels(text, main_label, sub_label, 0.95, 0.90)


def classify_text(text: str, image: Image.Image | None = None) -> ClassificationResult:
    """Clasifica un texto en categorías y subcategorías.

    Prioridad: Anthropic Claude > OpenAI > pipeline local BERT.
    """
    if os.environ.get("ANTHROPIC_API_KEY"):
        try:
            return _classify_with_anthropic(text)
        except Exception as exc:
            logger.warning("Anthropic falló (%s), intentando OpenAI.", exc)

    if os.environ.get("OPENAI_API_KEY"):
        try:
            return _classify_with_openai(text)
        except Exception as exc:
            logger.warning("OpenAI falló (%s), cayendo a pipeline local.", exc)

    classifier = get_pipeline()
    main_result = classifier(
        text,
        MAIN_CATEGORIES,
        multi_label=True,
        hypothesis_template=HYPOTHESIS_TEMPLATE,
    )
    main_ranked_text = _ranked_labels(main_result)
    main_ranked_image = _main_scores_from_image(image)
    main_ranked = _blend_main_rankings(main_ranked_text, main_ranked_image)
    if not main_ranked:
        fallback_main = MAIN_CATEGORIES[0]
        fallback_sub = GENERIC_SUBCATEGORY_BY_MAIN.get(fallback_main)
        return _normalize_labels(text, fallback_main, fallback_sub, 0.0, None)

    best_result: ClassificationResult | None = None
    best_score = -1.0
    for main_label, main_score in _select_main_candidates(main_ranked):
        sub_label, sub_score = _best_sub_for_main(classifier, text, main_label, main_score)
        lexical = _lexical_overlap_score(text, sub_label)
        combined = _combined_score(main_score, sub_score, lexical)
        candidate = ClassificationResult(
            main=main_label,
            sub=sub_label,
            main_score=main_score,
            sub_score=sub_score,
        )
        if combined > best_score:
            best_result = candidate
            best_score = combined

    if best_result is None:
        main_label, main_score = main_ranked[0]
        best_result = ClassificationResult(
            main=main_label,
            sub=GENERIC_SUBCATEGORY_BY_MAIN.get(main_label),
            main_score=main_score,
            sub_score=None,
        )

    return _normalize_labels(
        text,
        best_result.main,
        best_result.sub,
        best_result.main_score,
        best_result.sub_score,
    )


def build_text_from_product(product) -> str:
    parts: List[str] = []
    for attr in ("nombre", "descripcion_corta", "descripcion_larga", "sku"):
        value = getattr(product, attr, None)
        if value:
            parts.append(str(value))
    return " \n".join(parts)


def _read_image_field(image_field) -> Image.Image | None:
    if not image_field or not getattr(image_field, "name", None):
        return None
    try:
        image_field.open("rb")
        img = Image.open(image_field)
        img = ImageOps.exif_transpose(img).convert("RGB")
        return img.copy()
    except Exception:
        logger.warning("No se pudo abrir la imagen del producto para clasificación visual.", exc_info=True)
        return None
    finally:
        try:
            image_field.close()
        except Exception:
            pass


def load_product_image(product) -> Image.Image | None:
    image_sources = [
        getattr(product, "miniatura", None),
        getattr(product, "imagen_principal", None),
    ]

    galeria_manager = getattr(product, "galeria", None)
    if galeria_manager is not None:
        try:
            first_gallery = galeria_manager.first()
            if first_gallery is not None:
                image_sources.append(getattr(first_gallery, "imagen", None))
        except Exception:
            logger.debug("No se pudo leer la galería para clasificación visual.", exc_info=True)

    for image_field in image_sources:
        loaded = _read_image_field(image_field)
        if loaded is not None:
            return loaded
    return None


def classify_product(product) -> ClassificationResult:
    text = build_text_from_product(product)
    if not text:
        text = product.nombre or f"Producto {product.pk}"
    image = load_product_image(product)
    return classify_text(text, image=image)

