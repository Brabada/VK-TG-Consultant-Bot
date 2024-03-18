import logging

from google.cloud import dialogflow

logger = logging.getLogger('DebugBotLogger')


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

    logger.debug(f'''Query text: {response.query_result.query_text}
        Detect intent: {response.query_result.intent.display_name} (confidence: {response.query_result.intent_detection_confidence})
        Fulfillment text: {response.query_result.fulfillment_text}
    ''')

    if response.query_result.intent.is_fallback:
        logger.debug(f'''This is fallback message!''')
        return
    else:
        return response.query_result.fulfillment_text