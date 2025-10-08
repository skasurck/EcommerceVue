"""Herramientas de clasificación automática para productos."""

import threading
from dataclasses import dataclass
from importlib import import_module
from typing import Dict, List, Sequence, Tuple

from django.core.exceptions import ImproperlyConfigured

MAIN_CATEGORIES: List[str] = [
    "Componentes de PC",
    "Computadoras y Laptops",
    "Periféricos",
    "Almacenamiento",
    "Redes y Conectividad",
    "Impresión y Escaneo",
    "Accesorios",
    "Audio y Video",
]

SUBCATEGORIES: Dict[str, List[str]] = {
    "Componentes de PC": [
        "Procesadores (CPU)",
        "Tarjetas de Video (GPU)",
        "Tarjetas Madre (Motherboards)",
        "Memoria RAM",
        "Fuentes de Poder (PSU)",
        "Gabinetes (PC Cases)",
        "Enfriamiento - Disipadores CPU",
        "Enfriamiento - Líquido",
        "Enfriamiento - Ventiladores",
        "Enfriamiento - Pasta Térmica",
    ],
    "Computadoras y Laptops": [
        "Laptops",
        "Escritorio (Pre-armadas)",
        "All-in-One (AIO)",
        "Mini PCs",
    ],
    "Periféricos": [
        "Monitores",
        "Teclados",
        "Mouses (Ratones)",
        "Audífonos / Diademas",
        "Webcams",
        "Micrófonos",
        "Mousepads",
        "Tabletas Digitalizadoras",
    ],
    "Almacenamiento": [
        "SSD Interno (SATA / NVMe M.2)",
        "SSD Externo",
        "HDD Interno",
        "HDD Externo",
        "USB / Tarjetas SD",
        "Cases / Enclosures",
    ],
    "Redes y Conectividad": [
        "Routers",
        "Switches",
        "Adaptadores de Red",
        "Cables de Red",
        "Wi-Fi Mesh / Extensores",
    ],
    "Impresión y Escaneo": [
        "Impresoras",
        "Multifuncionales",
        "Tóner / Tinta",
        "Papel / Etiquetas",
        "Escáneres",
    ],
    "Accesorios": [
        "Cables y Convertidores",
        "Soportes / Sillas",
        "Limpieza y Mantenimiento",
        "Baterías / Cargadores",
        "Mochilas / Fundas",
    ],
    "Audio y Video": [
        "Audífonos",
        "Bocinas",
        "Interfaces / Capturadoras",
        "Micrófonos",
        "Proyectores / Pantallas",
    ],
}

GENERIC_SUBCATEGORY_BY_MAIN: Dict[str, str] = {
    "Accesorios": "Cables y Convertidores",
    "Componentes de PC": "Gabinetes (PC Cases)",
    "Computadoras y Laptops": "Laptops",
    "Periféricos": "Monitores",
    "Almacenamiento": "SSD Interno (SATA / NVMe M.2)",
    "Redes y Conectividad": "Routers",
    "Impresión y Escaneo": "Impresoras",
    "Audio y Video": "Bocinas",
}

HYPOTHESIS_TEMPLATE = "Este texto es sobre {}."
MODEL_NAME = "joeddav/xlm-roberta-large-xnli"
MAIN_THRESHOLD = 0.40
SUB_THRESHOLD = 0.35
NORMALIZATION_CONFIDENCE = 0.95

_pipeline = None
_pipeline_lock = threading.Lock()


def get_pipeline():
    """Carga perezosa del pipeline de zero-shot classification."""
    global _pipeline
    if _pipeline is None:
        with _pipeline_lock:
            if _pipeline is None:
                try:
                    transformers = import_module("transformers")
                except ModuleNotFoundError as exc:
                    raise ImproperlyConfigured(
                        "El paquete 'transformers' es requerido para la clasificación AI. "
                        "Instálalo con 'pip install transformers'."
                    ) from exc

                _pipeline = transformers.pipeline(
                    "zero-shot-classification",
                    model=MODEL_NAME,
                    device_map="auto",
                )
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
        sub: str | Dict[str, str],
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

    def resolve_sub(self, main_label: str) -> str:
        if isinstance(self.sub_targets, dict):
            return self.sub_targets.get(main_label) or next(iter(self.sub_targets.values()))
        return self.sub_targets  # type: ignore[return-value]


NORMALIZATION_RULES: Tuple[NormalizationRule, ...] = (
    NormalizationRule(("router",), "Redes y Conectividad", "Routers"),
    NormalizationRule(("switch",), "Redes y Conectividad", "Switches"),
    NormalizationRule(("monitor",), "Periféricos", "Monitores"),
    NormalizationRule(("impresora", "printer"), "Impresión y Escaneo", "Impresoras"),
    NormalizationRule(("cartucho", "tóner", "toner", "ink"), "Impresión y Escaneo", "Tóner / Tinta"),
    NormalizationRule(
        ("auriculares", "headset", "diadema"),
        ("Periféricos", "Audio y Video"),
        {"Periféricos": "Audífonos / Diademas", "Audio y Video": "Audífonos"},
    ),
    NormalizationRule(("ssd", "m.2", "nvme"), "Almacenamiento", "SSD Interno (SATA / NVMe M.2)"),
    NormalizationRule(("gabinete", "case atx"), "Componentes de PC", "Gabinetes (PC Cases)"),
    NormalizationRule(("fuente", "psu"), "Componentes de PC", "Fuentes de Poder (PSU)"),
    NormalizationRule(
        ("board", "mother", "motherboard"),
        "Componentes de PC",
        "Tarjetas Madre (Motherboards)",
    ),
)


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
                sub_score=max(sub_score or 0.0, NORMALIZATION_CONFIDENCE),
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
        main_label = "Accesorios"

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
