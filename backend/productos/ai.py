import logging
import threading
from dataclasses import dataclass
from importlib import import_module
from typing import Dict, List, Sequence, Tuple

from django.core.exceptions import ImproperlyConfigured

from productos.category_tree import CATEGORY_TREE

# Configurar un logger específico para este módulo
logger = logging.getLogger(__name__)

HYPOTHESIS_TEMPLATE = "Este texto es sobre {}."
MODEL_NAME = "Recognai/bert-base-spanish-wwm-cased-xnli"
MAIN_THRESHOLD = 0.40
SUB_THRESHOLD = 0.35
NORMALIZATION_CONFIDENCE = 0.95


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
HARDWARE_MAIN = MAIN_CATEGORY_BY_SLUG.get(HARDWARE_SLUG, "Cómputo (Hardware)")
PRINT_MAIN = MAIN_CATEGORY_BY_SLUG.get(PRINT_SLUG, "Impresión y Copiado")


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
        ("usb", "memoria usb"),
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


def classify_text(text: str) -> ClassificationResult:
    """Clasifica un texto en categorías y subcategorías."""
    classifier = get_pipeline()
    main_result = classifier(
        text,
        MAIN_CATEGORIES,
        multi_label=False,
        hypothesis_template=HYPOTHESIS_TEMPLATE,
    )
    main_label = main_result["labels"][0]
    main_score = float(main_result["scores"][0])
    if main_score < MAIN_THRESHOLD:
        main_label = MAIN_CATEGORIES[0]

    sub_candidates = SUBCATEGORIES.get(main_label) or []
    sub_label = None
    sub_score = None
    if sub_candidates:
        sub_result = classifier(
            text,
            sub_candidates,
            multi_label=False,
            hypothesis_template=HYPOTHESIS_TEMPLATE,
        )
        sub_label = sub_result["labels"][0]
        sub_score = float(sub_result["scores"][0])

    if not sub_label or (sub_score is not None and sub_score < SUB_THRESHOLD):
        fallback_sub = GENERIC_SUBCATEGORY_BY_MAIN.get(main_label)
        if not fallback_sub and sub_candidates:
            fallback_sub = sub_candidates[0]
        sub_label = fallback_sub

    normalized = _normalize_labels(text, main_label, sub_label, main_score, sub_score)
    return normalized


def build_text_from_product(product) -> str:
    parts: List[str] = []
    for attr in ("nombre", "descripcion_corta", "descripcion_larga", "sku"):
        value = getattr(product, attr, None)
        if value:
            parts.append(str(value))
    return " \n".join(parts)


