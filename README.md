🌐 Real-Time AI Translation Chat (Optimized)
Ushbu loyiha ikki foydalanuvchi o'rtasida real vaqt rejimida ishlaydigan, avtomatik va aqlli tarjima qilinadigan chat tizimidir. Tizim Cerebras AI (Llama 3.1) yordamida nihoyatda tez ishlaydi va SQLite kesh tizimi orqali API xarajatlarini tejaydi.

🏗️ Arxitektura va Optimizatsiya
Tizim uchta asosiy qismdan iborat:

Backend (Node.js + Socket.io): WebSocket orqali xabarlarni real vaqtda yetkazadi.

Translation Service (Python + FastAPI):

Batch Processing: Xabarlarni 30 talab paketlab tarjima qiladi.

Intelligent Cache: Avval tarjima qilingan matnlarni SQLite bazasidan oladi.

Context Aware: Slang, grammatik xatolar va ismlarni (transliteratsiya) tushunadi.

Frontend (React): IntersectionObserver yordamida foydalanuvchi ko'rayotgan xabarlarni birinchi navbatda tarjima qiladi.

Фрагмент кода
graph TD
    A[React Frontend] <-->|WebSocket| B(Node.js Server)
    B <-->|HTTP POST /batch| D[Python AI Service]
    D <-->|Cache Check| E[(SQLite DB)]
    D <-->|Fast Inference| F[Cerebras AI / Llama 3.1]
🚀 Tezkor Ishga Tushirish (Automation)
Loyihani ishga tushirish uchun endi har bir papkaga kirib yurish shart emas. Biz maxsus Python Runner yaratdik.

Talablar
Node.js (v18+)

Python (v3.10+)

Cerebras API Key

1-qadam: Sozlamalar
python-translate papkasi ichida .env faylini yarating:

Фрагмент кода
CEREBRAS_API_KEY=csk-sizning-api-kalitingiz
2-qadam: Birgina buyruq bilan ishga tushirish ⚡
Loyihaning asosiy papkasida (root) terminalni oching va quyidagilarni bajaring:

Bash
# Faqat birinchi marta (Kutubxonalarni o'rnatish va ishga tushirish uchun):
python python-translate/run.py
Ushbu script virtual muhitni yaratadi, barcha kutubxonalarni o'rnatadi va ikkala serverni (Backend & Frontend) alohida terminallarda ochib beradi.

🛠️ Texnologiyalar
Frontend: React.js, Tailwind CSS

Backend: Node.js, Socket.io

AI Engine: Python (FastAPI), Cerebras SDK, Llama 3.1-8B

Database: SQLite (Kesh uchun)

✨ Aqlli Funksiyalar
Emoji Protection: Emojilar tarjima qilinmaydi va o'z joyida qoladi.

Name Transliteration: Ismlar tarjima qilinmaydi, lekin maqsadli til alifbosiga o'giriladi (masalan: Komilon -> Комилон).

Slang Support: Chatdagi norasmiy so'zlar (nima gap, uzbekmisiz, sps) ma'nosi bo'yicha tarjima qilinadi.

Infinite Scroll Prefetch: Foydalanuvchi tepaga skroll qilishidan oldin, fon rejimida eski xabarlar 30 tadan paketlab tarjima qilib qo'yiladi.

📝 Eslatma
Agar tarjima bazada noto'g'ri saqlanib qolgan bo'lsa, python-translate/translations_cache.db faylini o'chirib yuboring va serverni qayta yoqing. Tizim avtomatik ravishda toza bazani yaratadi.