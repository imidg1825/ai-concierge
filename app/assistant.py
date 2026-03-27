from app.state import get_user_product, update_user_product
from app.market import build_market_query
from app.price_search import search_prices
from app.price_analysis import analyze_prices
from app.ad_generator import generate_ad_fallback
from app.text_parser import extract_product_data
from app.category_config import CATEGORY_CONFIG, DEFAULT_QUESTIONS


UNKNOWN_ANSWERS = {
    "не знаю",
    "неизвестно",
    "без бренда",
    "no brand",
    "unknown",
}


OPTIONAL_BRAND_CATEGORIES = {
    "велосипед",
    "диван",
    "стул",
}


def get_missing_fields(product, attributes):
    """
    Возвращает список недостающих полей по конфигу категории.
    Ищет сначала в product, потом в attributes.
    """
    category = product.category

    if not category:
        return ["category"]

    config = CATEGORY_CONFIG.get(category)

    if not config:
        required_fields = ["condition"]
    else:
        required_fields = config.get("required_fields", ["condition"])

    missing = []

    for field in required_fields:
        value = None

        if hasattr(product, field):
            value = getattr(product, field)

        if not value:
            value = attributes.get(field)

        if not value:
            missing.append(field)

    return missing


def get_question(category, field):
    config = CATEGORY_CONFIG.get(category, {})
    questions = config.get("questions", {})
    return questions.get(field, DEFAULT_QUESTIONS.get(field, f"Уточните: {field}"))


def build_collecting_response(
    product, attributes, message, step="collecting", missing_fields=None
):
    return {
        "step": step,
        "message": message,
        "product": {
            "category": product.category,
            "brand": product.brand,
            "condition": product.condition,
            "user_price_rub": int(product.price) if product.price else 0,
            "attributes": attributes,
        },
        "market": {
            "query": "",
            "min_price_rub": 0,
            "max_price_rub": 0,
            "median_price_rub": 0,
            "recommended_price_rub": 0,
        },
        "ad": None,
        "missing_fields": missing_fields or [],
        "status": "waiting_for_details",
    }


def build_completed_response(product, attributes):
    market_query = build_market_query(product, attributes)
    prices = search_prices(market_query)
    analysis = analyze_prices(prices)

    print(f"📊 Анализ рынка: {analysis}")

    ad = generate_ad_fallback(
        {
            "category": product.category,
            "brand": product.brand,
            "condition": product.condition,
            "attributes": attributes,
        },
        {
            "median_price_rub": analysis["median"],
            "recommended_price_rub": analysis["recommended_price"],
        },
    )

    return {
        "step": "completed",
        "message": "Объявление сгенерировано.",
        "product": {
            "category": product.category,
            "brand": product.brand,
            "condition": product.condition,
            "user_price_rub": int(product.price) if product.price else 0,
            "attributes": attributes,
        },
        "market": {
            "query": market_query,
            "min_price_rub": analysis["min"],
            "max_price_rub": analysis["max"],
            "median_price_rub": analysis["median"],
            "recommended_price_rub": analysis["recommended_price"],
        },
        "ad": ad,
        "status": "ad_generated",
    }


def process_message(text: str, user_id: str = "default"):
    text = text.strip()
    text_lower = text.lower()

    parsed = extract_product_data(text)
    product = get_user_product(user_id)

    # --------------------------
    # СПЕЦИАЛЬНЫЕ ОТВЕТЫ "НЕ ЗНАЮ"
    # --------------------------
    if text_lower in UNKNOWN_ANSWERS:
        if (
            product.category
            and product.category in OPTIONAL_BRAND_CATEGORIES
            and not product.brand
        ):
            update_user_product(user_id, "brand", "Неизвестно")
        elif not product.brand:
            update_user_product(user_id, "brand", "Неизвестно")

        product = get_user_product(user_id)

    # --------------------------
    # АВТОЗАПОЛНЕНИЕ ИЗ ТЕКСТА
    # --------------------------
    if product.category is None and parsed["category"] is not None:
        update_user_product(user_id, "category", parsed["category"])

    if product.brand is None and parsed["brand"] is not None:
        update_user_product(user_id, "brand", parsed["brand"])

    if product.condition is None and parsed["condition"] is not None:
        update_user_product(user_id, "condition", parsed["condition"])

    if product.price is None and parsed["price"] is not None:
        update_user_product(user_id, "price", parsed["price"])

    # перечитываем product после обновлений
    product = get_user_product(user_id)

    old_attributes = getattr(product, "attributes", {}) or {}
    new_attributes = parsed.get("attributes", {}) or {}
    attributes = {**old_attributes, **new_attributes}

    update_user_product(user_id, "attributes", attributes)

    # и ещё раз перечитываем, чтобы состояние было консистентным
    product = get_user_product(user_id)

    # --------------------------
    # КАТЕГОРИЯ
    # --------------------------
    if product.category is None:
        return build_collecting_response(
            product,
            attributes,
            "Что вы хотите продать?",
            step="category",
            missing_fields=["category"],
        )

    # --------------------------
    # ОСОБЫЕ ПРАВИЛА ДЛЯ ТЕЛЕФОНА
    # --------------------------
    if product.category == "телефон":
        if product.brand is None:
            return build_collecting_response(
                product,
                attributes,
                "Какой бренд телефона?",
                step="brand",
                missing_fields=["brand"],
            )

        if "model" not in attributes:
            return build_collecting_response(
                product,
                attributes,
                "Какая модель телефона?",
                step="model",
                missing_fields=["model"],
            )

        if "memory" not in attributes:
            return build_collecting_response(
                product,
                attributes,
                "Какой объем памяти?",
                step="memory",
                missing_fields=["memory"],
            )

        if product.condition is None:
            return build_collecting_response(
                product,
                attributes,
                "В каком состоянии телефон?",
                step="condition",
                missing_fields=["condition"],
            )

        return build_completed_response(product, attributes)

    # --------------------------
    # ОБЩАЯ ЛОГИКА ПО КОНФИГУ
    # --------------------------
    missing_fields = get_missing_fields(product, attributes)

    # бренд не обязателен для некоторых категорий
    if product.category in OPTIONAL_BRAND_CATEGORIES:
        missing_fields = [field for field in missing_fields if field != "brand"]

    if missing_fields:
        next_field = missing_fields[0]
        question = get_question(product.category, next_field)

        return build_collecting_response(
            product,
            attributes,
            question,
            step=next_field,
            missing_fields=missing_fields,
        )

    # --------------------------
    # ЕСЛИ ДАННЫХ ДОСТАТОЧНО
    # --------------------------
    return build_completed_response(product, attributes)
