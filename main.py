import telebot
from telebot import types
from flask import Flask
from threading import Thread
import os

# --- 1. SERVERI PËR RENDER (Që boti të qëndrojë online) ---
app = Flask('')

@app.route('/')
def home():
    return "Infos Road Macedonia Monitor is LIVE!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 2. KONFIGURIMI I BOTIT ---
TOKEN = "8630635624:AAFZzSrxEP9Vs5WjCSf6NgSQ2MrlYfIujWw"
CHANNEL_ID = "-1003803179344"
ADMIN_ID = "7888974036"  # ID-ja jote për njoftime të menjëhershme

bot = telebot.TeleBot(TOKEN)
user_data = {}

# Komanda /start
@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.ReplyKeyboardRemove()
    bot.reply_to(message, "👋 Mirësevini në Infos Roads Macedonia!\n\nDërgoni informacionin tuaj (tekst, foto ose video) këtu.", reply_markup=markup)

# Trajtimi i mesazheve fillestare
@bot.message_handler(content_types=['text', 'photo', 'video'])
def handle_incoming_message(message):
    user_id = message.chat.id
    user_data[user_id] = message
    
    # 1. NJOFTIMI I MENJËHERSHËM PËR ADMININ
    # Ti njoftohesh sapo vjen mesazhi, pa pritur butonat
    if str(user_id) != ADMIN_ID:
        user = message.from_user
        admin_info = (f"📩 **Mesazh i ri në bot!**\n\n"
                      f"👤 **Nga:** {user.first_name} {user.last_name or ''}\n"
                      f"🔗 **Username:** @{user.username or 'nuk_ka'}\n"
                      f"🆔 **ID:** {user.id}\n\n"
                      f"Përdoruesi sapo dërgoi materialin dhe po sheh butonat.")
        bot.send_message(ADMIN_ID, admin_info, parse_mode="Markdown")

    # 2. SHFAQJA E BUTONAVE PËR PËRDORUESIN
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("Po, posto-je ✅"))
    markup.add(types.KeyboardButton("Jo, kam bërë një gabim ❌"))
    
    bot.reply_to(message, "📢 A dëshironi ta publikoni këtë postim në kanal?", reply_markup=markup)

# Trajtimi i shtypjes së butonave nga përdoruesi
@bot.message_handler(func=lambda message: message.text in ["Po, posto-je ✅", "Jo, kam bërë një gabim ❌"])
def process_confirmation(message):
    user_id = message.chat.id
    original_msg = user_data.get(user_id)
    remove_markup = types.ReplyKeyboardRemove()

    if not original_msg:
        bot.send_message(user_id, "Ju lutem dërgoni lajmin përsëri.", reply_markup=remove_markup)
        return

    if message.text == "Po, posto-je ✅":
        try:
            # Postimi në Kanal (Anonim)
            if original_msg.content_type == 'text':
                bot.send_message(CHANNEL_ID, original_msg.text)
            elif original_msg.content_type == 'photo':
                bot.send_photo(CHANNEL_ID, original_msg.photo[-1].file_id, caption=original_msg.caption)
            elif original_msg.content_type == 'video':
                bot.send_video(CHANNEL_ID, original_msg.video.file_id, caption=original_msg.caption)
            
            bot.send_message(user_id, "✅ Postimi u dërgua me sukses në kanal!", reply_markup=remove_markup)
        except Exception as e:
            bot.send_message(user_id, "❌ Ndodhi një gabim gjatë postimit.", reply_markup=remove_markup)
    else:
        bot.send_message(user_id, "❌ Postimi u anulua.", reply_markup=remove_markup)

    # Pastrojmë kujtesën e mesazhit
    if user_id in user_data:
        del user_data[user_id]

# --- 3. NISJA ---
if __name__ == "__main__":
    keep_alive()
    print("Boti po punon...")
    bot.infinity_polling()
