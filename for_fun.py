import logging
import pytz
import datetime as dtm

from config import TOKEN
from uuid import uuid4
from telegram import Update, ForceReply, InlineQueryResultArticle, InputTextMessageContent, ParseMode
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
temp_list = [2]


def start(update: Update, context: CallbackContext):
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def help_command(update: Update, context: CallbackContext):
    temp_list.append(temp_list[-1] + 1)
    update.message.reply_text(f'Help!\n{temp_list[-1]}')


def echo(update: Update, context: CallbackContext):
    update.message.reply_text(update.message.text)


def caps(update: Update, context: CallbackContext):
    text_caps = ' '.join(context.args).upper()
    context.bot.send_message(chat_id=update.effective_user.id, text=text_caps)


def unknown(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Sorry, I didn't understand that command.")


def put(update: Update, context: CallbackContext):
    """Usage: /put value"""
    # Generate ID and separate value from command
    key = str(uuid4())
    # We don't use context.args here, since they value may contain whitespaces
    value = update.message.text.partition(' ')[2]

    # Store value
    context.user_data[key] = value
    # Send the key to the user
    update.message.reply_text(key)


def get(update: Update, context: CallbackContext):
    """Usage: /get uuid"""
    # Separate ID from command
    key = context.args[0]

    # Load value and send it to the user
    value = context.user_data.get(key, 'Not found')
    update.message.reply_text(value)


def job(context):
    chat_id = context.job.context
    local_now = dtm.datetime.now(context.bot.defaults.tzinfo)
    utc_now = dtm.datetime.utcnow()
    text = 'Running job at {} in timezone {}, which equals {} UTC.'.format(
        local_now, context.bot.defaults.tzinfo, utc_now
    )
    context.bot.send_message(chat_id=chat_id, text=text)


def echo2(update: Update, context):
    # Send with default parse mode
    update.message.reply_text('<b>{}</b>'.format(update.message.text))
    # Override default parse mode locally
    update.message.reply_text('*{}*'.format(update.message.text), parse_mode=ParseMode.MARKDOWN)
    update.message.reply_text('*{}*'.format(update.message.text), parse_mode=None)

    # Schedule job
    context.job_queue.run_once(job, dtm.datetime.now(), context=update.effective_chat.id)


def main():
    defaults = Defaults(parse_mode=ParseMode.HTML, tzinfo=pytz.timezone('Europe/Moscow'))
    updater = Updater(TOKEN, use_context=True, defaults=defaults)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    # dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo2))
    dispatcher.add_handler(CommandHandler("caps", caps))
    dispatcher.add_handler(CommandHandler('put', put))
    dispatcher.add_handler(CommandHandler('get', get))
    dispatcher.add_handler(MessageHandler(Filters.command, unknown))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
