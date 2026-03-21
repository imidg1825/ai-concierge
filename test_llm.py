from app.ad_generator import generate_ad_gemini as generate_ad

product = {
    "brand": None,
    "category": "угловой диван",
    "attributes": {"size": "240x160", "color": "серый", "material": "ткань"},
    "condition": "б/у, хорошее",
}

price = 18000

result = generate_ad(product, price)

print(result["raw"])
