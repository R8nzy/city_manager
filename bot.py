from io import BytesIO

import telebot
from config import TOKEN, DATABASE
from logic import DB_Map

bot = telebot.TeleBot(TOKEN, threaded=False)
manager = DB_Map(DATABASE)
manager.create_user_table()


def get_city(message):
    parts = message.text.split(maxsplit=1)
    return parts[1].strip() if len(parts) > 1 else ""


def send_map(message, cities):
    with BytesIO() as image:
        manager.create_graph(image, cities)
        image.seek(0)
        bot.send_photo(message.chat.id, image)


@bot.message_handler(commands=["start", "help"])
def help_command(message):
    bot.send_message(
        message.chat.id,
        "/show_city London — показать город\n"
        "/remember_city New York — сохранить город\n"
        "/show_my_cities — показать сохранённые города\n"
        "Названия пиши на английском."
    )


@bot.message_handler(commands=["show_city"])
def show_city(message):
    city = get_city(message)

    if not city:
        bot.send_message(message.chat.id, "Напиши: /show_city London")
    elif manager.get_coordinates(city):
        send_map(message, [city])
    else:
        bot.send_message(message.chat.id, "Город не найден.")


@bot.message_handler(commands=["remember_city"])
def remember_city(message):
    city = get_city(message)

    if not city:
        bot.send_message(message.chat.id, "Напиши: /remember_city London")
    elif manager.add_city(message.from_user.id, city):
        bot.send_message(message.chat.id, "Город сохранён!")
    else:
        bot.send_message(message.chat.id, "Город не найден.")


@bot.message_handler(commands=["show_my_cities"])
def show_my_cities(message):
    cities = manager.select_cities(message.from_user.id)

    if cities:
        send_map(message, cities)
    else:
        bot.send_message(message.chat.id, "Сначала сохрани хотя бы один город.")


if __name__ == "__main__":
    bot.infinity_polling()