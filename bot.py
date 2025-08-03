import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "7233728575:AAGdw-h-JM70nBYTBhJCeedCvmx740yKubw"
bot = telebot.TeleBot(TOKEN)

PRICE_PER_GRAM_USD = 20  # Цена 20$ за грамм

products = {
    "МЕФ КРИСТАЛЛ": PRICE_PER_GRAM_USD,
    "БОШКИ": PRICE_PER_GRAM_USD,
    "АМФЕТАМИН": PRICE_PER_GRAM_USD,
    "ЭКСТАЗИ": PRICE_PER_GRAM_USD,
    "ГАШИШ": PRICE_PER_GRAM_USD,
    "КОКАИН": PRICE_PER_GRAM_USD,
}

user_data = {}

@bot.message_handler(commands=["start"])
def start(message):
    chat_id = message.chat.id
    user_data[chat_id] = {}
    bot.send_message(chat_id, "Введите ваш город:")

@bot.message_handler(func=lambda msg: "city" not in user_data.get(msg.chat.id, {}))
def handle_city(message):
    chat_id = message.chat.id
    user_data[chat_id]["city"] = message.text
    show_product_menu(chat_id)

def show_product_menu(chat_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for product in products.keys():
        markup.add(KeyboardButton(product))
    markup.add(KeyboardButton("🔙 Назад"))
    bot.send_message(chat_id, "Выберите товар из каталога:", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "🔙 Назад")
def go_back(message):
    chat_id = message.chat.id
    user_data[chat_id].pop("product", None)
    user_data[chat_id].pop("city", None)
    bot.send_message(chat_id, "Введите ваш город заново:")

@bot.message_handler(func=lambda msg: msg.text in products)
def product_selected(message):
    chat_id = message.chat.id
    product = message.text
    user_data[chat_id]["product"] = product
    bot.send_message(chat_id, f"Вы выбрали *{product}*.\nСколько граммов хотите купить?", parse_mode="Markdown")

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

    text = send_order_message(product, grams, price_usd, price_rub, price_kzt)

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📩 Связаться с оператором", url="https://t.me/biznesimotiv"))
    bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=markup)

def send_order_message(product, grams, price_usd, price_rub, price_kzt):
    return f"""🧾 *Детали заказа:*
📦 Товар: *{product}*
🏙 Город: *введён вручную*
⚖ Кол-во: *{grams} г*
💵 К оплате: *{price_usd}$* / *{price_rub}₽* / *{price_kzt}₸*

💸 Переведите сумму на кошелек:
`TYF1hRDfrwXtW5qXcoffWxYbxecwaLjTph`
(USDT / TRC20)

После оплаты нажмите кнопку ниже для связи с оператором."""

bot.polling()
