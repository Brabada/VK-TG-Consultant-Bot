# VK/TG Consultant Bot

## Описание
Данный проект создан, чтобы при помощи DialogFlow обучить ботов отвечать на сообщения в VK и Telegram, заменяя тем
самым консультанта.

Схема работы для VK и Telegram схожа. Бот принимает сообщение в чате, отправляет его по API в DialogFlow. Далее пересылает ответ
от DialogFlow обратно в чат.

## Состав
- `start_vk_bot.py` - запускает бота для Telegram;
- `start_tg_bot.py` - запускает бота для VK;
- `create_intent.py` - создаёт intent (намерение) для обучающейся модели в DialogFlow по переданному в question.json 
вопросам и ответам на них. Пример файла question.json в репозитории;
- `create_api_key` - создаёт файл api_key.txt, содержащий ключ API для указанного project_id в Google Cloud. 

## Подготовка

- Создать аккаунт на https://dialogflow.cloud.google.com/
- Создать проект (https://cloud.google.com/dialogflow/docs/quick/setup) и получить его идентификатор
- Создать агента для проекта (https://cloud.google.com/dialogflow/es/docs/quick/build-agent)
- Включить API DialogFlow на Google-аккаунте (https://cloud.google.com/dialogflow/es/docs/quick/setup#api)
- Сформировать файл с ключами credentials.json от Google-аккаунта (https://cloud.google.com/dialogflow/es/docs/quick/setup#sdk)
- Запустить `create_api_key.py` с переданным `PROJECT_ID` (идентификатор проекта) и `GOOGLE_APPLICATION_CREDENTIALS`
  (путь до credentials.json, включая полное название файла). Более подробно о запуске в разделе "Получение API-ключа"
- Обучить модель, путём создания намерения через скрипт `create_intent.py`. Более подробно - в "Обучаем модель".
- Создать ключ доступа (токен) для группы VK и/или идентификатор токен созданного бота в Telegram.

## Создание API-ключа DialogFlow

Для взаимодействия с платформой DialogFlow помимо файла с ключами от Google-аккаунта ещё нужен API-ключ от аккаунта на DialogFlow
для работы с ним.

Перед созданием ключа у вас уже должен быть ID вашего проекта (e.g. `agent-007-kvtv`). 

- Создайте файл .env в директории с `create_api_key.py`, если вы ещё этого не сделали
- Добавьте строку `GOOGLE_CLOUD_PROJECT=%ID_ВАШЕГО_ПРОЕКТА%`
- Инициализируйте и активируйте venv: `python -m venv venv && . venv/Scripts/Activate`
- Установите зависимости: `pip install -r requirements.txt`
- Запустите `create_api_key.py`, ключ будет создан в виде файла `credentials.json` в той же папки, где был запущен скрипт.

## Обучаем модель DialogFlow

Есть два пути обучить модель в DialogFlow, прописать руками реакции на темы на сайте или загрузить реакции на темы через файл.
Для этого служит скрипт `create_intent.py`. Скрипт принимает полный путь к json-файлу с данными и обучает агента, привязанного к вашему проекту.

### Требуемая структура json-файла

Пример json-файла добавлен в репозиторий в виде файла `questions.py`.

Пример:
```json
"Устройство на работу": {
        "questions": [
            "Как устроиться к вам на работу?",
            "Как устроиться к вам?",
            "Как работать у вас?",
            "Хочу работать у вас",
            "Возможно-ли устроиться к вам?",
            "Можно-ли мне поработать у вас?",
            "Хочу работать редактором у вас"
        ],
        "answer": "Если вы хотите устроиться к нам, напишите на почту game-of-verbs@gmail.com мини-эссе о себе и прикрепите ваше портфолио."
    },
```
Первым уровнем задаётся тема (intention). Название ключей `questions` и `answer` не меняется, изменяется только их содержимое.

### Запуск create_intent.py
```shell
python3 create_intent.py path/to/questions.json
```

## Запуск бота для VK

### .env
- `VK_GROUP_TOKEN` - токен доступа для группы ВК в котором будет отвечать бот;
- `GOOGLE_APPLICATION_CREDENTIALS` - полный путь к _credentials.json_, который содержит API-ключ для DialogFlow
- `GOOGLE_CLOUD_PROJECT` - ID проекта на DialogFlow
- `LANGUAGE_CODE` - схема языка для DialogFlow

### Запуск start_vk_bot.py
```shell
python3 start_vk_bot.py
```

## Запуск бота для Telegram

### .env
- `TG_BOT_TOKEN` - токен вашего Telegram-бота;
- `GOOGLE_APPLICATION_CREDENTIALS` - полный путь к _credentials.json_, который содержит API-ключ для DialogFlow
- `GOOGLE_CLOUD_PROJECT` - ID проекта на DialogFlow
- `LANGUAGE_CODE` - схема языка для DialogFlow
- `LOGGING_LEVEL` - минимальный уровень отображения логов (DEBUG, INFO, WARNING, ERROR, CRITICAL)

### Запуск start_tg_bot.py
```shell
python3 start_tg_bot.py
```