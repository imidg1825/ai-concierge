def generate_ad_local(product, market):
    """
    Генерация объявления на основе данных товара и анализа рынка.
    Работает и для товаров с брендом, и без бренда.
    """

    brand = product.get("brand")
    category = product.get("category")
    condition = product.get("condition")
    attributes = product.get("attributes", {})

    median_price = market["median_price_rub"]
    recommended_price = market["recommended_price_rub"]

    # --------------------------
    # TITLE
    # --------------------------
    title_parts = []

    if brand:
        title_parts.append(str(brand))

    if category:
        title_parts.append(str(category))

    if condition:
        title_parts.append(condition)

    title = " — ".join(
        [
            (
                " ".join(title_parts[:-1]).strip()
                if len(title_parts) > 1
                else title_parts[0]
            )
            for _ in [0]
        ]
    )

    if len(title_parts) >= 2:
        title = f"{' '.join(title_parts[:-1]).strip()} — {title_parts[-1]}"
    elif len(title_parts) == 1:
        title = title_parts[0]
    else:
        title = "Объявление"

    # --------------------------
    # DESCRIPTION
    # --------------------------
    item_name_parts = []

    if brand:
        item_name_parts.append(str(brand))

    if category:
        item_name_parts.append(str(category))

    item_name = " ".join(item_name_parts).strip()
    if not item_name:
        item_name = "товар"

    description_lines = [
        f"Продается {item_name}.",
        f"Состояние: {condition}.",
    ]

    if attributes:
        description_lines.append("")
        description_lines.append("Характеристики:")

        if "size" in attributes:
            description_lines.append(f"- Размер: {attributes['size']}")
        if "color" in attributes:
            description_lines.append(f"- Цвет: {attributes['color']}")
        if "material" in attributes:
            description_lines.append(f"- Материал: {attributes['material']}")
        if "memory" in attributes:
            description_lines.append(f"- Память: {attributes['memory']}")
        if "type" in attributes:
            description_lines.append(f"- Тип: {attributes['type']}")

    description_lines.extend(
        [
            "",
            f"Средняя цена на рынке: {median_price} ₽.",
            f"Рекомендуемая цена продажи: {recommended_price} ₽.",
            "",
            "Товар полностью рабочий.",
            "Готов к использованию.",
        ]
    )

    return {
        "title": title,
        "description": "\n".join(description_lines).strip(),
        "recommended_price": recommended_price,
    }


import os
import requests
from dotenv import load_dotenv

load_dotenv()


def generate_ad(product: dict, price: int) -> dict:
    api_key = os.getenv("DEEPSEEK_API_KEY")

    prompt = f"""
Напиши объявление для Авито.

Стиль:
- как обычный человек
- без рекламы
- просто и понятно

Данные:
{product}

Цена: {price} рублей

Сделай:
1. Заголовок
2. Описание (2-3 предложения)
"""

    response = requests.post(
        "https://api.deepseek.com/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
        },
    )

    print(response.status_code)
    print(response.text)

    data = response.json()
    text = data["candidates"][0]["content"]["parts"][0]["text"]

    return {"raw": text}


import os
from google import genai


def generate_ad_gemini(product: dict, price: int) -> dict:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    prompt = f"""
Сгенерируй объявление для продажи товара.

Бренд: {product.get("brand")}
Модель: {product.get("category")}
Состояние: {product.get("condition")}
Характеристики: {product.get("attributes")}
Цена: {price} рублей

Формат:
Заголовок: ...
Описание: ...
"""

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt,
    )

    return {"raw": response.text}
