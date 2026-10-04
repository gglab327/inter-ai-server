from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

app = FastAPI()

# Разрешаем вашему Android-приложению отправлять запросы без блокировок CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    text: str
    image_base64: str = None  # Картинка не обязательна, чат может быть и просто текстовым

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    # Если пользователь прикрепил картинку, формируем мультимодальный запрос для зрения
    if request.image_base64:
        content_structure = [
            {"type": "text", "text": request.text},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{request.image_base64}"
                }
            }
        ]
    else:
        # Если картинки нет, отправляем обычный текст
        content_structure = request.text

    # Формируем стандартное JSON-тело для продвинутого бесплатного шлюза Pollinations
    payload = {
        "model": "openai",  # Используем стабильную модель
        "messages": [
            {
                "role": "user",
                "content": content_structure
            }
        ]
    }

    try:
        response = requests.post(
            "https://pollinations.ai",
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Сбой ИИ сервера")
            
        result = response.json()
        ai_reply = result["choices"][0]["message"]["content"]
        return {"reply": ai_reply}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
