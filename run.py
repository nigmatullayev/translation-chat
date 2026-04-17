import subprocess
import time
import sys
import os

# --- SOZLAMALAR ---
PYTHON_TRANSLATE_DIR = "python-translate"
VENV_PATH = os.path.join(PYTHON_TRANSLATE_DIR, "venv")
REQS = ["fastapi", "uvicorn", "python-dotenv", "cerebras-cloud-sdk", "emoji"]

def run_command(command, cwd=None):
    """Buyruqni yangi terminal oynasida ishga tushirish"""
    if sys.platform == "win32":
        # Windows uchun yangi CMD oynasida ochish
        return subprocess.Popen(["start", "cmd", "/k", command], cwd=cwd, shell=True)
    else:
        # Linux/Mac uchun (Terminalga qarab o'zgarishi mumkin)
        return subprocess.Popen(["x-terminal-emulator", "-e", command], cwd=cwd)

def setup_python():
    print(">>> Python muhitini tekshirish...")
    
    # venv borligini tekshirish
    if not os.path.exists(VENV_PATH):
        print(">>> Virtual muhit topilmadi. Yaratilmoqda...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], cwd=PYTHON_TRANSLATE_DIR)

    # Kutubxonalarni o'rnatish
    print(">>> Kutubxonalarni yangilash...")
    pip_path = os.path.join(VENV_PATH, "Scripts", "pip") if sys.platform == "win32" else os.path.join(VENV_PATH, "bin", "pip")
    subprocess.run([pip_path, "install"] + REQS, cwd=PYTHON_TRANSLATE_DIR)

def main():
    print("="*30)
    print(" UZWORK TRANSLATION PROJECT ")
    print("="*30)

    # 1. Python sozlash
    try:
        setup_python()
    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")
        return

    # 2. Backendni ishga tushirish
    print(">>> Backend ishga tushirilmoqda (Port 8080)...")
    backend_cmd = "venv\\Scripts\\activate && uvicorn translate_service:app --reload --port 8080"
    run_command(backend_cmd, cwd=PYTHON_TRANSLATE_DIR)

    time.sleep(2) # Kichik tanaffus

    # 3. React Frontendni ishga tushirish
    print(">>> Frontend ishga tushirilmoqda...")
    if os.path.exists("package.json"):
        run_command("npm start")
    else:
        print("!!! package.json topilmadi, frontend yoqilmadi.")

    print("\n✅ Hammasi tayyor! Terminallarni kuzatib boring.")
    print("Dasturni to'xtatish uchun terminallarni yopishingiz mumkin.")

if __name__ == "__main__":
    main()