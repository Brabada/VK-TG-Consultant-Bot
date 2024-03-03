import logging
import random
from logging.handlers import RotatingFileHandler

import telegram
import vk_api as vk
from environs import Env
from google.api_core.exceptions import InvalidArgument
from google.cloud import dialogflow
from vk_api.longpoll import VkLongPoll, VkEventType

logger = logging.getLogger('DebugBotLogger')


class LogTelegramHandler(logging.Handler):
    def __init__(self, bot_token, chat_id):
        super().__init__()
        self.tg_bot = telegram.Bot(token=bot_token)
        self.chat_id = chat_id

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def detect_intent_texts(project_id, session_id, texts, language_code):
    """Returns the result of detect intent with texts as inputs.
    Using the same `session_id` between requests allows continuation
    of the conversation."""

    session_client = dialogflow.SessionsClient()

    session = session_client.session_path(project_id, session_id)
    logger.debug(f'Session path: {session}\n')

    text_input = dialogflow.TextInput(text=texts, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)

    response = session_client.detect_intent(
        request={
            "session": session,
            "query_input": query_input,
        }
    )
    logger.debug(
        f'''Query text: {response.query_result.query_text}
        Detect intent: {response.query_result.intent.display_name} (confidence: {response.query_result.intent_detection_confidence})
        Fulfillment text: {response.query_result.fulfillment_text}'''
    )

    if response.query_result.intent.is_fallback:
        return

    return response.query_result.fulfillment_text


def echo(event, vk_api):
    return vk_api.messages.send(
        user_id=event.user_id,
        message=event.message,
        random_id=random.randint(0, 1000)
    )


def answer(event, vk_api, dialogflow_vars):
    message = detect_intent_texts(
        dialogflow_vars['project_id'],
        event.user_id,
        event.message,
        dialogflow_vars['language_code'],
    )
    if message:
        logger.debug(message)
        return vk_api.messages.send(
            user_id=event.user_id,
            message=message,
            random_id=random.randint(1, 1000)
        )
    else:
        logger.debug(message)
        message_not_defined = 'Я вас не понимаю...'
        logger.debug(message_not_defined)
        vk_api.messages.send(
            user_id=event.user_id,
            message=message_not_defined,
            random_id=random.randint(1, 1000)
        )


def vk_longpoll(vk_group_token, dialogflow_vars):
    vk_session = vk.VkApi(token=vk_group_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            answer(event, vk_api, dialogflow_vars)


def main():
    env = Env()
    env.read_env()

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.setLevel(level=env.str("LOGGING_LEVEL"))

    logger_handler = RotatingFileHandler('start_vk_bot.log', maxBytes=200, backupCount=3)
    logger.addHandler(logger_handler)

    logger.addHandler(
        LogTelegramHandler(
            chat_id=env.str('TG_USER_ID_FOR_LOGS'),
            bot_token=env.str('TG_LOG_BOT_TOKEN'))
    )

    vk_group_token = env.str('VK_GROUP_TOKEN')
    google_application_credentials_path = env.path('GOOGLE_APPLICATION_CREDENTIALS')

    dialogflow_vars = {
        'project_id': env.str('GOOGLE_CLOUD_PROJECT'),
        'language_code': env.str('LANGUAGE_CODE'),
    }

    logger.warning('The VK Consultant Bot is running')
    while True:
        try:
            vk_longpoll(vk_group_token, dialogflow_vars)
        except InvalidArgument as err:
            logger.error('Its possible that received message include sticker:')
            logger.exception(err)
        except Exception as err:
            logger.exception(err)


if __name__ == "__main__":
    main()