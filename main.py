import telebot
from telebot import types
from flask import Flask
from threading import Thread
import os

# --- 1. SERVERI PËR RENDER ---
app = Flask('')
@app.route('/')
def home(): return "Boti Infos Road Macedonia është LIVE!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    Thread(target=run).start()

# --- 2. KONFIGURIMI I BOTIT ---
TOKEN = "8630635624:AAFZzSrxEP9Vs5WjCSf6NgSQ2MrlYfIujWw"
CHANNEL_ID = "-1003803179344" 
ADMIN_ID = "7888974036"

bot = telebot.TeleBot(TOKEN)
user_data = {}

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, "👋 Mirësevini! Dërgoni raportimin tuaj këtu.", reply_markup=types.ReplyKeyboardRemove())

# --- 3. TRAJTIMI I BUTONAVE (KJO DUHET TË JETË E PARA) ---
@bot.message_handler(func=lambda message: message.text in ["Po, posto-je ✅", "Jo, kam bërë një gabim ❌"])
def handle_confirmation(message):
    user_id = message.chat.id
    original_msg = user_data.get(user_id)
    
    if not original_msg:
        bot.send_message(user_id, "Nuk kam asgjë për të postuar. Dërgoni një lajm të ri.", reply_markup=types.ReplyKeyboardRemove())
        return

    if message.text == "Po, posto-je ✅":
        try:
            # Postimi automatik në kanal
            if original_msg.content_type == 'text':
                bot.send_message(CHANNEL_ID, original_msg.text)
            elif original_msg.content_type == 'photo':
                bot.send_photo(CHANNEL_ID, original_msg.photo[-1].file_id, caption=original_msg.caption)
            elif original_msg.content_type == 'video':
                bot.send_video(CHANNEL_ID, original_msg.video.file_id, caption=original_msg.caption)
            
            bot.send_message(user_id, "✅ Lajmi u publikua me sukses në kanal!", reply_markup=types.ReplyKeyboardRemove())
            bot.send_message(ADMIN_ID, "🟢 Sukses: Një mesazh u publikua në kanal.")
        except Exception as e:
            bot.send_message(ADMIN_ID, f"⚠️ Gabim gjatë postimit: {e}")
            bot.send_message(user_id, "❌ Gabim teknik. Provoni përsëri.", reply_markup=types.ReplyKeyboardRemove())
    else:
        bot.send_message(user_id, "❌ Postimi u anulua.", reply_markup=types.ReplyKeyboardRemove())

    # Fshijmë të dhënat pas veprimit
    user_data.pop(user_id, None)

# --- 4. MARRJA E RAPORTIMEVE (TEKST, FOTO, VIDEO) ---
@bot.message_handler(content_types=['text', 'photo', 'video'])
def collect_report(message):
    user_id = message.chat.id
    
    # Kjo parandalon loop-in që pe në foto
    if message.text in ["Po, posto-je ✅", "Jo, kam bërë një gabim ❌"]:
        return

    user_data[user_id] = message
    
    # Njoftimi për Adminin (Ti)
    if str(user_id) != ADMIN_ID:
        user = message.from_user
        bot.send_message(ADMIN_ID, f"📩 Tentativë nga: {user.first_name} (@{user.username or 'nuk_ka'})")
        
        # Ti sheh çfarë po dërgohet
        if message.content_type == 'text':
            bot.send_message(ADMIN_ID, f"Përmbajtja: {message.text}")
        elif message.content_type == 'photo':
            bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=message.caption)

    # Pyetja për përdoruesin
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Po, posto-je ✅", "Jo, kam bërë një gabim ❌")
    
    bot.send_message(user_id, "A dëshironi ta publikoni këtë në kanal?", reply_markup=markup)

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
