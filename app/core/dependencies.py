from app.services.database_service import DatabaseService

# Instancia singleton del servicio de base de datos
_database_service = None


def get_database_service() -> DatabaseService:
    """Dependency injection para el servicio de base de datos"""
    global _database_service
    if _database_service is None:
        _database_service = DatabaseService()
    return _database_service