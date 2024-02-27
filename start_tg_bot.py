import os
import functools
import logging

from environs import Env
from telegram import Update
from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters
from google.cloud import dialogflow


def detect_intent_texts(project_id, session_id, texts, language_code):
    """Returns the result of detect intent with texts as inputs.
    Using the same `session_id` between requests allows continuation
    of the conversation."""

    session_client = dialogflow.SessionsClient()

    session = session_client.session_path(project_id, session_id)

    logging.debug(f'Session path: {session}\n')

    text_input = dialogflow.TextInput(text=texts, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)

    response = session_client.detect_intent(
        request={
            "session": session,
            "query_input": query_input,
        }
    )
    logging.debug(f'''Query text: {response.query_result.query_text}
        Detect intent: {response.query_result.intent.display_name} (confidence: {response.query_result.intent_detection_confidence}
        Fulfillment text: {response.query_result.fulfillment_text}
    ''')
    return response.query_result.fulfillment_text


def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text='Здравствуйте!')


def echo(update: Update, context: CallbackContext, project_id: str = '', language_code: str = ''):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


def answer(update: Update, context: CallbackContext, project_id: str = '', language_code: str = ''):
    answer = detect_intent_texts(project_id, update.effective_chat.id, update.message.text, language_code)
    context.bot.send_message(chat_id=update.effective_chat.id, text=answer)


def main():
    logging.warning('The TG Consultant Bot is running')

    env = Env()
    env.read_env()
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=env.str("LOGGING_LEVEL"))
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
    except Exception as err:
        logging.exception(err)


if __name__ == "__main__":
    main()
