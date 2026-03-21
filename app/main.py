from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from app.schemas import MessageRequest, MessageResponse
from app.assistant import process_message
from app.state import clear_user_state

app = FastAPI(
    title="AI Консьерж API",
    description="Ассистент для помощи в продаже товаров",
    docs_url=None,
    redoc_url=None,
    openapi_url="/openapi.json",
)


@app.get("/docs", include_in_schema=False)
def custom_swagger_ui():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="AI Concierge API - Swagger UI",
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post(
    "/message",
    response_model=MessageResponse,
    tags=["AI Консьерж"],
    summary="Диалог с AI-консьержем для продажи товара",
)
def message(data: MessageRequest):
    result = process_message(data.text)
    return result


@app.post(
    "/reset",
    tags=["AI Консьерж"],
    summary="Сбросить текущий диалог пользователя",
)
def reset():
    clear_user_state("default")
    return {"status": "dialog reset"}
