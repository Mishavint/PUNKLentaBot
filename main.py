import logging
from config import TOKEN

from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


### Texts ###
def text_for_start(name):
    return f"""
Приветствую, {name}. Я чат-бот для поиска людей в ленте. Я был создан студентом Пунка для студентов Пунка

На данный момент это MVP(Minimal Viable Product). Так что доступны всего 2 команды:

/find_in_lenta - команда для поиска людей, которые сейчас в Ленте и готовы доставить вам продукты
/find_in_punk - команда для поиска людей, которые сейчас в Пунке, если вы сейчас в Ленте
/clear - команда, чтобы вас удалили из очереди

Будьте людьми, заранее договаривайтесь про вознаграждение 🐒
"""


def text_for_help():
    return """
Бот создан @mishavint. Со всеми вопросами и пожеланиями писать ему (Умоляю не ночью).    

На данный момент реализована только MVP(Minimal Viable Product). Так что доступны всего 2 команды:
/find_in_lenta - команда для поиска людей, которые сейчас в Ленте и готовы доставить вам продукты
/find_in_punk - команда для поиска людей, которые сейчас в Пунке, если вы сейчас в Ленте
/clear - команда, чтобы вас удалили из очереди

Будьте людьми, заранее договаривайтесь про вознаграждение 🐒
"""


######### start help commands #########
def start_command(update: Update, context: CallbackContext):
    name = update.message.chat.first_name
    update.message.reply_text(text_for_start(name))


def help_command(update, context):
    update.message.reply_text(text_for_help())


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
                                 text=f"Человек, который ищет помощь: @{update.message.chat.username}")
        print(f"finders: {list_for_finders}\ncouriers: {list_for_couriers}")
    except IndexError:
        list_for_finders.append((update.message.chat.username, update.message.chat.id))
        update.message.reply_text(
            f"По моим данным никого в Ленте сейчас нет. Вы добавлены в очередь. Ваша очередь: "
            f"{list_for_finders.index((update.message.chat.username, update.message.chat_id)) + 1}")
        print(f"finders: {list_for_finders}\ncouriers: {list_for_couriers}")


def find_in_punk(update: Update, context: CallbackContext):
    if is_in_lists(update.message.chat, update):
        return

    try:
        finder = list_for_finders.pop(0)
        update.message.reply_text(f"Человек, который ищет помощь: @{finder[0]}")
        context.bot.send_message(chat_id=finder[1],
                                 text=f"Человек, который может вам помочь: @{update.message.chat.username}")
        print(f"finders: {list_for_finders}\ncouriers: {list_for_couriers}")
    except IndexError:
        list_for_couriers.append((update.message.chat.username, update.message.chat.id))
        update.message.reply_text(
            f"Никто не ищёт человека в ленте. Вы добавлены в очередь. Ваша очередь:"
            f" {list_for_couriers.index((update.message.chat.username, update.message.chat.id)) + 1}")
        print(f"finders: {list_for_finders}\ncouriers: {list_for_couriers}")


def remove_from_list(update: Update, context: CallbackContext):
    try:
        list_for_finders.remove((update.message.chat.username, update.message.chat.id))
        update.message.reply_text("Вы были успешно удалены из списка людей, которые ищут курьера")
        return
    except ValueError:
        try:
            list_for_couriers.remove((update.message.chat.username, update.message.chat.id))
            update.message.reply_text("Вы были успешно удалены из списка людей, которые сейчас в ленте")
            return
        except ValueError:
            update.message.reply_text("Вас нет ни в какой очереди")


######### util #########
def unknown_command(update: Update, context: CallbackContext):
    update.message.reply_text("Такой комманды не существует :-(")


def unknown_message(update: Update, context: CallbackContext):
    update.message.reply_text("Не могу такое разобрать :-(")


def is_in_lists(chat, update: Update):
    if list_for_finders.__contains__((chat.username, chat.id)):
        update.message.reply_text("Вы уже в списке на поиск курьера")
        return True
    if list_for_couriers.__contains__((chat.username, chat.id)):
        update.message.reply_text("Вы уже в списке курьеров")
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
    dispatcher.add_handler(MessageHandler(~Filters.command, unknown_message))

    dispatcher.add_handler(MessageHandler(Filters.command, unknown_command))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
