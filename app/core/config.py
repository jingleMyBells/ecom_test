from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_title: str = 'Тестовое задание e.Com'
    app_description: str = 'Валидатор входящих форм'
    secret: str = 'SNEAKY_SECRET'
    mongo_uri: str = 'mongodb://localhost:27017'
    mongo_database: str = 'ecom'
    mongo_collection: str = 'templates'

    model_config = SettingsConfigDict(env_file='.env')


settings = Settings()
