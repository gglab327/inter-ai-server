from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import urllib.parse

app = FastAPI()

# Настройка CORS, чтобы Android-приложение не блокировало ответы
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    text: str
    image_base64: str = None

@app.get("/")
async def root_endpoint():
    return {"status": "Сервер Inter AI успешно запущен и работает!"}

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        user_prompt = request.text
        
        # Если пользователь прикрепил картинку, мы добавляем текстовое указание для модели
        if request.image_base64:
            final_prompt = f"{user_prompt} (Пользователь прикрепил изображение)"
        else:
            final_prompt = user_prompt

        # Безопасно кодируем русский текст для URL (кириллица не сломает запрос)
        encoded_prompt = urllib.parse.quote(final_prompt)
        
        # Используем полностью открытый и бесплатный эндпоинт Pollinations AI
        url = f"https://pollinations.ai{encoded_prompt}?model=search"
        
        # Делаем GET-запрос к ИИ
        response = requests.get(url, timeout=30)
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Сбой ИИ шлюза")
        
        # КРИТИЧЕСКИ ВАЖНО: text.pollinations.ai возвращает чистый текст, а не JSON!
        # Мы просто забираем этот готовый текст ответа ИИ
        ai_reply = response.text
        
        # Возвращаем JSON-объект, который ожидает получить ваше Android-приложение
        return {"reply": ai_reply}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
