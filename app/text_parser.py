import re


def extract_product_data(text: str) -> dict:
    """
    Универсальный парсер товара.
    Извлекает:
    - category
    - brand
    - condition
    - price
    - attributes
    """

    text_lower = text.lower().strip()

    result = {
        "category": None,
        "brand": None,
        "condition": None,
        "price": None,
        "attributes": {},
    }

    # --------------------------
    # CATEGORY
    # --------------------------
    category_keywords = {
        "телефон": [
            "телефон",
            "смартфон",
            "iphone",
            "айфон",
            "samsung galaxy",
            "samsung",
            "самсунг",
            "redmi",
            "xiaomi",
        ],
        "ноутбук": [
            "ноутбук",
            "laptop",
            "macbook",
            "макбук",
        ],
        "часы": [
            "часы",
            "watch",
            "apple watch",
            "эпл вотч",
        ],
        "велосипед": [
            "велосипед",
            "байк",
            "горный велосипед",
            "шоссейный велосипед",
        ],
        "диван": [
            "диван",
            "угловой диван",
            "раскладной диван",
        ],
        "стул": [
            "стул",
            "кресло",
            "табурет",
        ],
    }

    for category, keywords in category_keywords.items():
        for word in keywords:
            if word in text_lower:
                result["category"] = category
                break
        if result["category"] is not None:
            break

    # --------------------------
    # BRAND
    # --------------------------
    brand_keywords = {
        "Apple": [
            "apple",
            "iphone",
            "айфон",
            "эпл",
            "macbook",
            "макбук",
            "apple watch",
        ],
        "Samsung": ["samsung", "galaxy", "самсунг"],
        "Xiaomi": ["xiaomi", "redmi", "mi", "сяоми"],
        "Huawei": ["huawei", "honor", "хуавей", "хонор"],
        "Asus": ["asus"],
        "Lenovo": ["lenovo"],
        "Acer": ["acer"],
        "HP": ["hp"],
        "Stels": ["stels"],
        "Trek": ["trek"],
        "Giant": ["giant"],
        "Merida": ["merida"],
        "IKEA": ["ikea", "икеа"],
    }

    for brand, keywords in brand_keywords.items():
        for word in keywords:
            if word in text_lower:
                result["brand"] = brand
                break
        if result["brand"] is not None:
            break

    # --------------------------
    # CONDITION
    # --------------------------
    if "отличн" in text_lower or "идеальн" in text_lower or "как новый" in text_lower:
        result["condition"] = "Отличное"
    elif "хорош" in text_lower or "нормальн" in text_lower:
        result["condition"] = "Хорошее"
    elif (
        "нов" in text_lower
        or "запечатан" in text_lower
        or "не вскрывался" in text_lower
    ):
        result["condition"] = "Новое"
    elif (
        "б/у" in text_lower
        or "бу" in text_lower
        or "подержан" in text_lower
        or "used" in text_lower
    ):
        result["condition"] = "Б/У"

    # --------------------------
    # PRICE
    # --------------------------
    numbers = re.findall(r"\d+", text_lower)

    for number in numbers:
        value = int(number)
        if value > 500:
            result["price"] = value
            break

    # --------------------------
    # ATTRIBUTES: MODEL
    # --------------------------
    iphone_model_match = re.search(
        r"((?:iphone|айфон)\s*\d{1,2}(?:\s*(?:pro\s*max|про\s*макс|pro|max|макс|mini|мини|pro|про))?)",
        text_lower,
    )
    if iphone_model_match:
        model = iphone_model_match.group(1)
        model = re.sub(r"\s+", " ", model).strip()

        model = (
            model.replace("айфон", "iPhone")
            .replace("iphone", "iPhone")
            .replace("про макс", "Pro Max")
            .replace("про", "Pro")
            .replace("макс", "Max")
            .replace("мини", "Mini")
        )

        result["attributes"]["model"] = model

    samsung_model_match = re.search(
        r"((?:samsung\s+galaxy|самсунг\s+галакси)\s+[a-zа-я]?\d{1,2}(?:\s*(?:ultra|plus|\+|fe))?)",
        text_lower,
    )
    if samsung_model_match and "model" not in result["attributes"]:
        model = samsung_model_match.group(1)
        model = re.sub(r"\s+", " ", model).strip()
        model = model.replace("самсунг галакси", "Samsung Galaxy").replace(
            "samsung galaxy", "Samsung Galaxy"
        )
        result["attributes"]["model"] = model

    macbook_model_match = re.search(
        r"((?:macbook|макбук)\s+(?:air|pro|эйр|про)(?:\s*\d{2})?)",
        text_lower,
    )
    if macbook_model_match and "model" not in result["attributes"]:
        model = macbook_model_match.group(1)
        model = re.sub(r"\s+", " ", model).strip()
        model = (
            model.replace("макбук", "MacBook")
            .replace("macbook", "MacBook")
            .replace("эйр", "Air")
            .replace("про", "Pro")
        )
        result["attributes"]["model"] = model

    # --------------------------
    # ATTRIBUTES: MEMORY
    # --------------------------
    memory_match = re.search(r"(\d+)\s?(gb|гб)", text_lower)
    if memory_match:
        result["attributes"]["memory"] = f"{memory_match.group(1)}GB"

    # --------------------------
    # ATTRIBUTES: COLOR
    # --------------------------
    color_keywords = [
        "черный",
        "белый",
        "серый",
        "красный",
        "синий",
        "зеленый",
        "желтый",
        "розовый",
        "фиолетовый",
        "бежевый",
        "коричневый",
    ]

    for color in color_keywords:
        if color in text_lower:
            result["attributes"]["color"] = color
            break

    # --------------------------
    # ATTRIBUTES: MATERIAL
    # --------------------------
    material_keywords = [
        "кожа",
        "экокожа",
        "ткань",
        "дерево",
        "металл",
        "пластик",
        "велюр",
    ]

    for material in material_keywords:
        if material in text_lower:
            result["attributes"]["material"] = material
            break

    # --------------------------
    # ATTRIBUTES: SIZE
    # --------------------------
    size_match = re.search(r"(\d{2,3})\s?[xх]\s?(\d{2,3})", text_lower)
    if size_match:
        result["attributes"]["size"] = f"{size_match.group(1)}x{size_match.group(2)}"
    else:
        size_meters_match = re.search(
            r"(\d+(?:[.,]\d+)?)\s*(м|метр|метра|метров)\b",
            text_lower,
        )
        if size_meters_match:
            result["attributes"]["size"] = size_meters_match.group(0).replace(",", ".")

    # --------------------------
    # ATTRIBUTES: BICYCLE TYPE
    # --------------------------
    if "горный" in text_lower:
        result["attributes"]["type"] = "горный"
    elif "шоссейный" in text_lower:
        result["attributes"]["type"] = "шоссейный"
    elif "городской" in text_lower:
        result["attributes"]["type"] = "городской"

    return result
