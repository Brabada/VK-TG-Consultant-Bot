import functools
import logging
from logging.handlers import RotatingFileHandler

from environs import Env
from google.api_core.exceptions import InvalidArgument
from telegram import Update
from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters

import intentions_api
import log_handlers

logger = logging.getLogger('DebugBotLogger')


def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text='Здравствуйте!')


def answer(update: Update, context: CallbackContext, project_id: str = '', language_code: str = ''):
    answer = intentions_api.detect_intent_texts(
        project_id,
        update.effective_chat.id,
        update.message.text,
        language_code
    )
    context.bot.send_message(chat_id=update.effective_chat.id, text=answer)


def main():

    env = Env()
    env.read_env()

    # Initializing and config bot for debug messages
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.setLevel(level=env.str("LOGGING_LEVEL"))

    logger_handler = RotatingFileHandler('start_tg_bot.log', maxBytes=200, backupCount=3)
    logger.addHandler(logger_handler)

    logger.addHandler(
        log_handlers.LogTelegramHandler(
            chat_id=env.str('TG_USER_ID_FOR_LOGS'),
            bot_token=env.str('TG_LOG_BOT_TOKEN'))
    )
    logger.warning('The TG Consultant Bot is running')

    # Initializing and config consultant bot
    tg_bot_token = env.str('TG_BOT_TOKEN')
    google_application_credentials_path = env.path('GOOGLE_APPLICATION_CREDENTIALS')
    project_id = env.str('GOOGLE_CLOUD_PROJECT')
    language_code = env.str('LANGUAGE_CODE')

    try:
        updater = Updater(token=tg_bot_token, use_context=True)
        dispatcher = updater.dispatcher

        start_handler = CommandHandler('start', start)
        dispatcher.add_handler(start_handler)

        answer_handler = MessageHandler(
            Filters.text & (~Filters.command),
            functools.partial(answer, project_id=project_id, language_code=language_code)
        )
        dispatcher.add_handler(answer_handler)
        updater.start_polling()
    except InvalidArgument as err:
        logger.error('Its possible that received message include sticker:')
        logger.exception(err)
    except Exception as err:
        logger.exception(err)


if __name__ == "__main__":
    main()
