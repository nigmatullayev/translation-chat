# import os
# import sqlite3
# from fastapi import FastAPI
# from pydantic import BaseModel
# from dotenv import load_dotenv
# from google import genai
# from google.genai import types
# from fastapi.middleware.cors import CORSMiddleware

# load_dotenv()

# # 1. API kalitni .env dan aniq o'qib olamiz
# api_key = os.environ.get("GEMINI_API_KEY")

# # 2. Kalitni Client'ga majburiy tarzda beramiz
# client = genai.Client(api_key=api_key)

# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# DB_FILE = "translations_cache.db"

# def init_db():
#     conn = sqlite3.connect(DB_FILE)
#     cursor = conn.cursor()
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS cache (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             original_text TEXT,
#             target_lang TEXT,
#             translated_text TEXT,
#             UNIQUE(original_text, target_lang)
#         )
#     ''')
#     conn.commit()
#     conn.close()

# init_db()

# class TranslateRequest(BaseModel):
#     text: str
#     source_lang: str = "auto"
#     target_lang: str

# @app.post("/translate")
# def translate(data: TranslateRequest):
#     try:
#         if not any(char.isalpha() for char in data.text):
#             return {"translated_text": data.text, "is_cached": True}

#         conn = sqlite3.connect(DB_FILE)
#         cursor = conn.cursor()
#         cursor.execute(
#             "SELECT translated_text FROM cache WHERE original_text = ? AND target_lang = ?", 
#             (data.text, data.target_lang)
#         )
#         cached_result = cursor.fetchone()
        
#         if cached_result:
#             conn.close()
#             return {"translated_text": cached_result[0], "is_cached": True}

#         lang_map = {
#             "uz": "Uzbek", "ru": "Russian", "en": "English", "tr": "Turkish",
#             "kk": "Kazakh", "ky": "Kyrgyz", "tk": "Turkmen", "tg": "Tajik",
#             "de": "German", "fr": "French", "es": "Spanish", "zh": "Chinese",
#             "ko": "Korean", "ar": "Arabic"
#         }
#         target_lang_full = lang_map.get(data.target_lang, data.target_lang)

#         system_instruction = (
#             f"You are a strict, literal translation engine. Your target language is {target_lang_full}. "
#             "CRITICAL RULES: "
#             f"1. SAME LANGUAGE CHECK: If the input text is ALREADY in {target_lang_full}, you MUST output the exact original text. Do not translate, do not change anything. "
#             "2. MEANINGLESS TEXT CHECK: If the text is meaningless gibberish, random keystrokes (e.g., 'asdf', 'gdrg', 'qwerty'), or lacks semantic meaning, output the exact original text. Do not try to make sense of it. "
#             "3. NO CONVERSATION: Never answer questions. (e.g., If the text is 'What is your name?', just translate the question itself). "
#             "4. RAW OUTPUT ONLY: Output strictly the final text. No quotes, no intro, no notes, no apologies."
#             "5. SHORT WORDS: Handle short words gracefully based on chat context (e.g., 'zor' = 'zo'r' = great/awesome; 'ishlamadi' = didn't work). Do not hallucinate meanings."
#         )
        
#         # Gemini uchun yangi chaqiruv usuli
#         response = client.models.generate_content(
#             model='gemini-2.5-flash',
#             contents=data.text,
#             config=types.GenerateContentConfig(
#                 system_instruction=system_instruction,
#                 temperature=0.1,
#                 max_output_tokens=500,
#             ),
#         )
        
#         translated_text = response.text.strip()

#         cursor.execute(
#             "INSERT OR IGNORE INTO cache (original_text, target_lang, translated_text) VALUES (?, ?, ?)",
#             (data.text, data.target_lang, translated_text)
#         )
#         conn.commit()
#         conn.close()

#         return {"translated_text": translated_text, "is_cached": False}
        
#     except Exception as e:
#         print(f"Tarjima xatosi: {e}")
#         return {"error": str(e)}

# import os
# import sqlite3
# import json
# from fastapi import FastAPI
# from pydantic import BaseModel
# from dotenv import load_dotenv
# from cerebras.cloud.sdk import Cerebras
# from fastapi.middleware.cors import CORSMiddleware

# load_dotenv()

# # Cerebras ga ulanish
# api_key = os.environ.get("CEREBRAS_API_KEY")
# client = Cerebras(api_key=api_key)

# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# DB_FILE = "translations_cache.db"

# def init_db():
#     conn = sqlite3.connect(DB_FILE)
#     cursor = conn.cursor()
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS cache (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             original_text TEXT,
#             target_lang TEXT,
#             translated_text TEXT,
#             UNIQUE(original_text, target_lang)
#         )
#     ''')
#     conn.commit()
#     conn.close()

# init_db()

# # --- MODELLAR ---
# class TranslateItem(BaseModel):
#     id: str
#     text: str

# class BatchTranslateRequest(BaseModel):
#     messages: list[TranslateItem]
#     target_lang: str

# @app.post("/translate-batch")
# def translate_batch(data: BatchTranslateRequest):
#     try:
#         conn = sqlite3.connect(DB_FILE)
#         cursor = conn.cursor()
        
#         final_translations = {}
#         uncached_messages_dict = {} # AI ga yuborish uchun lug'at {id: matn}

#         # 1. Keshdan qidirish
#         for msg in data.messages:
#             msg_id = str(msg.id)
#             original_text = msg.text.strip()

#             if not any(char.isalpha() for char in original_text):
#                 final_translations[msg_id] = original_text
#                 continue

#             # 1. Keshdan qidirish va BIR XIL matnlarni guruhlash
#             for msg in data.messages:
#                 msg_id = str(msg.id)
#                 original_text = msg.text.strip()

#                 # --- YANGI QISM ---
#                 # Agar xabarda faqat emojilar yoki tinish belgilari bo'lsa (harf yo'q bo'lsa)
#                 # yoki matn emojilardan iborat bo'lsa, uni aslicha qaytaramiz
#                 if not any(char.isalpha() for char in original_text) or emoji.is_emoji(original_text.replace(" ", "")):
#                      final_translations[msg_id] = original_text
#                      continue
#                 # -------------------

#                 cursor.execute(
#                     "SELECT translated_text FROM cache WHERE original_text = ? AND target_lang = ?", 
#                     (original_text, data.target_lang)
#                 )

#             cursor.execute(
#                 "SELECT translated_text FROM cache WHERE original_text = ? AND target_lang = ?", 
#                 (original_text, data.target_lang)
#             )
#             cached_result = cursor.fetchone()
            
#             if cached_result:
#                 final_translations[msg_id] = cached_result[0]
#             else:
#                 # Agar bazada yo'q bo'lsa, lug'atga yig'amiz
#                 uncached_messages_dict[msg_id] = original_text

#         # 2. Agar hammasi bazada bo'lsa, tamom.
#         if not uncached_messages_dict:
#             conn.close()
#             return {"translations": final_translations}

#         # 3. AI ga yuborish
#         lang_map = {
#             "uz": "Uzbek", "ru": "Russian", "en": "English", "tr": "Turkish",
#             "kk": "Kazakh", "ky": "Kyrgyz", "tk": "Turkmen", "tg": "Tajik",
#             "de": "German", "fr": "French", "es": "Spanish", "zh": "Chinese",
#             "ko": "Korean", "ar": "Arabic"
#         }
#         target_lang_full = lang_map.get(data.target_lang, data.target_lang)

#         system_instruction = (
#             f"You are an expert bilingual interpreter. Your task is to accurately translate the values of a JSON object into {target_lang_full}. "
#             "CONTEXT: The input texts are from an informal, fast-paced chat app. They contain heavy slang, abbreviations, grammatical errors, typos, mixed scripts, and EMOJIS. "
#             "CRITICAL RULES: "
#             f"1. TRANSLATE MEANING: Understand the informal context and translate the intended meaning into natural {target_lang_full}. "
#             "2. EMOJIS (CRITICAL): NEVER translate, describe, or alter emojis. Keep all emojis EXACTLY as they appear in the original text and in the same position (e.g., 'salom 👋' -> 'привет 👋'). "
#             f"3. IF ALREADY IN TARGET: If the text is fundamentally already in {target_lang_full}, correct the typos and keep it in {target_lang_full}. "
#             f"4. NAMES: Transliterate proper names into the target language's alphabet (e.g., 'Komilon' -> 'Комилон' in Russian). "
#             "5. MEANINGLESS: Do not translate absolute gibberish. "
#             "6. OUTPUT FORMAT: Return ONLY a valid JSON object matching the input keys. No markdown (like ```json), no conversational text."
#         )

#         input_json_str = json.dumps(uncached_messages_dict, ensure_ascii=False)
        
#         response = client.chat.completions.create(
#             messages=[
#                 {"role": "system", "content": system_instruction},
#                 {"role": "user", "content": input_json_str}
#             ],
#             model="llama3.1-8b",
#             temperature=0.3,
#             max_completion_tokens=2048,
#             stream=False
#         )
        
#         raw_response = response.choices[0].message.content.strip()
        
#         if raw_response.startswith("```json"):
#             raw_response = raw_response[7:]
#         if raw_response.endswith("```"):
#             raw_response = raw_response[:-3]
#         raw_response = raw_response.strip()

#         # 4. Javobni o'qiymiz va BAZAGA SAQLAYMIZ
#         translated_json = json.loads(raw_response)
        
#         for msg_id, translated_text in translated_json.items():
#             msg_id = str(msg_id) # ID ni xavfsiz holatga keltirish
#             translated_text = translated_text.strip()
            
#             # 4.1 Javobni mijozga jo'natish uchun saqlaymiz
#             final_translations[msg_id] = translated_text
            
#             # 4.2 Bazaga saqlash uchun asl matnni dict dan olamiz
#             original_txt = uncached_messages_dict.get(msg_id)
            
#             if original_txt:
#                 try:
#                     # Baza yozish
#                     cursor.execute(
#                         "INSERT OR IGNORE INTO cache (original_text, target_lang, translated_text) VALUES (?, ?, ?)",
#                         (original_txt, data.target_lang, translated_text)
#                     )
#                 except sqlite3.Error as db_err:
#                     print(f"Bazaga yozishda xato: {db_err}")
        
#         conn.commit()
#         conn.close()

#         return {"translations": final_translations}
        
#     except Exception as e:
#         print(f"Batch Tarjima xatosi: {e}")
#         return {"error": str(e)}

# # --- ESKI (YAKKA) TARJIMA UCHUN YORDAMCHI API ---
# class TranslateRequest(BaseModel):
#     text: str
#     source_lang: str = "auto"
#     target_lang: str

# @app.post("/translate")
# def translate(data: TranslateRequest):
#     try:
#         # Bazadan izlash
#         conn = sqlite3.connect(DB_FILE)
#         cursor = conn.cursor()
#         cursor.execute(
#             "SELECT translated_text FROM cache WHERE original_text = ? AND target_lang = ?", 
#             (data.text, data.target_lang)
#         )
#         cached = cursor.fetchone()
        
#         if cached:
#             conn.close()
#             return {"translated_text": cached[0], "is_cached": True}

#         # Agar bazada yo'q bo'lsa Cerebras orqali bitta xabarni tarjima qilish
#         lang_map = {
#             "uz": "Uzbek", "ru": "Russian", "en": "English"
#         }
#         target_lang_full = lang_map.get(data.target_lang, data.target_lang)

#         system_instruction = (
#             f"You are a professional translator. Translate to {target_lang_full}. "
#             "Only output the raw translated text. No explanations."
#         )
        
#         response = client.chat.completions.create(
#             messages=[
#                 {"role": "system", "content": system_instruction},
#                 {"role": "user", "content": data.text}
#             ],
#             model="llama3.1-8b",
#             temperature=0.1,
#             max_completion_tokens=500,
#             stream=False
#         )
        
#         translated_text = response.choices[0].message.content.strip()

#         cursor.execute(
#             "INSERT OR IGNORE INTO cache (original_text, target_lang, translated_text) VALUES (?, ?, ?)",
#             (data.text, data.target_lang, translated_text)
#         )
#         conn.commit()
#         conn.close()

#         return {"translated_text": translated_text, "is_cached": False}
        
#     except Exception as e:
#         print(f"Yakka tarjima xatosi: {e}")
#         return {"error": str(e)}

import os
import sqlite3
import json
import emoji
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from cerebras.cloud.sdk import Cerebras
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

# Cerebras ga ulanish
api_key = os.environ.get("CEREBRAS_API_KEY")
client = Cerebras(api_key=api_key)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = "translations_cache.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_text TEXT,
            target_lang TEXT,
            translated_text TEXT,
            UNIQUE(original_text, target_lang)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- YORDAMCHI FUNKSIYA (Emojilarni bloklash uchun) ---
def is_valid_for_translation(text: str) -> bool:
    """Matnda kamida bitta harf bo'lsagina True qaytaradi."""
    return any(char.isalpha() for char in text)

# --- MODELLAR ---
class TranslateItem(BaseModel):
    id: str
    text: str

class BatchTranslateRequest(BaseModel):
    messages: list[TranslateItem]
    target_lang: str

class TranslateRequest(BaseModel):
    text: str
    source_lang: str = "auto"
    target_lang: str


# ==========================================
# 1. BATCH API (Skroll avto-tarjima uchun)
# ==========================================
@app.post("/translate-batch")
def translate_batch(data: BatchTranslateRequest):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        final_translations = {}
        unique_texts_map = {}

        # 1. Keshdan qidirish va guruhlash
        for msg in data.messages:
            msg_id = str(msg.id)
            original_text = msg.text.strip()

            # HIMOYA: Agar faqat emoji/raqam/belgi bo'lsa -> Bazaga ham, AI ga ham bormaydi!
            if not is_valid_for_translation(original_text):
                 final_translations[msg_id] = original_text
                 continue

            cursor.execute(
                "SELECT translated_text FROM cache WHERE original_text = ? AND target_lang = ?", 
                (original_text, data.target_lang)
            )
            cached_result = cursor.fetchone()
            
            if cached_result:
                final_translations[msg_id] = cached_result[0]
            else:
                if original_text not in unique_texts_map:
                    unique_texts_map[original_text] = []
                unique_texts_map[original_text].append(msg_id)

        if not unique_texts_map:
            conn.close()
            return {"translations": final_translations}

        # 2. AI ga yuborish
        ai_input_dict = {}
        text_by_idx = {}
        
        for idx, text in enumerate(unique_texts_map.keys()):
            idx_str = str(idx)
            ai_input_dict[idx_str] = text
            text_by_idx[idx_str] = text

        lang_map = {
            "uz": "Uzbek", "ru": "Russian", "en": "English"
        }
        target_lang_full = lang_map.get(data.target_lang, data.target_lang)

        system_instruction = (
            f"You are an expert bilingual interpreter. Your task is to accurately translate the values of a JSON object into {target_lang_full}. "
            "CONTEXT: The input texts are from an informal chat app. They contain heavy slang, abbreviations, grammatical errors, typos, mixed scripts (like Cyrillic/Latin Uzbek), and EMOJIS.\n\n"
            "CRITICAL RULES:\n"
            f"1. TRANSLATE MEANING: Understand the informal context. Fix typos internally and translate the intended meaning into natural, culturally appropriate {target_lang_full}. (e.g., 'узбекмисан' -> 'Are you Uzbek?', 'zor' -> 'Great').\n"
            "2. EMOJIS (ABSOLUTE): NEVER translate, describe, or touch emojis. Keep them EXACTLY in their original position. If input is '👍', output must be '👍'. Never output words like 'Молчание'.\n"
            f"3. IF ALREADY IN TARGET: If the text is fundamentally already in {target_lang_full}, just correct any typos and keep it in {target_lang_full}.\n"
            f"4. PROPER NAMES: Do NOT translate the meaning of names. DO transliterate them into the {target_lang_full} alphabet (e.g., 'Komilon' -> 'Комилон' in Russian).\n"
            "5. MEANINGLESS: Do not translate absolute gibberish.\n"
            "6. OUTPUT FORMAT: Return ONLY a valid JSON object matching the input keys. No markdown (like ```json), no conversational text.\n\n"
            "EXAMPLE INPUT: {\"0\": \"Salom 🤝\", \"1\": \"узбекмисан 🤐\", \"2\": \"zor 🔥\", \"3\": \"Komilon\"}\n"
            f"EXAMPLE OUTPUT (if target is Russian): {{\"0\": \"Привет 🤝\", \"1\": \"ты узбек 🤐\", \"2\": \"отлично 🔥\", \"3\": \"Комилон\"}}"
        )

        input_json_str = json.dumps(ai_input_dict, ensure_ascii=False)
        
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": input_json_str}
            ],
            model="llama3.1-8b",
            temperature=0.5,
            max_completion_tokens=2048,
            stream=False
        )
        
        raw_response = response.choices[0].message.content.strip()
        
        if raw_response.startswith("```json"):
            raw_response = raw_response[7:]
        if raw_response.endswith("```"):
            raw_response = raw_response[:-3]
        raw_response = raw_response.strip()

        translated_json = json.loads(raw_response)
        
        for idx_str, translated_text in translated_json.items():
            translated_text = translated_text.strip()
            original_txt = text_by_idx.get(idx_str)
            
            if original_txt:
                try:
                    cursor.execute(
                        "INSERT OR IGNORE INTO cache (original_text, target_lang, translated_text) VALUES (?, ?, ?)",
                        (original_txt, data.target_lang, translated_text)
                    )
                except sqlite3.Error:
                    pass
                
                for msg_id in unique_texts_map[original_txt]:
                    final_translations[msg_id] = translated_text
        
        conn.commit()
        conn.close()

        return {"translations": final_translations}
        
    except Exception as e:
        print(f"Batch Tarjima xatosi: {e}")
        return {"error": str(e)}


# ==========================================
# 2. SINGLE API (Bittalab tarjima qilish uchun)
# ==========================================
@app.post("/translate")
def translate(data: TranslateRequest):
    try:
        original_text = data.text.strip()
        
        # HIMOYA: Yakka tarjimada ham faqat emoji bo'lsa qaytarib yuboramiz!
        if not is_valid_for_translation(original_text):
            return {"translated_text": original_text, "is_cached": True}

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT translated_text FROM cache WHERE original_text = ? AND target_lang = ?", 
            (original_text, data.target_lang)
        )
        cached = cursor.fetchone()
        
        if cached:
            conn.close()
            return {"translated_text": cached[0], "is_cached": True}

        lang_map = {
            "uz": "Uzbek", "ru": "Russian", "en": "English"
        }
        target_lang_full = lang_map.get(data.target_lang, data.target_lang)

        system_instruction = (
            f"You are a professional interpreter. Translate the text into {target_lang_full}. "
            "CRITICAL RULES: "
            "1. NEVER translate emojis. Keep them exactly as they are. "
            "2. Transliterate names. "
            "3. Output ONLY the final translated text. No explanations."
        )
        
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": original_text}
            ],
            model="llama3.1-8b",
            temperature=0.3,
            max_completion_tokens=500,
            stream=False
        )
        
        translated_text = response.choices[0].message.content.strip()

        cursor.execute(
            "INSERT OR IGNORE INTO cache (original_text, target_lang, translated_text) VALUES (?, ?, ?)",
            (original_text, data.target_lang, translated_text)
        )
        conn.commit()
        conn.close()

        return {"translated_text": translated_text, "is_cached": False}
        
    except Exception as e:
        print(f"Yakka tarjima xatosi: {e}")
        return {"error": str(e)}