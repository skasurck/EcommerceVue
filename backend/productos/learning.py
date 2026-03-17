import math
import threading
import time
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Dict, Iterable, List

from django.db.models import Count, Max

from .models import Categoria, ProductClassificationFeedback

MAX_TRAINING_SAMPLES = 12000
MIN_MODEL_SAMPLES = 20
MIN_LABEL_SAMPLES = 2
MIN_TOP_SCORE = 0.10
MIN_CONFIDENCE = 0.58
MODEL_CACHE_SECONDS = 120
SUPPORT_SATURATION = 12

_cache_lock = threading.Lock()
_cached_model = None
_cached_key = None
_cached_at = 0.0


@dataclass
class FeedbackPrediction:
    main: str
    sub: str
    score: float
    confidence: float
    support: int


@dataclass
class FeedbackModel:
    idf: Dict[str, float]
    label_weights: Dict[str, Dict[str, float]]
    label_norms: Dict[str, float]
    label_support: Dict[str, int]
    main_by_label: Dict[str, str]
    total_samples: int


def _strip_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def _tokenize(text: str) -> List[str]:
    cleaned = _strip_accents(text).lower()
    tokens: List[str] = []
    current = []
    for ch in cleaned:
        if ch.isalnum():
            current.append(ch)
        else:
            if current:
                token = "".join(current)
                if len(token) >= 3 and not token.isdigit():
                    tokens.append(token)
                current = []
    if current:
        token = "".join(current)
        if len(token) >= 3 and not token.isdigit():
            tokens.append(token)
    return tokens


def build_text_from_product_fields(product) -> str:
    parts = []
    for attr in ("nombre", "descripcion_corta", "descripcion_larga", "sku"):
        value = getattr(product, attr, None)
        if value:
            parts.append(str(value))
    return " \n".join(parts)


def _category_depth(category: Categoria) -> int:
    depth = 0
    current = category
    seen = set()
    while current and current.id not in seen:
        seen.add(current.id)
        depth += 1
        current = current.parent
    return depth


def _category_path(category: Categoria) -> str:
    parts = []
    current = category
    seen = set()
    while current and current.id not in seen:
        seen.add(current.id)
        parts.append(current.nombre)
        current = current.parent
    return " > ".join(reversed(parts))


def _select_target_category(category_ids: Iterable[int]) -> Categoria | None:
    ordered_ids = []
    for raw_id in category_ids:
        try:
            normalized = int(raw_id)
        except (TypeError, ValueError):
            continue
        if normalized not in ordered_ids:
            ordered_ids.append(normalized)

    if not ordered_ids:
        return None

    categories = Categoria.objects.select_related(
        "parent", "parent__parent", "parent__parent__parent"
    ).filter(id__in=ordered_ids)
    by_id = {cat.id: cat for cat in categories}

    best = None
    best_depth = -1
    for category_id in ordered_ids:
        category = by_id.get(category_id)
        if not category:
            continue
        depth = _category_depth(category)
        if depth > best_depth:
            best = category
            best_depth = depth
    return best


def record_manual_feedback(product, category_ids, source=ProductClassificationFeedback.SOURCE_MANUAL_SINGLE) -> bool:
    target_category = _select_target_category(category_ids)
    if target_category is None:
        return False

    target_sub = _category_path(target_category)
    if not target_sub:
        return False
    target_main = target_sub.split(" > ")[0]

    text = build_text_from_product_fields(product)
    if not text:
        text = product.nombre or ""
    text = text.strip()
    if not text:
        return False

    latest = (
        ProductClassificationFeedback.objects.filter(producto=product)
        .only("target_sub", "input_text")
        .first()
    )
    if latest and latest.target_sub == target_sub and latest.input_text == text:
        return False

    ProductClassificationFeedback.objects.create(
        producto=product,
        input_text=text,
        target_main=target_main,
        target_sub=target_sub,
        source=source,
    )
    return True


def _training_rows():
    rows = (
        ProductClassificationFeedback.objects.only("input_text", "target_main", "target_sub")
        .order_by("-id")[:MAX_TRAINING_SAMPLES]
    )
    return list(rows)


def _build_model(rows) -> FeedbackModel | None:
    if len(rows) < MIN_MODEL_SAMPLES:
        return None

    label_tf = defaultdict(Counter)
    label_support = Counter()
    main_by_label: Dict[str, str] = {}
    document_frequency = Counter()
    total_docs = 0

    for row in rows:
        label = (row.target_sub or "").strip()
        if not label:
            continue
        tokens = _tokenize(row.input_text or "")
        if not tokens:
            continue

        counts = Counter(tokens)
        label_tf[label].update(counts)
        label_support[label] += 1
        main_by_label[label] = (row.target_main or label.split(" > ")[0]).strip()
        total_docs += 1
        for token in counts.keys():
            document_frequency[token] += 1

    if total_docs < MIN_MODEL_SAMPLES:
        return None

    valid_labels = {label for label, count in label_support.items() if count >= MIN_LABEL_SAMPLES}
    if not valid_labels:
        return None

    idf = {
        token: math.log((1.0 + total_docs) / (1.0 + df)) + 1.0
        for token, df in document_frequency.items()
    }

    label_weights: Dict[str, Dict[str, float]] = {}
    label_norms: Dict[str, float] = {}
    normalized_support: Dict[str, int] = {}
    normalized_main: Dict[str, str] = {}

    for label in valid_labels:
        counts = label_tf[label]
        total_terms = sum(counts.values())
        if total_terms <= 0:
            continue
        weights: Dict[str, float] = {}
        for token, count in counts.items():
            token_idf = idf.get(token)
            if token_idf is None:
                continue
            weights[token] = (count / total_terms) * token_idf
        if not weights:
            continue
        norm = math.sqrt(sum(value * value for value in weights.values()))
        if norm <= 0:
            continue
        label_weights[label] = weights
        label_norms[label] = norm
        normalized_support[label] = int(label_support[label])
        normalized_main[label] = main_by_label.get(label, label.split(" > ")[0])

    if not label_weights:
        return None

    return FeedbackModel(
        idf=idf,
        label_weights=label_weights,
        label_norms=label_norms,
        label_support=normalized_support,
        main_by_label=normalized_main,
        total_samples=total_docs,
    )


def _feedback_cache_key():
    stats = ProductClassificationFeedback.objects.aggregate(total=Count("id"), max_id=Max("id"))
    return int(stats.get("total") or 0), int(stats.get("max_id") or 0)


def get_feedback_model(force_refresh=False) -> FeedbackModel | None:
    global _cached_model, _cached_key, _cached_at
    key = _feedback_cache_key()
    now = time.time()
    with _cache_lock:
        if (
            not force_refresh
            and _cached_model is not None
            and _cached_key == key
            and (now - _cached_at) < MODEL_CACHE_SECONDS
        ):
            return _cached_model

        model = _build_model(_training_rows())
        _cached_model = model
        _cached_key = key
        _cached_at = now
        return _cached_model


def predict_with_feedback(text: str, model: FeedbackModel | None = None) -> FeedbackPrediction | None:
    model = model or get_feedback_model()
    if model is None:
        return None

    query_tokens = _tokenize(text or "")
    if not query_tokens:
        return None

    query_counts = Counter(query_tokens)
    total_query_terms = sum(query_counts.values())
    if total_query_terms <= 0:
        return None

    query_weights = {
        token: (count / total_query_terms) * model.idf.get(token, 0.0)
        for token, count in query_counts.items()
        if model.idf.get(token, 0.0) > 0
    }
    if not query_weights:
        return None

    query_norm = math.sqrt(sum(value * value for value in query_weights.values()))
    if query_norm <= 0:
        return None

    scored = []
    for label, label_vector in model.label_weights.items():
        dot = 0.0
        for token, query_weight in query_weights.items():
            label_weight = label_vector.get(token)
            if label_weight:
                dot += query_weight * label_weight
        if dot <= 0:
            continue

        base_score = dot / (query_norm * model.label_norms[label] + 1e-9)
        support = model.label_support.get(label, 0)
        support_boost = 0.75 + 0.25 * min(1.0, support / SUPPORT_SATURATION)
        score = base_score * support_boost
        scored.append((label, score, support))

    if not scored:
        return None

    scored.sort(key=lambda item: item[1], reverse=True)
    top_label, top_score, top_support = scored[0]
    second_score = scored[1][1] if len(scored) > 1 else 0.0

    if top_score < MIN_TOP_SCORE:
        return None

    confidence = top_score / (top_score + second_score + 1e-9)
    if confidence < MIN_CONFIDENCE:
        return None

    return FeedbackPrediction(
        main=model.main_by_label.get(top_label, top_label.split(" > ")[0]),
        sub=top_label,
        score=top_score,
        confidence=confidence,
        support=top_support,
    )
