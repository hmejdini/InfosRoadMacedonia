import telebot
from telebot import types
from flask import Flask
from threading import Thread
import os

# 1. KONFIGURIMI I SERVERIT
app = Flask('')

@app.route('/')
def home():
    return "Infos Road Macedonia is LIVE!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. KONFIGURIMI I BOTIT
TOKEN = "8630635624:AAFZzSrxEP9Vs5WjCSf6NgSQ2MrlYfIujWw"
CHANNEL_ID = "-1003803179344"

bot = telebot.TeleBot(TOKEN)
user_data = {}

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "👋 Mirësevini në Infos Roads Macedonia!\n\nDërgoni lajmin tuaj këtu. Informacioni do të postohet në kanal si anonim, por administratori do të njoftohet për dërguesit.")

@bot.message_handler(content_types=['text', 'photo', 'video'])
def ask_confirmation(message):
    user_data[message.chat.id] = message
    
    # Marrim të dhënat e dërguesit (për adminin)
    emri = message.from_user.first_name if message.from_user.first_name else "Pa emër"
    mbiemri = message.from_user.last_name if message.from_user.last_name else ""
    username = f"(@{message.from_user.username})" if message.from_user.username else "(Nuk ka username)"
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("Po, posto-je ✅", callback_data="yes"),
        types.InlineKeyboardButton("Jo, anuloje ❌", callback_data="no")
    )
    
    # Ky mesazh të vjen VETËM ty (dërguesit) për konfirmim
    teksti_admin = f"👤 **Dërguesi:** {emri} {mbiemri} {username}\n\n📢 A dëshironi ta publikoni këtë në kanal si anonim?"
    bot.reply_to(message, teksti_admin, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "yes":
        msg = user_data.get(call.message.chat.id)
        if msg:
            try:
                # Postimi në kanal bëhet plotësisht anonim
                if msg.content_type == 'text':
                    bot.send_message(CHANNEL_ID, msg.text)
                elif msg.content_type == 'photo':
                    bot.send_photo(CHANNEL_ID, msg.photo[-1].file_id, caption=msg.caption)
                elif msg.content_type == 'video':
                    bot.send_video(CHANNEL_ID, msg.video.file_id, caption=msg.caption)
                
                bot.edit_message_text("✅ Lajmi u postua si anonim në kanal!", call.message.chat.id, call.message.message_id)
            except Exception as e:
                bot.edit_message_text(f"❌ Gabim: Sigurohu që boti është Admin në kanal.", call.message.chat.id, call.message.message_id)
    
    elif call.data == "no":
        bot.edit_message_text("❌ Postimi u anulua.", call.message.chat.id, call.message.message_id)

# 3. NISJA
if __name__ == "__main__":
    keep_alive()
    print("Boti po punon...")
    bot.infinity_polling()
