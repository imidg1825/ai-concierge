import re
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup


BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9," "image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
}


def clean_prices(prices: list[int]) -> list[int]:
    return sorted(
        {
            price
            for price in prices
            if isinstance(price, int) and 1000 < price < 1_000_000
        }
    )


def extract_rub_prices_from_text(text: str) -> list[int]:
    """
    Ищет цены вида:
    - 33 000 ₽
    - 1000 ₽
    - 12 500 руб
    - 12500 р
    """
    prices: list[int] = []

    pattern = re.compile(
        r"(\d{1,3}(?:[ \u00A0]\d{3})+|\d{3,7})(?:[.,]\d{2})?\s*(?:₽|руб|р)",
        flags=re.IGNORECASE,
    )

    for match in pattern.findall(text):
        raw = re.sub(r"\D", "", match)
        if not raw:
            continue

        value = int(raw)
        if 1000 < value < 1_000_000:
            prices.append(value)

    return prices


def looks_like_market_price(value: int, query: str = "") -> bool:
    """
    Фильтр цен с учетом типа товара.
    """
    query_lower = query.lower()

    # iPhone / телефоны
    if "iphone" in query_lower or "телефон" in query_lower or "смартфон" in query_lower:
        return 15000 < value < 200000

    # ноутбуки / MacBook
    if "macbook" in query_lower or "ноутбук" in query_lower or "laptop" in query_lower:
        return 20000 < value < 300000

    # диваны / мебель
    if "диван" in query_lower:
        return 10000 < value < 80000

    # велосипеды
    if "велосипед" in query_lower:
        return 5000 < value < 200000

    # fallback
    return 5000 < value < 200000


def remove_outliers(prices: list[int]) -> list[int]:
    """
    Убирает выбросы по простому IQR-подходу.
    Если данных мало, возвращает как есть.
    """
    if len(prices) < 4:
        return prices

    prices = sorted(prices)

    q1 = prices[len(prices) // 4]
    q3 = prices[(len(prices) * 3) // 4]

    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    return [p for p in prices if lower <= p <= upper]


def search_yandex(query: str) -> list[int]:
    print(f"🟡 search_yandex query: {query}")

    search_query = f"{query} цена"
    url = f"https://yandex.ru/search/?text={quote_plus(search_query)}"

    try:
        response = requests.get(
            url,
            headers=BROWSER_HEADERS,
            timeout=(10, 40),
        )
        print("🟡 Yandex status:", response.status_code)
        response.raise_for_status()

    except requests.Timeout as e:
        print("❌ Таймаут Yandex:", e)
        return []

    except requests.RequestException as e:
        print("❌ Ошибка Yandex:", e)
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    # Берем весь HTML, потому что числа могут лежать не в обычном тексте
    html = soup.prettify()

    # Ищем все числа длиной 4-7 цифр
    raw_numbers = re.findall(r"\d{4,7}", html)

    prices: list[int] = []

    for num in raw_numbers:
        try:
            value = int(num)

            if looks_like_market_price(value, search_query):
                prices.append(value)

        except Exception:
            continue

    prices = clean_prices(prices)

    print(f"🟡 Yandex parsed prices: {prices[:30]}")
    return prices[:30]


def search_prices(query: str) -> list[int]:
    print(f"🔎 Ищу цены по запросу: {query}")

    prices: list[int] = []

    yandex_prices = search_yandex(query)

    print(f"🟡 Yandex: {yandex_prices}")

    prices.extend(yandex_prices)

    prices = clean_prices(prices)
    prices = remove_outliers(prices)

    print(f"💰 Итоговые цены в рублях: {prices}")
    return prices
