from datetime import datetime

import motor.motor_asyncio
from pydantic.v1 import create_model

from app.model.template import CreatableModel, email_validator, phone_validator


MONGO_DETAILS = 'mongodb://localhost:27017'


async def date_converter(value):
    format_1 = '%d.%m.%Y'
    format_2 = '%Y-%m-%d'
    try:
        date_value = datetime.strptime(value, format_1)
        print("SHOULD WORK HERE")
        return date_value
    except (ValueError, TypeError):
        try:
            date_value = datetime.strptime(value, format_2)
            return date_value
        except (ValueError, TypeError):
            raise ValueError('Данные не соответствуют приемлемым форрматам даты')


async def modify_request_data_with_dates(data: dict):
    data_with_dates = dict()
    for key, value in data.items():
        try:
            data_with_dates[key] = await date_converter(value)
        except ValueError:
            data_with_dates[key] = value
    return data_with_dates


async def get_templates_from_db():
    db_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
    db = db_client['ecom']
    collection = db['templates']
    cursor = collection.find()
    models = []
    for doc in await cursor.to_list(length=1000):
        fields = {}
        name = doc.pop('name')
        doc.pop('_id')
        for key, value in doc.items():
            fields[key] = (type(value), ...)
        Model = create_model(name, __base__=CreatableModel)
        await Model.add_fields(**fields)
        models.append(Model)
    models.sort(key=lambda m: len(m.__fields__), reverse=True)
    return models


async def find_template_match(data, models):
    template_name = None
    for model in models:
        try:
            obj = model(**data)
            template_name = model.__name__
            break
        except Exception as e:
            print(e)
            continue
    return template_name

TYPES = {
    'phone': phone_validator,
    'email': email_validator,
}


async def define_input_data_types(data):
    result = dict()
    for key, value in data.items():
        if isinstance(value, datetime):
            result[key] = value.__class__.__name__.upper()
            break
        for type_key, type_value in TYPES.items():
            try:
                validation_result = type_value(value)
                if validation_result is not None:
                    result[key] = type_key.upper()
                    break
            except Exception as e:
                print("HERE")
                print(e)
                continue
        if result.get(key) is None:
            if isinstance(value, str):
                result[key] = 'TEXT'
            else:
                result[key] = (f'{value.__class__.__name__.upper()}, '
                               f'данный тип данных не поддержан ни в '
                               f'одном из шаблонов')

    return result


