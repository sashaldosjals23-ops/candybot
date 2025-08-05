import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
from flask import Flask
from threading import Thread

# Инициализация Flask-сервера
app = Flask(__name__)

@app.route('/')
def home():
    return '✅ Bot is running!'

# Функция для запуска Flask в отдельном потоке
def run():
    app.run(host='0.0.0.0', port=8080)

# Telegram Bot
TOKEN = "8369455981:AAGBJJYaKr0rJD24B9YVKip0Bunp2a7hXYE"
bot = telebot.TeleBot(TOKEN)

PRICE_PER_GRAM_USD = 20

products = {
    "МЕФ КРИСТАЛЛ": PRICE_PER_GRAM_USD,
    "БОШКИ": PRICE_PER_GRAM_USD,
    "АМФЕТАМИН": PRICE_PER_GRAM_USD,
    "ЭКСТАЗИ": PRICE_PER_GRAM_USD,
    "ГАШИШ": PRICE_PER_GRAM_USD,
    "КОКАИН": PRICE_PER_GRAM_USD,
}


allowed_cities = [
    "Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург", "Казань",
    "Нижний Новгород", "Челябинск", "Самара", "Омск", "Ростов-на-Дону",
    "Уфа", "Красноярск", "Пермь", "Воронеж", "Волгоград","Магадан" , "Мурманск" ,
    "Киев", "Харьков", "Одесса", "Днепр", "Запорожье", "Львов", "Кривой Рог",
    "Николаев", "Мариуполь", "Луганск",
    "Алматы", "Нур-Султан", "Шымкент", "Караганда", "Актобе", "Тараз",
    "Павлодар", "Усть-Каменогорск", "Семей", "Костанай",
]

user_data = {}

@bot.message_handler(commands=["start"])
def start(message):
    chat_id = message.chat.id
    user_data[chat_id] = {}
    send_city_request(chat_id)

def send_city_request(chat_id):
    markup = InlineKeyboardMarkup(row_width=3)
    for city in allowed_cities[:15]:
        markup.add(InlineKeyboardButton(city, callback_data=f"city_{city}"))
    markup.add(InlineKeyboardButton("Другой город", callback_data="other_city"))
    bot.send_message(chat_id, "Выберите ваш город из списка или напишите его вручную:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("city_") or call.data == "other_city")
def city_callback(call):
    chat_id = call.message.chat.id
    if chat_id not in user_data:
        user_data[chat_id] = {}

    if call.data == "other_city":
        bot.send_message(chat_id, "Введите ваш город вручную:")
        user_data[chat_id]["awaiting_city_input"] = True
        bot.answer_callback_query(call.id)
    else:
        city = call.data[5:]
        if city in allowed_cities:
            user_data[chat_id]["city"] = city
            user_data[chat_id].pop("awaiting_city_input", None)
            bot.edit_message_text(f"Вы выбрали город: *{city}*", chat_id=chat_id, message_id=call.message.message_id, parse_mode="Markdown")
            show_product_menu(chat_id)
            bot.answer_callback_query(call.id)
        else:
            bot.answer_callback_query(call.id, "Город недоступен.", show_alert=True)

@bot.message_handler(func=lambda m: user_data.get(m.chat.id, {}).get("awaiting_city_input", False))
def manual_city_input(message):
    chat_id = message.chat.id
    city = message.text.strip()
    if city in allowed_cities:
        user_data[chat_id]["city"] = city
        user_data[chat_id].pop("awaiting_city_input", None)
        bot.send_message(chat_id, f"Вы выбрали город: *{city}*", parse_mode="Markdown")
        show_product_menu(chat_id)
    else:
        bot.send_message(chat_id, "Извините, мы не работаем в вашем городе.")

def show_product_menu(chat_id):
    markup = InlineKeyboardMarkup(row_width=2)
    for product in products.keys():
        markup.add(InlineKeyboardButton(product, callback_data=f"product_{product}"))
    markup.add(InlineKeyboardButton("🔙 Назад", callback_data="back_to_city"))
    bot.send_message(chat_id, "Выберите товар из каталога:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("product_") or call.data == "back_to_city")
def product_callback(call):
    chat_id = call.message.chat.id
    if call.data == "back_to_city":
        user_data[chat_id].pop("city", None)
        user_data[chat_id].pop("product", None)
        send_city_request(chat_id)
        bot.edit_message_text("Выберите ваш город:", chat_id=chat_id, message_id=call.message.message_id)
        bot.answer_callback_query(call.id)
    else:
        product = call.data[8:]
        user_data[chat_id]["product"] = product
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        photo_path = os.path.join(BASE_DIR, f"{product}.jpg")
        if os.path.exists(photo_path):
            with open(photo_path, "rb") as photo:
                bot.send_photo(chat_id, photo, caption=f"Вы выбрали *{product}*.\nСколько граммов хотите купить?", parse_mode="Markdown")
        else:
            bot.send_message(chat_id, f"Вы выбрали *{product}*.\nСколько граммов хотите купить?", parse_mode="Markdown")
        bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda m: m.text.isdigit() and "product" in user_data.get(m.chat.id, {}))
def quantity_selected(message):
    chat_id = message.chat.id
    grams = int(message.text)
    product = user_data[chat_id]["product"]
    price_usd = grams * products[product]
    price_rub = round(price_usd * 93, 2)
    price_kzt = round(price_usd * 470, 2)

    text = send_order_message(chat_id, product, grams, price_usd, price_rub, price_kzt)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📩 Связаться с оператором", url="https://t.me/operatortgbot"))
    bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=markup)

def send_order_message(chat_id, product, grams, price_usd, price_rub, price_kzt):
    city = user_data.get(chat_id, {}).get("city", "не указан")
    return f"""🧾 *Детали заказа:*
📦 Товар: *{product}*
🏙 Город: *{city}*
⚖ Кол-во: *{grams} г*
💵 К оплате: *{price_usd}$* / *{price_rub}₽* / *{price_kzt}₸*

💸 Переведите сумму на кошелек:
TYF1hRDfrwXtW5qXcoffWxYbxecwaLjTph
(USDT / TRC20)

После оплаты нажмите кнопку ниже для связи с оператором."""

# --- ЗАПУСК ВСЕГО ---
if __name__ == "__main__":
    Thread(target=run).start()
    bot.infinity_polling()
