import telebot
from telebot import types
from flask import Flask
from threading import Thread
import os

# 1. KONFIGURIMI I SERVERIT (Që Render mos ta fikë botin)
app = Flask('')

@app.route('/')
def home():
    return "Infos Road Macedonia is LIVE!"

def run():
    # Render kërkon një portë aktive, përdorim 8080 si default
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. KONFIGURIMI I BOTIT
# Token-i yt i ri
TOKEN = "8630635624:AAFZzSrxEP9Vs5WjCSf6NgSQ2MrlYfIujWw"
# ID e kanalit tënd
CHANNEL_ID = "-1003803179344"

bot = telebot.TeleBot(TOKEN)
user_data = {}

# Komanda /start
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "👋 Mirësevini në Infos Roads Macedonia!\n\nDërgoni lajmin tuaj (tekst, foto ose video) dhe unë do t'ju pyes nëse doni ta publikoni.")

# Trajtimi i mesazheve (Tekst, Foto, Video)
@bot.message_handler(content_types=['text', 'photo', 'video'])
def ask_confirmation(message):
    # Ruajmë mesazhin përkohësisht që ta dimë çfarë do publikojmë
    user_data[message.chat.id] = message
    
    # Krijojmë butonat Po/Jo
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("Po, posto-je ✅", callback_data="yes"),
        types.InlineKeyboardButton("Jo, anuloje ❌", callback_data="no")
    )
    bot.reply_to(message, "📢 A dëshironi ta publikoni këtë postim në kanal?", reply_markup=markup)

# Trajtimi i shtypjes së butonave
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "yes":
        msg = user_data.get(call.message.chat.id)
        if msg:
            try:
                if msg.content_type == 'text':
                    bot.send_message(CHANNEL_ID, msg.text)
                elif msg.content_type == 'photo':
                    bot.send_photo(CHANNEL_ID, msg.photo[-1].file_id, caption=msg.caption)
                elif msg.content_type == 'video':
                    bot.send_video(CHANNEL_ID, msg.video.file_id, caption=msg.caption)
                
                bot.edit_message_text("✅ U postua me sukses në kanal!", call.message.chat.id, call.message.message_id)
            except Exception as e:
                bot.edit_message_text(f"❌ Gabim: Sigurohu që boti është Admin në kanal.", call.message.chat.id, call.message.message_id)
    
    elif call.data == "no":
        bot.edit_message_text("❌ Postimi u anulua.", call.message.chat.id, call.message.message_id)

# 3. NISJA E PROGRAMIT
if __name__ == "__main__":
    keep_alive() # Nis serverin Flask në sfond
    print("Boti po punon...")
    bot.infinity_polling()
