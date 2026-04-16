import telebot
from telebot import types
from flask import Flask
from threading import Thread
import os

# --- SERVERI ---
app = Flask('')
@app.route('/')
def home():
    return "InfosRoadMacedonia is LIVE!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- BOTI ---
TOKEN = "7884841743:AAH_Q8D9zY5vS1v7G0S2p7M9W3k0X7v8b4k"
CHANNEL_ID = "-1003803179344"
bot = telebot.TeleBot(TOKEN)
user_data = {}

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "👋 Mirësevini! Dërgoni lajmin tuaj (tekst, foto ose video) këtu.")

@bot.message_handler(content_types=['text', 'photo', 'video'])
def ask_confirmation(message):
    user_data[message.chat.id] = message
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("Po, posto-je ✅", callback_data="yes"),
        types.InlineKeyboardButton("Jo, anuloje ❌", callback_data="no")
    )
    bot.reply_to(message, "A dëshironi ta publikoni këtë postim në kanal?", reply_markup=markup)

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
                bot.edit_message_text("✅ Lajmi u postua me sukses!", call.message.chat.id, call.message.message_id)
            except:
                bot.answer_callback_query(call.id, "Gabim! Sigurohu që boti është Admin.")
    elif call.data == "no":
        bot.edit_message_text("❌ Postimi u anulua.", call.message.chat.id, call.message.message_id)

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
