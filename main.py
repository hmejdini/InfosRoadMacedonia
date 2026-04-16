import telebot
from telebot import types
from flask import Flask
from threading import Thread
import os

# --- 1. SERVERI PËR RENDER (Që boti të mos fiket) ---
app = Flask('')

@app.route('/')
def home():
    return "Boti Infos Road Macedonia është LIVE!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 2. KONFIGURIMI I BOTIT ---
TOKEN = "8630635624:AAFZzSrxEP9Vs5WjCSf6NgSQ2MrlYfIujWw"
CHANNEL_USERNAME = "@NewsInfosRoadsMacedonia"
ADMIN_ID = "7888974036" # ID-ja jote

bot = telebot.TeleBot(TOKEN)
user_data = {}

# Komanda /start
@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, "👋 Mirësevini në Infos Roads Macedonia!\n\nDërgoni lajmin tuaj këtu.", reply_markup=markup)

# Trajtimi i mesazheve hyrëse
@bot.message_handler(content_types=['text', 'photo', 'video'])
def handle_incoming_message(message):
    # Injoro tekstin e butonave që të mos krijohet lësh
    if message.text in ["Po, posto-je ✅", "Jo, kam bërë një gabim ❌"]:
        return

    user_id = message.chat.id
    user_data[user_id] = message
    
    # NJOFTIMI I MENJËHERSHËM PËR ADMININ (TI)
    if str(user_id) != ADMIN_ID:
        user = message.from_user
        info_header = (f"📩 **Tentativë e re postimi!**\n\n"
                       f"👤 **Nga:** {user.first_name} {user.last_name or ''}\n"
                       f"🔗 **Username:** @{user.username or 'nuk_ka'}\n"
                       f"🆔 **ID:** {user.id}\n"
                       f"👇 **Materiali që po dërgon:**")
        
        bot.send_message(ADMIN_ID, info_header, parse_mode="Markdown")
        
        # Ti si admin sheh përmbajtjen që po dërgohet
        if message.content_type == 'text':
            bot.send_message(ADMIN_ID, f"📝 **Teksti:**\n{message.text}")
        elif message.content_type == 'photo':
            bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=f"🖼 **Foto:**\n{message.caption or ''}")
        elif message.content_type == 'video':
            bot.send_video(ADMIN_ID, message.video.file_id, caption=f"🎥 **Video:**\n{message.caption or ''}")

    # SHFAQJA E BUTONAVE PËR PËRDORUESIN
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("Po, posto-je ✅"))
    markup.add(types.KeyboardButton("Jo, kam bërë një gabim ❌"))
    
    if message.content_type == 'text':
        teksti_konfirmimit = f"Postimi juaj\n'{message.text}'\n\nA dëshironi ta publikoni këtë postim në kanal?"
        bot.send_message(user_id, teksti_konfirmimit, reply_markup=markup)
    else:
        bot.send_message(user_id, "Materiali juaj u mor. A dëshironi ta publikoni këtë në kanal?", reply_markup=markup)

# Trajtimi i klikimit të butonave (Postimi Auto në Kanal)
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
            # POSTIMI AUTOMATIK NË KANAL
            if original_msg.content_type == 'text':
                bot.send_message(CHANNEL_USERNAME, original_msg.text)
            elif original_msg.content_type == 'photo':
                bot.send_photo(CHANNEL_USERNAME, original_msg.photo[-1].file_id, caption=original_msg.caption)
            elif original_msg.content_type == 'video':
                bot.send_video(CHANNEL_USERNAME, original_msg.video.file_id, caption=original_msg.caption)
            
            bot.send_message(user_id, "✅ Lajmi u publikua me sukses në kanal!", reply_markup=remove_markup)
            bot.send_message(ADMIN_ID, f"🟢 U publikua në {CHANNEL_USERNAME}")
        except Exception as e:
            bot.send_message(user_id, "❌ Gabim: Sigurohu që boti është Admin në kanal.", reply_markup=remove_markup)
    else:
        bot.send_message(user_id, "❌ Postimi u anulua.", reply_markup=remove_markup)
        bot.send_message(ADMIN_ID, "🔴 Përdoruesi e anuloi postimin.")

    # Pastrojmë memorien
    if user_id in user_data:
        del user_data[user_id]

# --- 3. NISJA ---
if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
