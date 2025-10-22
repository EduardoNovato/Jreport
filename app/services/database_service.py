from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from typing import Dict, Any
import logging

from app.models.database import DatabaseConnection, SQLQuery

logger = logging.getLogger(__name__)


class DatabaseService:
    """Servicio para manejar conexiones y consultas de base de datos"""
    
    def __init__(self):
        self.active_connections: Dict[str, DatabaseConnection] = {}
        self.active_engines: Dict[str, Any] = {}
    
    def create_connection_string(self, connection: DatabaseConnection) -> str:
        """Crear string de conexión según el tipo de base de datos"""
        if connection.db_type.lower() == "postgres":
            return f"postgresql://{connection.username}:{connection.password}@{connection.host}:{connection.port}/{connection.database}"
        elif connection.db_type.lower() == "mysql":
            return f"mysql+pymysql://{connection.username}:{connection.password}@{connection.host}:{connection.port}/{connection.database}"
        else:
            raise HTTPException(status_code=400, detail="Tipo de base de datos no soportado")
    
    def connect_database(self, connection: DatabaseConnection):
        """Conectar a la base de datos y retornar connection_id"""
        try:
            connection_string = self.create_connection_string(connection)
            engine = create_engine(connection_string, echo=False)
            
            # Generar ID único para la conexión
            connection_id = f"{connection.db_type}_{connection.host}_{connection.port}_{connection.database}"
            
            # Guardar conexión y engine
            self.active_connections[connection_id] = connection
            self.active_engines[connection_id] = engine
            
            logger.info(f"Conexión exitosa: {connection_id}")
            return connection_id
            
        except SQLAlchemyError as e:
            logger.error(f"Error SQLAlchemy: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error de conexión a la base de datos: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error general: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error al conectar con la base de datos: {str(e)}"
            )
    
    def execute_query(self, sql_query: SQLQuery):
        """Ejecutar consulta SQL y retornar resultados"""
        try:
            # Verificar que la conexión existe
            if sql_query.connection_id not in self.active_connections:
                raise HTTPException(
                    status_code=404,
                    detail="Conexión no encontrada. Primero conecta a una base de datos."
                )
            
            if sql_query.connection_id not in self.active_engines:
                raise HTTPException(
                    status_code=404,
                    detail="Engine de conexión no encontrado."
                )
            
            connection = self.active_connections[sql_query.connection_id]
            engine = self.active_engines[sql_query.connection_id]
            
            # Validar que sea una consulta de solo lectura
            query_lower = sql_query.query.strip().lower()
            allowed_queries = ['select']
            
            if not any(query_lower.startswith(cmd) for cmd in allowed_queries):
                raise HTTPException(
                    status_code=400,
                    detail="Solo se permiten consultas de lectura (SELECT)"
                )
            
            # Ejecutar consulta
            with engine.connect() as conn:
                query_to_execute = sql_query.query
                
                # Agregar LIMIT si no está presente
                if (sql_query.limit and 
                    'limit' not in query_lower and 
                    query_lower.startswith('select')):
                    query_to_execute += f" LIMIT {sql_query.limit}"
                
                result = conn.execute(text(query_to_execute))
                rows = result.fetchall()
                
                # Convertir a lista de diccionarios
                if rows:
                    columns = list(result.keys())
                    data = [dict(zip(columns, row)) for row in rows]
                else:
                    data = []
                
                logger.info(f"Query ejecutada: {query_to_execute} - Filas: {len(data)}")
            
            return {
                "status": "success",
                "connection_id": sql_query.connection_id,
                "database": connection.database,
                "query": sql_query.query,
                "row_count": len(data),
                "data": data
            }
            
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            logger.error(f"Error SQLAlchemy en query: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error al ejecutar la consulta: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error general en query: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error al ejecutar la consulta: {str(e)}"
            )
    
    def get_active_connections(self):
        """Obtener lista de conexiones activas"""
        connections_info = []
        for conn_id, conn in self.active_connections.items():
            connections_info.append({
                "connection_id": conn_id,
                "database_type": conn.db_type.upper(),
                "host": conn.host,
                "port": conn.port,
                "database": conn.database,
                "schema": conn.schema
            })
        
        return {
            "status": "success",
            "active_connections": len(self.active_connections),
            "connections": connections_info
        }