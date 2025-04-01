from dependency_injector import containers, providers
from app.services.firebase_service import FirebaseService
from app.services.task_manager_service import TaskManagerService
from app.controllers.dashboard_controller import DashboardController
from app.views.screens.specialized_dashboard_screen import SpecializedDashboardScreen

class Container(containers.DeclarativeContainer):
    """Container principal pour l'injection de dépendances."""
    
    # Configuration
    config = providers.Configuration()
    
    # Services
    firebase_service = providers.Singleton(
        FirebaseService,
        config=config.firebase
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
    
    # Screens
    specialized_dashboard = providers.Factory(
        SpecializedDashboardScreen,
        dashboard_controller=dashboard_controller,
        task_manager=task_manager
    )
