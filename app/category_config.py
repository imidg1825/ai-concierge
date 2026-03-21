CATEGORY_CONFIG = {
    "телефон": {
        "required_fields": ["brand", "model", "memory", "condition"],
        "questions": {
            "brand": "Какой бренд телефона?",
            "model": "Какая модель?",
            "memory": "Какой объём памяти?",
            "condition": "В каком состоянии телефон?",
        },
    },
    "диван": {
        "required_fields": ["size", "material", "color", "condition"],
        "questions": {
            "size": "Какой размер дивана?",
            "material": "Из какого материала диван?",
            "color": "Какого он цвета?",
            "condition": "В каком состоянии диван?",
        },
    },
    "велосипед": {
        "required_fields": ["type", "brand", "condition"],
        "questions": {
            "type": "Какой это тип велосипеда? Горный, городской, шоссейный?",
            "brand": "Какой бренд велосипеда?",
            "condition": "В каком состоянии велосипед?",
        },
    },
}

DEFAULT_QUESTIONS = {
    "category": "Что именно вы продаёте?",
    "brand": "Какой бренд?",
    "model": "Какая модель?",
    "memory": "Какой объём памяти?",
    "condition": "В каком состоянии товар?",
    "size": "Какой размер?",
    "material": "Из какого материала?",
    "color": "Какого цвета товар?",
    "type": "Какой это тип?",
}
