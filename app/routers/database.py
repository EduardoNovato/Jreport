from fastapi import APIRouter, Depends
from app.models.database import DatabaseConnection, SQLQuery
from app.services.database_service import DatabaseService
from app.core.dependencies import get_database_service

router = APIRouter(prefix="/database", tags=["Database"])


@router.post("/connection")
async def create_database_connection(
    connection: DatabaseConnection,
    db_service: DatabaseService = Depends(get_database_service)
):
    """
    Endpoint para probar la conexión a base de datos
    Soporta PostgreSQL y MySQL
    """
    connection_id = db_service.connect_database(connection)
    
    return {
        "status": "success",
        "message": f"Conexión exitosa a la base de datos {connection.database} ({connection.db_type.upper()})",
        "connection_id": connection_id
    }


@router.post("/query")
async def execute_sql_query(
    sql_query: SQLQuery,
    db_service: DatabaseService = Depends(get_database_service)
):
    """
    Endpoint para ejecutar consultas SQL en una base de datos conectada
    Permite consultas SELECT únicamente
    """
    return db_service.execute_query(sql_query)


@router.get("/connections")
async def list_active_connections(
    db_service: DatabaseService = Depends(get_database_service)
):
    """
    Listar todas las conexiones activas
    """
    return db_service.get_active_connections()

@router.delete("/connection/{connection_id}")
async def close_database_connection(
    connection_id: str,
    db_service: DatabaseService = Depends(get_database_service)
):
    """
    Cerrar una conexión de base de datos activa
    """
    return db_service.close_connection(connection_id)