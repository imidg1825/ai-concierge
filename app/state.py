from app.schemas import Product

# хранение состояния диалога (пока в памяти)
dialog_state = {}


def get_user_product(user_id: str) -> Product:
    if user_id not in dialog_state:
        dialog_state[user_id] = Product()
    return dialog_state[user_id]


def update_user_product(user_id: str, key: str, value):
    product = get_user_product(user_id)
    setattr(product, key, value)


def clear_user_state(user_id: str):
    if user_id in dialog_state:
        del dialog_state[user_id]
