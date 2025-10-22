from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración de la aplicación"""
    app_name: str = "Servicios de Jreport"
    app_version: str = "0.0.1"
    debug: bool = True

settings = Settings()