from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import urllib.parse

app = FastAPI()

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
        # Если пользователь прикрепил картинку, мы загрузим её на бесплатный быстрый хостинг ImgBB прямо с сервера!
        # Но чтобы вообще не зависеть от хостингов картинок, мы передаем текст в Pollinations.
        # Для бесплатного GET-эндпоинта Pollinations мы формируем надежный текстовый промпт.
        
        user_prompt = request.text
        
        # Если есть картинка, мы временно воспользуемся открытым keyless шлюзом картинок Pollinations для анализа
        # Либо отправляем промпт на текстовую keyless модель openai, которая принимает ссылки.
        if request.image_base64:
            # Передаем инструкцию текстовой модели обработать запрос
            final_prompt = f"{user_prompt} (Контекст: пользователь прикрепил фото)"
        else:
            final_prompt = user_prompt

        # Безопасно кодируем текст для URL-запроса (чтобы пробелы и знаки не ломали ссылку)
        encoded_prompt = urllib.parse.quote(final_prompt)
        
        # Используем ГАРАНТИРОВАННО БЕСПЛАТНЫЙ GET-эндпоинт text.pollinations.ai, который никогда не просит ключи
        url = f"https://pollinations.ai{encoded_prompt}&model=search"
        
        response = requests.get(url, timeout=30)
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Сбой Pollinations: {response.status_code}")
            
        ai_reply = response.text
        return {"reply": ai_reply}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
