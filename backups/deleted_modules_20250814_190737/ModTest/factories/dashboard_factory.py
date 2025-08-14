"""Factory pour créer des tableaux de bord dynamiques selon le rôle"""

from typing import Dict, List, Any, Optional
from ..services.config_service import ConfigService
from ..config.components import COMPONENT_CONFIGS
import importlib

class DashboardFactory:
    """Factory pour créer des tableaux de bord dynamiques selon le rôle"""
    
    def __init__(self):
        self.config = ConfigService()
        
    def create_dashboard(self, role: str) -> Dict[str, Any]:
        """Crée un tableau de bord pour un rôle spécifique
        
        Args:
            role: Identifiant du rôle (ex: 'pilot_command')
            
        Returns:
            Dict contenant la configuration du tableau de bord
        """
        # Récupérer les permissions du rôle
        role_config = self.config.get_config(f'interface.roles.{role}')
        if not role_config:
            raise ValueError(f"Configuration non trouvée pour le rôle: {role}")
            
        permissions = role_config.get('permissions', [])
        
        # Construire le tableau de bord
        dashboard = {
            'title': f"Tableau de bord - {role_config['name']}",
            'layout': self._get_layout_for_permissions(permissions),
            'components': self._get_components_for_permissions(permissions),
            'actions': self._get_actions_for_permissions(permissions),
            'tasks': self._get_tasks_for_permissions(permissions)
        }
        
        return dashboard
    
    def _get_layout_for_permissions(self, permissions: List[str]) -> Dict[str, List[str]]:
        """Détermine la disposition des composants selon les permissions"""
        layout = {
            'top_bar': ['role_selector', 'notifications'],
            'main_content': [],
            'side_panel': []
        }
        
        # Composants principaux selon les permissions
        if 'operations.view' in permissions:
            layout['main_content'].extend(['operations_status', 'flight_log'])
            layout['side_panel'].append('weather_widget')
            
        if 'maintenance.view' in permissions:
            layout['main_content'].append('maintenance_status')
            
        if 'personnel.view' in permissions:
            layout['side_panel'].append('personnel_status')
            
        if 'formation.view' in permissions:
            layout['side_panel'].append('training_schedule')
            
        if 'documents.view' in permissions:
            layout['main_content'].append('document_viewer')
            
        return layout
    
    def _get_components_for_permissions(self, permissions: List[str]) -> Dict[str, Dict[str, Any]]:
        """Retourne les composants activés selon les permissions"""
        components = {
            'role_selector': self._create_component_config('RoleSelector'),
            'notifications': self._create_component_config('NotificationCenter')
        }
        
        # Composants conditionnels selon les permissions
        if 'operations.view' in permissions:
            components['operations_status'] = self._create_component_config('OperationsStatus')
            components['flight_log'] = self._create_component_config('FlightLog')
            components['weather_widget'] = self._create_component_config('WeatherWidget')
            
        if 'maintenance.view' in permissions:
            components['maintenance_status'] = self._create_component_config('MaintenanceStatus')
            
        if 'personnel.view' in permissions:
            components['personnel_status'] = self._create_component_config('PersonnelStatus')
            
        if 'formation.view' in permissions:
            components['training_schedule'] = self._create_component_config('TrainingSchedule')
            
        if 'documents.view' in permissions:
            components['document_viewer'] = self._create_component_config('DocumentViewer')
            
        return components
    
    def _create_component_config(self, component_type: str) -> Dict[str, Any]:
        """Crée la configuration d'un composant"""
        if component_type not in COMPONENT_CONFIGS:
            raise ValueError(f"Type de composant non trouvé: {component_type}")
            
        config = COMPONENT_CONFIGS[component_type]
        return {
            'type': config['class'],
            'config': config['default_config'].copy()
        }
    
    def _get_actions_for_permissions(self, permissions: List[str]) -> List[Dict[str, str]]:
        """Retourne les actions disponibles selon les permissions"""
        actions = []
        
        # Actions pour les opérations
        if 'operations.edit' in permissions:
            actions.extend([
                {
                    'id': 'new_operation',
                    'label': 'Nouvelle Opération',
                    'icon': 'plus',
                    'action': 'create_operation'
                },
                {
                    'id': 'edit_operation',
                    'label': 'Modifier Opération',
                    'icon': 'pencil',
                    'action': 'edit_operation'
                }
            ])
            
        # Actions pour la maintenance
        if 'maintenance.edit' in permissions:
            actions.extend([
                {
                    'id': 'new_maintenance',
                    'label': 'Nouvelle Maintenance',
                    'icon': 'wrench',
                    'action': 'create_maintenance'
                },
                {
                    'id': 'schedule_maintenance',
                    'label': 'Planifier Maintenance',
                    'icon': 'calendar',
                    'action': 'schedule_maintenance'
                }
            ])
            
        return actions
    
    def _get_tasks_for_permissions(self, permissions: List[str]) -> List[Dict[str, str]]:
        """Retourne les tâches disponibles selon les permissions"""
        tasks = []
        
        # Tâches pour les opérations
        if 'operations.view' in permissions:
            tasks.extend([
                {
                    'id': 'flight_briefing',
                    'label': 'Briefing de Vol',
                    'module': 'briefing',
                    'icon': 'clipboard-list'
                },
                {
                    'id': 'weather_check',
                    'label': 'Vérification Météo',
                    'module': 'weather',
                    'icon': 'weather-cloudy'
                }
            ])
            
        # Tâches pour la maintenance
        if 'maintenance.view' in permissions:
            tasks.extend([
                {
                    'id': 'maintenance_checklist',
                    'label': 'Liste de Vérification',
                    'module': 'maintenance',
                    'icon': 'clipboard-check'
                },
                {
                    'id': 'equipment_status',
                    'label': 'État des Équipements',
                    'module': 'equipment',
                    'icon': 'drone'
                }
            ])
            
        return tasks
    
    def create_component_instance(self, component_type: str, config: Dict[str, Any]) -> Any:
        """Crée une instance d'un composant
        
        Args:
            component_type: Type du composant (chemin complet de la classe)
            config: Configuration du composant
            
        Returns:
            Instance du composant
        """
        try:
            # Séparer le module et la classe
            module_path, class_name = component_type.rsplit('.', 1)
            
            # Importer le module
            module = importlib.import_module(module_path)
            
            # Obtenir la classe
            component_class = getattr(module, class_name)
            
            # Créer l'instance avec la configuration
            return component_class(**config)
            
        except (ImportError, AttributeError) as e:
            raise ImportError(f"Impossible de charger le composant {component_type}: {str(e)}")
