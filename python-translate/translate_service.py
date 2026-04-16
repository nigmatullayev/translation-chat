import os
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from cerebras.cloud.sdk import Cerebras

from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

# Configure Cerebras
client = Cerebras(
    api_key=os.environ.get("CEREBRAS_API_KEY")
)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class TranslateRequest(BaseModel):
    text: str
    source_lang: str = "auto"  # Default to auto-detect
    target_lang: str

@app.post("/translate")
def translate(data: TranslateRequest):
    try:
        # Kodlarni to'liq nomga o'girish
        lang_map = {
            "uz": "Uzbek",
            "ru": "Russian",
            "en": "English",
            "tr": "Turkish",
            "kk": "Kazakh",
            "ky": "Kyrgyz",
            "tk": "Turkmen",
            "tg": "Tajik",
            "de": "German",
            "fr": "French",
            "es": "Spanish",
            "zh": "Chinese",
            "ko": "Korean",
            "ar": "Arabic"
        }
        target_lang_full = lang_map.get(data.target_lang, data.target_lang)

        system_instruction = (
            f"You are a professional translator. Translate the following chat message into {target_lang_full}. "
            "Maintain the original meaning, tone, and perspective (e.g., 'your' should remain second-person). "
            "Only return the translated text, absolutely nothing else. No quotes, no explanations."
        )
        
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": f"Message: {data.text}"}
            ],
            model="llama3.1-8b",
            max_completion_tokens=1024,
            temperature=0.2,
            stream=False
        )
        
        return {
            "translated_text": response.choices[0].message.content.strip()
        }
    except Exception as e:
        return {"error": str(e)}
