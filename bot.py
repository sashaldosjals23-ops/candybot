import os
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "7233728575:AAGdw-h-JM70nBYTBhJCeedCvmx740yKubw"
bot = telebot.TeleBot(TOKEN)

products = {
    "МЕФ КРИСТАЛЛ": 15,
    "БОШКИ": 15,
    "АМФЕТАМИН": 15,
    "ЭКСТАЗИ": 15,
    "ГАШИШ": 15,
    "КОКАИН": 15,
}

cities = [
    "Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург", "Казань",
    "Нижний Новгород", "Челябинск", "Омск", "Самара", "Ростов-на-Дону",
    "Уфа", "Красноярск", "Пермь", "Воронеж", "Волгоград",
    "Алматы", "Астана", "Шымкент", "Караганда", "Актобе"
]

user_data = {}

@bot.message_handler(commands=["start"])
def start(message):
    user_data[message.chat.id] = {}
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(*[KeyboardButton(city) for city in cities[:5]])
    bot.send_message(message.chat.id, "Выберите ваш город:", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text in cities)
def city_selected(message):
    user_data[message.chat.id]["city"] = message.text
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(*[KeyboardButton(prod) for prod in products.keys()])
    bot.send_message(message.chat.id, "Выберите товар из каталога:", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text.upper() in products)
def product_selected(message):
    product = message.text.upper()
    user_data[message.chat.id]["product"] = product
    bot.send_message(message.chat.id, f"Вы выбрали {product}. Сколько граммов хотите купить?")

@bot.message_handler(func=lambda msg: msg.text.isdigit())
def quantity_selected(message):
    grams = int(message.text)
    chat_id = message.chat.id
    product = user_data[chat_id].get("product")
    if not product:
        bot.send_message(chat_id, "Сначала выберите товар.")
        return
    price_usd = grams * products[product]
    price_rub = round(price_usd * 93, 2)
    price_kzt = round(price_usd * 470, 2)

   text = f"""🧾 *Детали заказа:*
📦 Товар: *{product}*
⚖ Кол-во: *{grams}г*
💵 К оплате: *{price_usd}$* / *{price_rub}₽* / *{price_kzt}₸*

💸 Переведите сумму на кошелек:
`TYF1hRDfrwXtW5qXcoffWxYbxecwaLjTph`
(USDT / TRC20)

После оплаты нажмите кнопку ниже для связи с оператором."""


    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📩 Связаться с оператором", url="https://t.me/biznesimotiv"))

    bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=markup)

bot.polling()
