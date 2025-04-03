from dependency_injector import containers, providers
from app.services.firebase_service import FirebaseService
from app.services.task_manager_service import TaskManagerService
from app.controllers.dashboard_controller import DashboardController
from app.views.screens.specialized_dashboard_screen import SpecializedDashboardScreen
from app.services.config_service import ConfigService

class Container(containers.DeclarativeContainer):
    """Container principal pour l'injection de dépendances."""
    
    # Configuration
    config = providers.Configuration()
    
    # Services
    config_service = providers.Singleton(ConfigService)
    
    firebase_service = providers.Singleton(
        FirebaseService
    )
    
    task_manager = providers.Singleton(
        TaskManagerService,
        firebase_service=firebase_service
    )
    
    # Controllers
    dashboard_controller = providers.Factory(
        DashboardController,
        task_manager=task_manager,
        firebase_service=firebase_service
    )
