from app.state import get_user_product, update_user_product
from app.market import build_market_query
from app.price_search import search_prices
from app.price_analysis import analyze_prices
from app.ad_generator import generate_ad, generate_ad_fallback
from app.text_parser import extract_product_data
from app.category_config import CATEGORY_CONFIG, DEFAULT_QUESTIONS


def get_missing_fields(product, attributes):
    category = product.category

    # если категории нет — сначала нужна она
    if not category:
        return ["category"]

    config = CATEGORY_CONFIG.get(category)

    # если категории нет в конфиге — минимум требуем состояние
    if not config:
        required_fields = ["condition"]
    else:
        required_fields = config["required_fields"]

    missing = []

    for field in required_fields:
        value = None

        # сначала ищем в product
        if hasattr(product, field):
            value = getattr(product, field)

        # потом в attributes
        if not value:
            value = attributes.get(field)

        if not value:
            missing.append(field)

    return missing


def get_question(category, field):
    config = CATEGORY_CONFIG.get(category, {})
    questions = config.get("questions", {})
    return questions.get(field, DEFAULT_QUESTIONS.get(field, f"Уточните: {field}"))


def process_message(text: str, user_id: str = "default"):
    parsed = extract_product_data(text)

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

    product = get_user_product(user_id)
    old_attributes = getattr(product, "attributes", {}) or {}
    new_attributes = parsed.get("attributes", {}) or {}
    attributes = {**old_attributes, **new_attributes}

    update_user_product(user_id, "attributes", attributes)

    # --------------------------
    # ПРОВЕРКА НЕДОСТАЮЩИХ ПОЛЕЙ
    # --------------------------
    missing_fields = get_missing_fields(product, attributes)

    if missing_fields:
        next_field = missing_fields[0]
        question = get_question(product.category, next_field)

        return {
            "step": "collecting",
            "message": question,
            "product": {
                "category": product.category,
                "brand": product.brand,
                "condition": product.condition,
                "user_price_rub": product.price or 0,
                "attributes": attributes,
            },
            "market": {
                "query": "",
                "min_price_rub": 0,
                "max_price_rub": 0,
                "median_price_rub": 0,
                "recommended_price_rub": 0,
            },
            "missing_fields": missing_fields,
            "status": "waiting_for_details",
        }

    # --------------------------
    # ЕСЛИ ДАННЫХ ДОСТАТОЧНО ДЛЯ ГЕНЕРАЦИИ
    # brand не обязателен
    # --------------------------
    if (
        product.category is not None
        and product.condition is not None
        and product.price is not None
    ):
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

    # --------------------------
    # КАТЕГОРИЯ
    # --------------------------
    if product.category is None:
        return {
            "step": "category",
            "message": "Что вы хотите продать?",
            "product": {
                "category": product.category,
                "brand": product.brand,
                "condition": product.condition,
                "user_price_rub": product.price or 0,
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
            "status": "collecting_data",
        }

    # --------------------------
    # СОСТОЯНИЕ
    # --------------------------
    if product.condition is None:
        return {
            "step": "condition",
            "message": "Укажите состояние товара.",
            "product": {
                "category": product.category,
                "brand": product.brand,
                "condition": product.condition,
                "user_price_rub": product.price or 0,
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
            "status": "collecting_data",
        }

    # --------------------------
    # ЦЕНА
    # --------------------------
    # if product.price is None:
    #    return {
    #       "step": "price",
    #      "message": "Укажите цену в рублях.",
    #      "product": {
    #          "category": product.category,
    #          "brand": product.brand,
    #         "condition": product.condition,
    #         "user_price_rub": product.price or 0,
    #        "attributes": attributes,
    #   },
    #   "market": {
    #      "query": "",
    #     "min_price_rub": 0,
    #      "max_price_rub": 0,
    #     "median_price_rub": 0,
    #     "recommended_price_rub": 0,
    # },
    #  "ad": None,
    #  "status": "collecting_data",
    # }

    # --------------------------
    # ЗАПАСНОЙ ФИНАЛ
    # --------------------------
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
