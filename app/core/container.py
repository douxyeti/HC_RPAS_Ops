import logging
from dependency_injector import containers, providers
from app.services.firebase_service import FirebaseService
from app.services.task_manager_service import TaskManagerService
from app.services.procedures_manager_service import ProceduresManagerService
from app.controllers.dashboard_controller import DashboardController
from app.views.screens.specialized_dashboard_screen import SpecializedDashboardScreen
from app.views.screens.procedures_manager_screen import ProceduresManagerScreen
from app.services.config_service import ConfigService
from app.utils.logger import setup_logger

class Container(containers.DeclarativeContainer):
    """Container principal pour l'injection de dépendances."""
    
    # Configuration
    config = providers.Configuration()
    
    # Logger
    logger = providers.Singleton(
        setup_logger,
        name="hc_rpas",
        level=logging.INFO,
        log_to_file=True
    )
    
    # Services
    config_service = providers.Singleton(ConfigService)
    
    firebase_service = providers.Singleton(
        FirebaseService
    )
    
    task_manager = providers.Singleton(
        TaskManagerService,
        firebase_service=firebase_service
    )
    
    procedures_manager = providers.Callable(
        ProceduresManagerService
    )
    
    # Controllers
    dashboard_controller = providers.Factory(
        DashboardController,
        task_manager=task_manager,
        firebase_service=firebase_service
    )
    
    # Screens
    procedures_manager_screen = providers.Factory(
        ProceduresManagerScreen,
        procedures_manager_service=procedures_manager
    )
