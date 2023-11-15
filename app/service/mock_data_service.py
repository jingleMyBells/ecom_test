from datetime import datetime

import motor.motor_asyncio

from app.core.config import settings


async def generate_mock_templates() -> None:
    """
    Функция для создания тестового набора шаблонов в бд.
    """
    db_client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongo_uri)
    db = db_client[settings.mongo_database]
    collection = db[settings.mongo_collection]

    template_1 = {
        'name': 'EmailForm',
        'email': 'python@python.ru'
    }

    template_2 = {
        'name': 'PhoneForm',
        'phone': '+7 456 789 32 12'
    }

    template_3 = {
        'name': 'DateForm',
        'current_date': datetime.now()
    }

    template_4 = {
        'name': 'MultyFieldForm',
        'email': 'python@python.ru',
        'phone': '+7 456 789 32 12',
        'current_date': datetime.now(),
    }

    template_5 = {
        'name': 'ExtraFieldsForm',
        'email': 'python@python.ru',
        'user_email': 'python@python.ru',
        'phone': '+7 456 789 32 12',
        'current_date': datetime.now(),
        'some_text': 'съешь еще этих французских булок да выпей йаду'
    }

    await collection.insert_many(
        [
            template_1,
            template_2,
            template_3,
            template_4,
            template_5
        ],
    )
