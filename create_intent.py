import json
import logging

import google.api_core.exceptions
from environs import Env
from google.cloud import dialogflow


def create_intent(project_id, display_name, training_phrases_parts, message_texts):
    """Create an intent of the given intent type"""
    try:
        intents_client = dialogflow.IntentsClient()
        parent = dialogflow.AgentsClient.agent_path(project_id)
        training_phrases = []
        for training_phrases_part in training_phrases_parts:
            part = dialogflow.Intent.TrainingPhrase.Part(text=training_phrases_part)
            # Here we create a new training phrase for each provided part.
            training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
            training_phrases.append(training_phrase)

        text = dialogflow.Intent.Message.Text(text=message_texts)
        message = dialogflow.Intent.Message(text=text)
        logging.debug(f'Intent name: {display_name}\n Training phrases: {training_phrases}\n, Message: {message}')
        intent = dialogflow.Intent(
            display_name=display_name,
            training_phrases=training_phrases,
            messages=[message]
        )
        response = intents_client.create_intent(
            request={"parent": parent, "intent": intent}
        )
        logging.debug(f'Intent created {response}')
    except google.api_core.exceptions.InvalidArgument:
        return logging.error(f'Не удалось создать намерение {display_name}')


def main():
    env = Env()
    env.read_env()
    google_application_credentials = env.path('GOOGLE_APPLICATION_CREDENTIALS')
    project_id = env.str('GOOGLE_CLOUD_PROJECT')
    questions_file_path = env.path('QUESTIONS_FILE_PATH', 'questions.json')

    logging.basicConfig(level=env.str('LOGGING_LEVEL'))
    with open(questions_file_path, 'r', encoding='utf8') as file:
        phrases_json = file.read()
    phrases = json.loads(phrases_json)
    for intent_key, intent_value in phrases.items():
        create_intent(project_id, intent_key, intent_value['questions'], [intent_value['answer']])


if __name__ == '__main__':
    main()
