from typing import Any, Dict, Optional
import re

from pydantic.v1 import BaseModel
from pydantic.v1.class_validators import Validator
from pydantic.v1.fields import ModelField


def phone_validator(v):
    regex = r'^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$'
    if re.match(regex, v):
        return v
    raise ValueError('phone is incorrect')


def email_validator(v):
    regex = (r'^[a-z0-9!#$%&"*+/=?^_`{|}~-]+'
             r'(?:\.[a-z0-9!#$%&"*+/=?^_`{|}~'
             r'-]+)*@(?:[a-z0-9](?:[a-z0-9-]*'
             r'[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$')
    if re.match(regex, v):
        return v
    raise ValueError('email is incorrect')


PHONE_VALIDATOR = Validator(phone_validator)
EMAIL_VALIDATOR = Validator(email_validator)


TYPES_VALIDATORS = {
    'phone': PHONE_VALIDATOR,
    'mail': EMAIL_VALIDATOR,
}


class CreatableModel(BaseModel):
    """
    Модель для выгрузки шаблонов из базы данных.
    Добавлен метод для наполнения модели полями нужных типов данных.
    Типы данных соответствуют базовым для Монги,
    снабжены кастомными валидаторами.
    """

    @classmethod
    async def add_fields(cls, **field_definitions: Any):
        new_fields: Dict[str, ModelField] = {}
        new_annotations: Dict[str, Optional[type]] = {}

        for f_name, f_def in field_definitions.items():
            if isinstance(f_def, tuple):
                try:
                    f_annotation, f_value = f_def
                except ValueError as e:
                    raise Exception('field definitions should either'
                                    ' be a tuple of (<type>, <default>)'
                                    ' or just a default value, unfortunately'
                                    ' this means tuples as default values '
                                    'are not allowed') from e
            else:
                f_annotation, f_value = None, f_def

            if f_annotation:
                new_annotations[f_name] = f_annotation

            class_validators = None

            for key in TYPES_VALIDATORS.keys():
                if key.lower() in f_name.lower():
                    class_validators = {
                        'validate_always': TYPES_VALIDATORS.get(key)
                    }
                    break

            new_fields[f_name] = ModelField.infer(
                name=f_name,
                value=f_value,
                annotation=f_annotation,
                class_validators=class_validators,
                config=cls.__config__,
            )

        cls.__fields__.update(new_fields)
        cls.__annotations__.update(new_annotations)
