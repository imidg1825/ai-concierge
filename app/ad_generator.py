from app.llm_client import generate_ad_text
from app.llm_client import parse_ai_text


def generate_ad_fallback(product, market):
    return generate_ad(product, market)


def generate_ad(product, market):
    brand = product.get("brand")
    category = product.get("category")
    condition = product.get("condition")
    attributes = product.get("attributes", {}) or {}

    median_price = market["median_price_rub"]
    recommended_price = market["recommended_price_rub"]

    # TITLE
    title_parts = []

    model = attributes.get("model")
    if brand and brand.lower() not in str(model).lower():
        title_parts.append(str(brand))
    if model:
        title_parts.append(str(model))
    elif category:
        title_parts.append(str(category))

    title = " ".join(title_parts).strip()
    if attributes:
        attrs = " ".join(str(v) for k, v in attributes.items() if v and k != "model")
    if attrs:
        title = f"{title} {attrs}".strip()
    if condition:
        condition_map = {
            "Хорошее": "в хорошем состоянии",
            "Отличное": "в отличном состоянии",
            "Новое": "новый",
        }

    condition_text = condition_map.get(condition, condition.lower())

    title = f"{title} — {condition_text}" if title else condition_text
    if not title:
        title = "Объявление"

        # DESCRIPTION
    item_name_parts = []
    if brand:
        item_name_parts.append(str(brand))
    if model:
        item_name_parts.append(str(model))
    elif category:
        item_name_parts.append(str(category))

    item_name = " ".join(item_name_parts).strip() or "товар"

    description_lines = [
        f"Продаю {item_name}.",
    ]

    if condition:
        description_lines.append(f"Состояние — {condition.lower()}.")
    else:
        description_lines.append("Состояние хорошее, товар полностью рабочий.")

    feature_lines = []

    if "memory" in attributes:
        feature_lines.append(f"память {attributes['memory']}")
    if "color" in attributes:
        feature_lines.append(f"цвет {attributes['color']}")
    if "size" in attributes:
        feature_lines.append(f"размер {attributes['size']}")
    if "material" in attributes:
        feature_lines.append(f"материал {attributes['material']}")
    if "type" in attributes:
        feature_lines.append(f"тип {attributes['type']}")

    if feature_lines:
        description_lines.append("Из характеристик: " + ", ".join(feature_lines) + ".")

    description_lines.append(
        "Подойдёт для повседневного использования. Можно сразу пользоваться без дополнительных вложений."
    )

    description_lines.append(
        f"Ориентир по рынку — около {median_price} ₽, рекомендованная цена продажи — {recommended_price} ₽."
    )

    description_lines.append("Если есть вопросы — пишите.")

    ai_text = generate_ad_text(product, market)
    parsed = parse_ai_text(ai_text)
    description = parsed["variant_1"] or " ".join(description_lines).strip()

    if description:
        return {
            "title": title,
            "description": description,
            "recommended_price": recommended_price,
        }

    return {
        "title": title,
        "description": " ".join(description_lines).strip(),
        "recommended_price": recommended_price,
    }
