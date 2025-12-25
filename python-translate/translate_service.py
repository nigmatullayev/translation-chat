import os
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
app = FastAPI()

class TranslateRequest(BaseModel):
    text: str
    source_lang: str = "auto"  # Default to auto-detect
    target_lang: str

@app.post("/translate")
def translate(data: TranslateRequest):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional translator. Only return the translated text, nothing else. Do not add explanations, quotes, or extra context."
                },
                {
                    "role": "user",
                    "content": f"Translate from {data.source_lang} to {data.target_lang}: {data.text}" if data.source_lang != "auto" else f"Translate to {data.target_lang}: {data.text}"
                }
            ]
        )
        return {
            "translated": response.choices[0].message.content.strip()
        }
    except Exception as e:
        return {"error": str(e)}
