import logging
from dataclasses import dataclass
from importlib import import_module
from typing import Dict, List, Optional, Sequence, Tuple, TypedDict

from django.core.exceptions import ImproperlyConfigured
from .models import Categoria
from .category_tree import CATEGORY_TREE

logger = logging.getLogger(__name__)

HYPOTHESIS_TEMPLATE = "Este texto es sobre {}."
MODEL_NAME = "Recognai/bert-base-spanish-wwm-cased-xnli"

# Umbrales para el nuevo enfoque de 2 pasos
MAIN_CATEGORY_THRESHOLD = 0.50
SUB_CATEGORY_THRESHOLD = 0.70
NORMALIZATION_CONFIDENCE = 0.90

# --- Estructuras de Datos y Mapas de Categorías ---

class CategoryNode(TypedDict):
    id: Optional[int]
    nombre: str
    subcategorias: List['CategoryNode']

def _build_db_path_map() -> Dict[str, int]:
    """Crea un mapa de ruta completa (por nombre) hacia ID en la base de datos."""
    all_cats = Categoria.objects.all().only("id", "nombre", "parent_id")
    cat_by_id = {cat.id: cat for cat in all_cats}
    path_cache: Dict[int, str] = {}

    def build_path(cat_id: int) -> str:
        if cat_id in path_cache:
            return path_cache[cat_id]
        cat = cat_by_id.get(cat_id)
        if not cat:
            return ""
        parts: List[str] = []
        current = cat
        while current:
            parts.insert(0, current.nombre)
            current = cat_by_id.get(current.parent_id) if current.parent_id else None
        path = " > ".join(parts)
        path_cache[cat_id] = path
        return path

    path_map: Dict[str, int] = {}
    for cat_id in cat_by_id:
        path = build_path(cat_id)
        if path:
            path_map[path] = cat_id
    return path_map

def _get_category_tree_from_master() -> List[CategoryNode]:
    """Construye un árbol usando el CATEGORY_TREE maestro y resuelve IDs desde la DB."""
    path_map = _build_db_path_map()
    missing_paths: List[str] = []

    def build_nodes(nodes, trail: List[str]) -> List[CategoryNode]:
        result: List[CategoryNode] = []
        for node in nodes:
            name = node["name"]
            path = " > ".join(trail + [name])
            cat_id = path_map.get(path)
            if cat_id is None:
                missing_paths.append(path)
            entry: CategoryNode = {
                "id": cat_id,
                "nombre": name,
                "subcategorias": build_nodes(node.get("children") or [], trail + [name]),
            }
            result.append(entry)
        return result

    tree = build_nodes(CATEGORY_TREE, [])
    if missing_paths:
        logger.warning(
            "Categorias del arbol maestro no encontradas en DB (primeras %s): %s",
            min(10, len(missing_paths)),
            ", ".join(missing_paths[:10]),
        )
    return tree

def _build_category_maps_from_db(tree: List[CategoryNode]) -> Tuple[List[str], Dict[str, List[str]], Dict[str, int]]:
    """Genera mapas para la clasificación a partir del árbol de categorías."""
    main_categories: List[str] = []
    subcategories_by_main: Dict[str, List[str]] = {}
    main_category_ids: Dict[str, int] = {}

    for root_node in tree:
        main_label = root_node['nombre']
        main_categories.append(main_label)
        if root_node.get("id") is not None:
            main_category_ids[main_label] = root_node["id"]
        
        leaf_paths: List[str] = []
        
        def find_leaves(node: CategoryNode, trail: List[str]):
            current_path = " > ".join(trail + [node['nombre']])
            if not node['subcategorias']:
                leaf_paths.append(current_path)
            else:
                for child in node['subcategorias']:
                    find_leaves(child, trail + [node['nombre']])
        
        find_leaves(root_node, [])
        subcategories_by_main[main_label] = leaf_paths if leaf_paths else [main_label]

    return main_categories, subcategories_by_main, main_category_ids

def _build_leaf_map(tree: List[CategoryNode]) -> Dict[str, int]:
    """Crea un mapa de 'Ruta completa > ID' para todas las categorías hoja."""
    leaf_map: Dict[str, int] = {}

    def find_leaves(node: CategoryNode, trail: List[str]):
        current_path = " > ".join(trail + [node['nombre']])
        if not node['subcategorias']:
            if node.get("id") is not None:
                leaf_map[current_path] = node["id"]
        else:
            for child in node['subcategorias']:
                find_leaves(child, trail + [node['nombre']])

    for root_node in tree:
        find_leaves(root_node, [])
        
    return leaf_map

# -- Carga global de la estructura de categorías --
CATEGORY_TREE_FROM_MASTER = _get_category_tree_from_master()
MAIN_CATEGORIES, SUBCATEGORIES, MAIN_CATEGORY_IDS = _build_category_maps_from_db(CATEGORY_TREE_FROM_MASTER)
LEAF_CATEGORIES_MAP = _build_leaf_map(CATEGORY_TREE_FROM_MASTER)

# --- Lógica del Pipeline y Clasificación ---
_pipeline = None

def get_pipeline():
    global _pipeline
    if _pipeline is None:
        logger.info("Pipeline no está cargado. Iniciando la carga...")
        transformers = import_module("transformers")
        _pipeline = transformers.pipeline("zero-shot-classification", model=MODEL_NAME, device="cpu")
        logger.info("¡Pipeline de Transformers cargado!")
    return _pipeline

@dataclass
class AISuggestion:
    id: int
    score: float

@dataclass
class ClassificationResult:
    suggestions: List[AISuggestion]

# --- Reglas de Normalización (Reintroducidas y Simplificadas) ---
class NormalizationRule:
    def __init__(self, keywords: Sequence[str], category_path: str):
        self.keywords = tuple(k.lower() for k in keywords)
        self.category_id = LEAF_CATEGORIES_MAP.get(category_path)

    def matches(self, text: str) -> bool:
        if not self.category_id:
            return False
        lower_text = text.lower()
        return any(keyword in lower_text for keyword in self.keywords)

# Se define un conjunto de reglas manuales para casos comunes y obvios.
MANUAL_NORMALIZATION_RULES = [
    NormalizationRule(("mouse", "ratón"), "Cómputo (Hardware) > Dispositivos de Entrada > Mouse"),
    NormalizationRule(("mouse gamer",), "Cómputo (Hardware) > PC Gaming > Mouse Gamer"),
    NormalizationRule(("teclado",), "Cómputo (Hardware) > Dispositivos de Entrada > Teclados"),
    NormalizationRule(("teclado gamer",), "Cómputo (Hardware) > PC Gaming > Teclados Gamer"),
    NormalizationRule(("diadema", "headset", "audifonos", "audífonos"), "Audio y Video > Audio > Audífonos"),
    NormalizationRule(("miniprinter", "impresora de tickets"), "Punto de Venta (POS) > Impresoras de Tickets"),
    NormalizationRule(("impresora", "printer"), "Impresión y Copiado > Impresoras y Multifuncionales > Impresoras"),
    NormalizationRule(("cajon de dinero", "cajón de dinero", "cash drawer"), "Punto de Venta (POS) > Cajones de dinero"),
]

def apply_normalization_rules(text: str) -> List[AISuggestion]:
    """Aplica reglas manuales para encontrar categorías obvias."""
    suggestions = []
    for rule in MANUAL_NORMALIZATION_RULES:
        if rule.matches(text):
            suggestions.append(AISuggestion(id=rule.category_id, score=NORMALIZATION_CONFIDENCE))
    return suggestions

def classify_text(text: str) -> ClassificationResult:
    """Clasifica texto usando un enfoque de 2 pasos y reglas manuales."""
    # 1. Aplicar reglas manuales primero
    manual_suggestions = apply_normalization_rules(text)
    if manual_suggestions:
        logger.info(f"Clasificación resuelta por reglas manuales: {manual_suggestions}")
        return ClassificationResult(suggestions=manual_suggestions)

    # 2. Si no hay reglas, proceder con el modelo de IA
    classifier = get_pipeline()
    final_suggestions: Dict[int, float] = {}

    # Paso 1: Clasificar contra las categorías principales
    main_results = classifier(text, MAIN_CATEGORIES, multi_label=True, hypothesis_template=HYPOTHESIS_TEMPLATE)
    
    winning_mains = []
    for label, score in zip(main_results["labels"], main_results["scores"]):
        if score >= MAIN_CATEGORY_THRESHOLD:
            winning_mains.append(label)

    logger.info(f"Categorías principales candidatas: {winning_mains}")

    # Paso 2: Para cada principal ganadora, clasificar en sus subcategorías
    for main_label in winning_mains:
        sub_candidates = SUBCATEGORIES.get(main_label, [])
        if not sub_candidates:
            continue

        sub_results = classifier(text, sub_candidates, multi_label=True, hypothesis_template=HYPOTHESIS_TEMPLATE)
        
        for label, score in zip(sub_results["labels"], sub_results["scores"]):
            if score >= SUB_CATEGORY_THRESHOLD:
                cat_id = LEAF_CATEGORIES_MAP.get(label)
                if cat_id:
                    # Si ya existe, guardar el score más alto
                    final_suggestions[cat_id] = max(score, final_suggestions.get(cat_id, 0.0))

    # Convertir el diccionario a una lista de objetos AISuggestion
    sorted_suggestions = sorted(final_suggestions.items(), key=lambda item: item[1], reverse=True)
    
    result = ClassificationResult(suggestions=[AISuggestion(id=cat_id, score=score) for cat_id, score in sorted_suggestions])
    logger.info(f"Sugerencias de IA finales: {result.suggestions}")
    
    return result

def build_text_from_product(product) -> str:
    """Construye un texto único a partir de los campos de un producto."""
    parts: List[str] = []
    for attr in ("nombre", "descripcion_corta", "descripcion_larga", "sku"):
        value = getattr(product, attr, None)
        if value:
            parts.append(str(value))
    return " \n".join(parts)

