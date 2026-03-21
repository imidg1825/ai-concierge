import os
import requests
import re

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


def generate_ad_text(product: dict, market: dict) -> str:
    if not OPENROUTER_API_KEY:
        print("LLM error: API key not found")
        return ""

    prompt = f"""
Ты помогаешь написать объявление для Авито.

Нужно вернуть РОВНО 3 разных варианта текста объявления.

Правила:
- пиши как обычный человек, будто продаешь свою вещь
- допускается легкая разговорность (например: "все работает", "можно проверить при встрече")
- без пафоса и кричащей рекламы
- не выдумывай характеристики, которых нет во входных данных
- текст должен быть живым и читаемым
- каждый вариант должен быть 2-4 предложения
- без markdown
- без списков
- без пояснений от себя
- не объединяй варианты в один абзац

Формат ответа ОБЯЗАТЕЛЬНО такой:

Вариант 1:
<текст>

Вариант 2:
<текст>

Вариант 3:
<текст>

Никакого другого текста быть не должно.

Пиши так, чтобы объявление выглядело как реальное на Авито, а не как текст от нейросети.

Данные товара:
Категория: {product.get("category")}
Бренд: {product.get("brand")}
Состояние: {product.get("condition")}
Характеристики: {product.get("attributes")}
Рекомендуемая цена: {market.get("recommended_price_rub")} руб
""".strip()

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "openrouter/auto",
                "messages": [
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.9,
            },
            timeout=30,
        )

        response.raise_for_status()
        data = response.json()

        return data["choices"][0]["message"]["content"].strip()

    except Exception as e:
        print(f"LLM error: {e}")
        return ""


def parse_ai_text(ai_text: str) -> dict:
    result = {
        "variant_1": "",
        "variant_2": "",
        "variant_3": "",
    }

    if not ai_text or not ai_text.strip():
        return result

    pattern = re.compile(
        r"Вариант\s*1:\s*(.*?)\s*Вариант\s*2:\s*(.*?)\s*Вариант\s*3:\s*(.*)",
        re.DOTALL | re.IGNORECASE,
    )

    match = pattern.search(ai_text)

    if match:
        result["variant_1"] = match.group(1).strip()
        result["variant_2"] = match.group(2).strip()
        result["variant_3"] = match.group(3).strip()
        return result

    result["variant_1"] = ai_text.strip()
    return result
