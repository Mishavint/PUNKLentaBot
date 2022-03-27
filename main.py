import logging
from config import TOKEN

from telegram import (
    Update,
    ForceReply,
    InlineQueryResultArticle,
    InputTextMessageContent,
    ParseMode)

from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    InlineQueryHandler,
    MessageFilter,
    Defaults
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


### Texts ###
def text_for_start(name):
    return f"""
Приветствую, {name}. Я чат-бот для поиска людей в ленте. Я был создан студентов Пунка для студентов Пунка
        
На данный момент это MVP(Minimal Viable Product). Так что доступны всего 2 команды:
    
/find_in_lenta
/find_in_punk
    """


def text_for_help():
    return "help :D"


######### start help commands #########
def start_command(update: Update, context: CallbackContext):
    name = update.message.chat.first_name
    update.message.reply_text(text_for_start(name))


def help_command(update, context):
    return 3


#########  find people commands #########
list_for_finders = list()
list_for_couriers = list()


def find_in_lenta(update: Update, context: CallbackContext):
    if list_for_couriers.__contains__((update.message.chat.username, update.message.chat.id)):
        update.message.reply_text("Вы уже в очереди")
        return

    try:
        courier = list_for_couriers.pop(0)
        update.message.reply_text(f"Человек, который может вам помочь:@{courier[0]}")
        context.bot.send_message(chat_id=courier[1],
                                 text=f"Человек, который ищет помощь:@{update.message.chat.username}")
    except IndexError:
        list_for_finders.append((update.message.chat.username, update.message.chat.id))
        update.message.reply_text(
            f"По моим данным никого в Ленте сейчас нет. Вы добавлены в очередь. Ваша очередь: "
            f"{list_for_finders.index((update.message.chat.username, update.message.chat_id)) + 1}"
        )


def find_in_punk(update: Update, context: CallbackContext):
    if list_for_couriers.__contains__((update.message.chat.username, update.message.chat.id)):
        update.message.reply_text("Вы уже в очереди")
        return

    try:
        finder = list_for_finders.pop(0)
        update.message.reply_text(f"Человек, который ищет помощь:@{finder[0]}")
        context.bot.send_message(chat_id=finder[1],
                                 text=f"Человек, который может вам помочь:@{update.message.chat.username}")
    except IndexError:
        list_for_couriers.append((update.message.chat.username, update.message.chat.id))
        update.message.reply_text(
            f"Никто не ищёт человека в ленте. Вы добавлены в очередь. Ваша очередь:"
            f" {list_for_couriers.index((update.message.chat.username, update.message.chat.id)) + 1}")


######### util #########
def unknown_command(update: Update, context: CallbackContext):
    update.message.reply_text("Такой комманды не существует :-(")


def unknown_message(update: Update, context: CallbackContext):
    update.message.reply_text("Не могу такое разобрать :-(")


#########  main #########
def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("find_in_lenta", find_in_lenta))
    dispatcher.add_handler(CommandHandler("find_in_punk", find_in_punk))
    dispatcher.add_handler(MessageHandler(~Filters.command, unknown_message))

    dispatcher.add_handler(MessageHandler(Filters.command, unknown_command))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
