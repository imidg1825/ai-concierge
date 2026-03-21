from app.schemas import Product


def build_market_query(product: Product, attributes: dict | None = None) -> str:
    """
    Строит поисковый запрос для поиска рыночных цен.

    Логика:
    1. Если есть model — используем её как основу.
    2. Если есть memory — добавляем.
    3. Если модели нет — используем brand + category.
    4. Для мебели и похожих товаров добавляем size / material.
    """

    parts = []

    # 1. Модель — самый сильный сигнал
    if attributes and attributes.get("model"):
        parts.append(attributes["model"])

    # 2. Память
    if attributes and attributes.get("memory"):
        parts.append(attributes["memory"])

    # 3. Если модели нет — бренд + категория
    if not parts:
        if product.brand:
            parts.append(product.brand)

        if product.category:
            parts.append(product.category)

    # 4. Дополнительные характеристики
    if attributes:
        if attributes.get("size"):
            parts.append(attributes["size"])

        if attributes.get("material"):
            parts.append(attributes["material"])

    query = " ".join(parts).strip()

    print(f"🧠 market query built: {query}")

    return query
