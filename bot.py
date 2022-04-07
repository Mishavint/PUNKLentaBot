#!/usr/bin/python3
import logging
from config import TOKEN

from telegram import *
from telegram.ext import *

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


### Texts ###
def text_for_start(name):
    return f"""
Приветствую, {name}. Я чат-бот для поиска людей в ленте. Я был создан студентом Пунка для студентов Пунка

На данный момент это MVP(Minimal Viable Product). Так что доступна всего 1 команда:

/menu - главное меню, с помощью него можно найти человека или помочь кому-то

Будьте людьми, заранее договаривайтесь про вознаграждение 🦉
"""


def text_for_help():
    return """
Бот создан @mishavint. Со всеми вопросами и пожеланиями писать ему (Умоляю не ночью).    

На данный момент это MVP(Minimal Viable Product). Так что доступна всего 1 команда:

/menu - главное меню, с помощью него можно найти человека или помочь кому-то

Готов помочь - используйте эту кнопку, если вы в Ленте и не хотите помочь кому-то

Ищу помощь - используйте эту кнопку, если вы в Пунке и ищите человека в Ленте

Будьте людьми, заранее договаривайтесь про вознаграждение 🦉
"""


######### start help commands #########
def start_command(update: Update, context: CallbackContext):
    name = update.message.chat.first_name
    update.message.reply_text(text_for_start(name))


def help_command(update: Update, context: CallbackContext):
    update.message.reply_text(text_for_help())


######### buttons #########
main_menu_buttons = [
    [KeyboardButton("Готов помочь 🛒"),
     KeyboardButton("Ищу помощь 🏬")],
    [KeyboardButton("Помощь по боту 🆘")]
]

search_button = [[KeyboardButton("Отменить поиск 🔎")]]

######### find people commands #########
list_for_finders = list()
list_for_couriers = list()


def find_in_lenta(update: Update, context: CallbackContext):
    if is_in_lists(update.message.chat, update):
        return

    try:
        courier = list_for_couriers.pop(0)
        update.message.reply_text(f"Человек, который может вам помочь: @{courier[0]}")
        context.bot.send_message(chat_id=courier[1],
                                 text=f"Человек, который ищет помощь: @{update.message.chat.username}",
                                 reply_markup=ReplyKeyboardMarkup(main_menu_buttons, resize_keyboard=True))
        main_menu(update, context)
    except IndexError:
        list_for_finders.append((update.message.chat.username, update.message.chat.id))
        update.message.reply_text(
            f"По моим данным никого в Ленте сейчас нет. Вы добавлены в очередь. Ваша очередь: "
            f"{list_for_finders.index((update.message.chat.username, update.message.chat_id)) + 1}",
            reply_markup=ReplyKeyboardMarkup(search_button, resize_keyboard=True))


def find_in_punk(update: Update, context: CallbackContext):
    if is_in_lists(update.message.chat, update):
        return

    try:
        finder = list_for_finders.pop(0)
        update.message.reply_text(f"Человек, который ищет помощь: @{finder[0]}")
        context.bot.send_message(chat_id=finder[1],
                                 text=f"Человек, который может вам помочь: @{update.message.chat.username}",
                                 reply_markup=ReplyKeyboardMarkup(main_menu_buttons, resize_keyboard=True))
        main_menu(update, context)
    except IndexError:
        list_for_couriers.append((update.message.chat.username, update.message.chat.id))
        update.message.reply_text(
            f"По моим данным никто не ищет человека в ленте. Вы добавлены в очередь. Ваша очередь:"
            f" {list_for_couriers.index((update.message.chat.username, update.message.chat.id)) + 1}",
            reply_markup=ReplyKeyboardMarkup(search_button, resize_keyboard=True))


def remove_from_list(update: Update, context: CallbackContext):
    try:
        list_for_finders.remove((update.message.chat.username, update.message.chat.id))
        update.message.reply_text("Вы были успешно удалены из списка людей, которые ищут курьера")
        main_menu(update, context)
    except ValueError:
        try:
            list_for_couriers.remove((update.message.chat.username, update.message.chat.id))
            update.message.reply_text("Вы были успешно удалены из списка людей, которые сейчас в ленте")
            main_menu(update, context)
        except ValueError:
            update.message.reply_text("Вас нет ни в какой очереди")
            main_menu(update, context)


######### menu #########
def main_menu(update: Update, context: CallbackContext):
    update.message.reply_text(text="Главное меню",
                              reply_markup=ReplyKeyboardMarkup(main_menu_buttons, resize_keyboard=True))


######### util #########
def unknown_command(update: Update, context: CallbackContext):
    update.message.reply_text("Такой команды не существует :-(")


def message(update: Update, context: CallbackContext):
    if "готов помочь 🛒" in update.message.text.lower():
        find_in_punk(update, context)
    elif "ищу помощь 🏬" in update.message.text.lower():
        find_in_lenta(update, context)
    elif "отменить поиск 🔎" in update.message.text.lower():
        remove_from_list(update, context)
    elif "помощь по боту 🆘" in update.message.text.lower():
        help_command(update, context)
    elif "главное меню" in update.message.text.lower():
        main_menu(update, context)
    else:
        update.message.reply_text("Не могу такое разобрать :-(")


def is_in_lists(chat, update: Update):
    if list_for_finders.__contains__((chat.username, chat.id)):
        update.message.reply_text("Вы уже в списке на поиск курьера",
                                  reply_markup=ReplyKeyboardMarkup(search_button, resize_keyboard=True))
        return True
    if list_for_couriers.__contains__((chat.username, chat.id)):
        update.message.reply_text("Вы уже в списке курьеров",
                                  reply_markup=ReplyKeyboardMarkup(search_button, resize_keyboard=True))
        return True
    return False


######### main #########
def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("help", help_command))

    dispatcher.add_handler(CommandHandler("find_in_lenta", find_in_lenta))
    dispatcher.add_handler(CommandHandler("find_in_punk", find_in_punk))
    dispatcher.add_handler(CommandHandler("clear", remove_from_list))

    dispatcher.add_handler(CommandHandler("menu", main_menu))

    dispatcher.add_handler(MessageHandler(~Filters.command, message))
    dispatcher.add_handler(MessageHandler(Filters.command, unknown_command))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
