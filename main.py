import telebot
from telebot import types
from flask import Flask
from threading import Thread
import os

# --- 1. SERVERI PËR RENDER (Për ta mbajtur botin ndezur) ---
app = Flask('')
@app.route('/')
def home(): return "Boti Infos Road Macedonia është Live!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    Thread(target=run).start()

# --- 2. KONFIGURIMI I BOTIT ---
TOKEN = "8630635624:AAFZzSrxEP9Vs5WjCSf6NgSQ2MrlYfIujWw"
CHANNEL_ID = "-1003803179344"
ADMIN_ID = "7888974036" # ID-ja jote (SMOKI)

bot = telebot.TeleBot(TOKEN)
user_data = {}

# Komanda /start
@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, "👋 Mirësevini në Infos Roads Macedonia!\n\nDërgoni lajmin tuaj këtu.", reply_markup=markup)

# Trajtimi i mesazheve (Tekst, Foto, Video)
@bot.message_handler(content_types=['text', 'photo', 'video'])
def handle_incoming_message(message):
    # MOS e konsidero tekstin e butonave si raportim të ri
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
                       f"🆔 **ID:** {user.id}")
        bot.send_message(ADMIN_ID, info_header, parse_mode="Markdown")

    # SHFAQJA E BUTONAVE (STILI I PASTËR PA REPLY)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("Po, posto-je ✅"))
    markup.add(types.KeyboardButton("Jo, kam bërë një gabim ❌"))
    
    if message.content_type == 'text':
        # Formati: Postimi juaj 'teksti'...
        teksti_konfirmimit = f"Postimi juaj\n'{message.text}'\n\nA dëshironi ta publikoni këtë postim në kanal?"
        bot.send_message(user_id, teksti_konfirmimit, reply_markup=markup)
    else:
        bot.send_message(user_id, "Materiali juaj u mor. A dëshironi ta publikoni këtë në kanal?", reply_markup=markup)

# Trajtimi i klikimit të butonave
@bot.message_handler(func=lambda message: message.text in ["Po, posto-je ✅", "Jo, kam bërë një gabim ❌"])
def process_confirmation(message):
    user_id = message.chat.id
    original_msg = user_data.get(user_id)
    
    # Kjo komandë siguron që butonat të hiqen nga ekrani
    remove_markup = types.ReplyKeyboardRemove()

    if not original_msg:
        bot.send_message(user_id, "Ju lutem dërgoni lajmin përsëri.", reply_markup=remove_markup)
        return

    if message.text == "Po, posto-je ✅":
        try:
            # POSTIMI I MATERIALIT ORIGJINAL NË KANAL
            if original_msg.content_type == 'text':
                bot.send_message(CHANNEL_ID, original_msg.text)
            elif original_msg.content_type == 'photo':
                bot.send_photo(CHANNEL_ID, original_msg.photo[-1].file_id, caption=original_msg.caption)
            elif original_msg.content_type == 'video':
                bot.send_video(CHANNEL_ID, original_msg.video.file_id, caption=original_msg.caption)
            
            bot.send_message(user_id, "✅ Lajmi u publikua me sukses në kanal!", reply_markup=remove_markup)
            bot.send_message(ADMIN_ID, "🟢 Ky mesazh u publikua në kanal.")
        except Exception as e:
            bot.send_message(user_id, "❌ Gabim gjatë postimit.", reply_markup=remove_markup)
    else:
        bot.send_message(user_id, "❌ Postimi u anulua.", reply_markup=remove_markup)
        bot.send_message(ADMIN_ID, "🔴 Ky mesazh u anulua nga përdoruesi.")

    # Pastrojmë kujtesën
    if user_id in user_data:
        del user_data[user_id]

# --- 3. NISJA ---
if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
