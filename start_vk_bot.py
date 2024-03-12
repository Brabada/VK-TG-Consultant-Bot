import logging
import random
from logging.handlers import RotatingFileHandler

import vk_api as vk
from environs import Env
from google.api_core.exceptions import InvalidArgument
from vk_api.longpoll import VkLongPoll, VkEventType

import intentions_api
import log_handlers

logger = logging.getLogger('DebugBotLogger')


def echo(event, vk_api):
    return vk_api.messages.send(
        user_id=event.user_id,
        message=event.message,
        random_id=random.randint(0, 1000)
    )


def answer(event, vk_api, dialogflow_vars):
    message = intentions_api.detect_intent_texts(
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
        log_handlers.LogTelegramHandler(
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