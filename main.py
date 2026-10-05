from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import urllib.parse

app = FastAPI()

# Отключаем блокировки CORS для Android-приложения
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    text: str
    image_base_base64: str = None  # Имя поля может быть любым, сейчас оно не ломает код

@app.get("/")
async def root_endpoint():
    return {"status": "Сервер Inter AI успешно запущен и работает!"}

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        # Извлекаем чистый текст сообщения пользователя
        user_prompt = request.text
        
        # Безопасно кодируем русский текст для передачи внутри URL (чтобы кириллица не вызывала сбоев)
        encoded_prompt = urllib.parse.quote(user_prompt)
        
        # Отправляем запрос на 100% бесплатный, keyless и открытый GET-эндпоинт Pollinations AI
        url = f"https://text.pollinations.ai/{encoded_prompt}?model=search"
        
        # Делаем GET-запрос к ИИ
        response = requests.get(url, timeout=30)
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Сбой ИИ шлюза")
        
        # text.pollinations.ai возвращает чистый Plain Text (не JSON!). Мы просто забираем его.
        ai_reply = response.text
        
        # Формируем аккуратный JSON-ответ, который ждет ваше Android-приложение
        return {"reply": ai_reply}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
