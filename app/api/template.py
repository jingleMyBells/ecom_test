import logging

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

from app.service.template import (
    define_input_data_types,
    find_template_match,
    get_templates_from_db,
    modify_request_data_with_dates,
    transform_request_to_data,
)
from app.service.mock_data_service import generate_mock_templates


logger = logging.getLogger(__name__)
router = APIRouter()


@router.post('/get_form')
async def get_form(request: Request) -> JSONResponse:
    """Эндпоинт поиска шаблона."""
    models = await get_templates_from_db()
    request_data = await transform_request_to_data(request)
    if len(request_data.items()) == 0:
        return JSONResponse(
            content={'error': 'Запрос не содержит подходящих данных'},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    request_data_with_date = await modify_request_data_with_dates(request_data)
    template_name = await find_template_match(
        request_data_with_date,
        models,
    )

    if template_name is None:
        logger.info('Подходящий шаблон не найден')
        return JSONResponse(
            content=await define_input_data_types(request_data_with_date),
            status_code=status.HTTP_200_OK,
        )
    else:
        logger.info(f'Модель нашлась, ее имя: {template_name}')
        return JSONResponse(
            content={'Имя искомого шаблона': template_name},
            status_code=status.HTTP_200_OK,
        )


@router.post('/generate')
async def generate_template() -> str:
    """Эндпоинт генерации тестовых данных."""
    logger.info('Генерируем тестовые данные в монге')
    await generate_mock_templates()
    return 'Тестовые шаблоны созданы'
