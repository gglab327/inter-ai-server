from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import urllib.parse

app = FastAPI()

# Отключаем блокировки CORS, чтобы Android-приложение беспрепятственно получало ответы
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    text: str
    image_base64: str = None  # Имя поля строго совпадает с вашим Android-приложением!

@app.get("/")
async def root_endpoint():
    return {"status": "Сервер Inter AI успешно запущен и работает!"}

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        # 1. Проверяем, прикрепил ли пользователь изображение (имя переменной исправлено!)
        if request.image_base64:
            # Формируем массив контента для мультимодальной нейросети со "зрением"
            content_structure = [
                {"type": "text", "text": request.text},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{request.image_base64}"
                    }
                }
            ]
            
            # Упаковываем JSON-тело для официального шлюза completions
            payload = {
                "model": "p1",  # Бесплатная мультимодальная модель
                "messages": [
                    {
                        "role": "user",
                        "content": content_structure
                    }
                ]
            }
            
            # Отправляем POST-запрос на ПРАВИЛЬНЫЙ адрес шлюза генерации
            response = requests.post(
                "https://pollinations.ai",
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Сбой ИИ при анализе фотографии")
                
            result = response.json()
            # Безопасно извлекаем ответ ИИ по официальной структуре OpenAI
            ai_reply = result["choices"][0]["message"]["content"]
            return {"reply": ai_reply}
            
        else:
            # 2. Если картинки НЕТ (отправлен простой текст), используем открытый GET-эндпоинт
            encoded_prompt = urllib.parse.quote(request.text)
            
            # ИСПРАВЛЕНО: Добавлен правильный субдомен text. и разделительный слэш /
            url = f"https://pollinations.ai{encoded_prompt}?model=search"
            
            response = requests.get(url, timeout=30)
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Сбой текстового ИИ шлюза")
                
            return {"reply": response.text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
