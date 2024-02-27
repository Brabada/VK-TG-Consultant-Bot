import random
import logging
import vk_api as vk
from environs import Env
from google.cloud import dialogflow
from vk_api.longpoll import VkLongPoll, VkEventType


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
    logging.debug(
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
        return vk_api.messages.send(
            user_id=event.user_id,
            message=message,
            random_id=random.randint(1, 1000)
        )
    else:
        return


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
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=env.str("LOGGING_LEVEL")
    )
    vk_group_token = env.str('VK_GROUP_TOKEN')
    google_application_credentials_path = env.path('GOOGLE_APPLICATION_CREDENTIALS')

    dialogflow_vars = {
        'project_id': env.str('GOOGLE_CLOUD_PROJECT'),
        'language_code': env.str('LANGUAGE_CODE'),
    }

    logging.warning('The VK Consultant Bot is running')
    try:
        vk_longpoll(vk_group_token, dialogflow_vars)
    except Exception as err:
        logging.exception(err)


if __name__ == "__main__":
    main()