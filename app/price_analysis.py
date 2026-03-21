import statistics


def remove_outliers(prices: list[int]) -> list[int]:
    """
    Удаляет выбросы из списка цен методом IQR.
    """

    if len(prices) < 4:
        return prices

    prices_sorted = sorted(prices)

    q1 = statistics.quantiles(prices_sorted, n=4)[0]
    q3 = statistics.quantiles(prices_sorted, n=4)[2]

    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    filtered = [price for price in prices_sorted if lower_bound <= price <= upper_bound]

    return filtered


def analyze_prices(prices: list[int]) -> dict:
    """
    Анализирует рынок и возвращает ключевые метрики.
    """

    if not prices:
        return {
            "min": 0,
            "max": 0,
            "median": 0,
            "recommended_price": 0,
        }

    prices = remove_outliers(prices)

    minimum = min(prices)
    maximum = max(prices)
    median = int(statistics.median(prices))

    recommended_price = int(median * 0.95)

    return {
        "min": minimum,
        "max": maximum,
        "median": median,
        "recommended_price": recommended_price,
    }
