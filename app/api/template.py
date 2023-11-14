from fastapi import APIRouter, Request

from app.service.template import (
    define_input_data_types,
    find_template_match,
    get_templates_from_db,
    modify_request_data_with_dates
)
from app.service.mock_data_service import generate_mock_templates

import motor.motor_asyncio

router = APIRouter()


@router.post('/get_form')
async def get_form(request: Request):
    models = await get_templates_from_db()
    request_data = await request.json()
    request_data_with_date = await modify_request_data_with_dates(request_data)
    template_name = await find_template_match(
        request_data_with_date,
        models,
    )

    if template_name is None:
        print('Не нашлось модели')
        return await define_input_data_types(request_data_with_date)
    else:
        print(f'Модель нашлась, ее имя: {template_name}')
        return {'Имя искомого шаблона': template_name}


@router.post('/generate')
async def generate_template():
    await generate_mock_templates()
    return 'Тестовые шаблоны созданы'


MONGO_DETAILS = 'mongodb://localhost:27017'


@router.get('/get_templates')
async def get_all_templates():
    db_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
    db = db_client['ecom']
    collection = db['templates']
    cursor = collection.find()
    for doc in await cursor.to_list(length=1000):
        print(doc)
    return 'test ok'
