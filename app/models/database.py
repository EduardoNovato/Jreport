from pydantic import BaseModel
from typing import Optional


class DatabaseConnection(BaseModel):
    """Modelo para la configuración de conexión a base de datos"""
    db_type: str = "postgres"  # "postgres", "mysql", etc.
    host: str
    port: int
    database: str
    username: str
    password: str


class SQLQuery(BaseModel):
    """Modelo para ejecutar consultas SQL"""
    connection_id: str
    query: str
    # limit: Optional[int] = 100


class ConnectionResponse(BaseModel):
    """Modelo de respuesta para conexión exitosa"""
    status: str
    message: str
    connection_id: str


class QueryResponse(BaseModel):
    """Modelo de respuesta para consultas SQL"""
    status: str
    connection_id: str
    database: str
    query: str
    row_count: int
    data: list
    metadata: dict