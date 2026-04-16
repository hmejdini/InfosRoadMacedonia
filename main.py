import telebot
from telebot import types
from flask import Flask
from threading import Thread
import os

# --- 1. KONFIGURIMI I SERVERIT (Për Render) ---
app = Flask('')

@app.route('/')
def home():
    return "Infos Road Macedonia Monitor is LIVE!"

def run():
    # Render përdor portën 8080 si default nëse nuk specifikohet
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 2. KONFIGURIMI I BOTIT ---
TOKEN = "8630635624:AAFZzSrxEP9Vs5WjCSf6NgSQ2MrlYfIujWw"
CHANNEL_ID = "-1003803179344"
ADMIN_ID = "7888974036"  # ID-ja jote që more nga bot-i

bot = telebot.TeleBot(TOKEN)

# Komanda /start
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "👋 Mirësevini në Infos Roads Macedonia!\n\nDërgoni informacionin tuaj këtu dhe ai do të publikohet automatikisht në kanal.")

# Trajtimi i mesazheve (Tekst, Foto, Video)
@bot.message_handler(content_types=['text', 'photo', 'video'])
def handle_auto_post(message):
    # A) PUBLIKIMI AUTOMATIK NË KANAL (ANONIM)
    try:
        if message.content_type == 'text':
            bot.send_message(CHANNEL_ID, message.text)
        elif message.content_type == 'photo':
            bot.send_photo(CHANNEL_ID, message.photo[-1].file_id, caption=message.caption)
        elif message.content_type == 'video':
            bot.send_video(CHANNEL_ID, message.video.file_id, caption=message.caption)
        
        # Konfirmimi për përdoruesin që dërgoi mesazhin
        bot.reply_to(message, "✅ Lajmi u publikua me sukses në kanal!")
        
    except Exception as e:
        # Njofto adminin nëse boti nuk është Admin në kanal
        bot.send_message(ADMIN_ID, f"❌ Gabim gjatë postimit në kanal: {e}\nSigurohu që boti ka leje dërgimi.")

    # B) NJOFTIMI PRIVAT PËR ADMININ (TI)
    # Kjo dërgohet vetëm nëse dërguesi nuk është vetë Admini
    if str(message.chat.id) != ADMIN_ID:
        user = message.from_user
        info_tekst = (
            f"🔔 **Njoftim i ri!**\n\n"
            f"👤 **Dërguesi:** {user.first_name} {user.last_name or ''}\n"
            f"🔗 **Username:** @{user.username or 'nuk_ka'}\n"
            f"🆔 **ID:** {user.id}\n\n"
            f"Sapo u dërgua një postim automatik në kanal."
        )
        
        bot.send_message(ADMIN_ID, info_tekst, parse_mode="Markdown")

# --- 3. NISJA E PROGRAMIT ---
if __name__ == "__main__":
    keep_alive()  # Mban serverin ndezur
    print("Boti po punon...")
    bot.infinity_polling()
