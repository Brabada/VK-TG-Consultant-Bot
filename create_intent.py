import json
import os

from environs import Env
from google.cloud import dialogflow


def create_intent(project_id, display_name, training_phrases_parts, message_texts):
    """Create an intent of the given intent type"""
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
    intent = dialogflow.Intent(
        display_name=display_name,
        training_phrases=training_phrases,
        messages=[message]
    )
    response = intents_client.create_intent(
        request={"parent": parent, "intent": intent}
    )
    print(f'Intent created {response}')


def main():
    env = Env()
    env.read_env()
    google_application_credentials = env.path('GOOGLE_APPLICATION_CREDENTIALS')
    project_id = env.str('GOOGLE_CLOUD_PROJECT')
    with open('questions.json', 'r', encoding='utf8') as file:
        phrases_json = file.read()
    phrases = json.loads(phrases_json)
    intent_topic = 'Устройство на работу'
    answer = [phrases[intent_topic]['answer']] # answer must be list or create_intent slicing single answer by letters
    create_intent(project_id, intent_topic, phrases[intent_topic]['questions'], answer)


if __name__ == '__main__':
    main()