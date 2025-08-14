"""Configuration des composants pour les tableaux de bord dynamiques"""

from typing import Dict, Any

COMPONENT_CONFIGS: Dict[str, Dict[str, Any]] = {
    'StatusCard': {
        'class': 'app.components.status_card.StatusCard',
        'default_config': {
            'elevation': 2,
            'radius': [12, 12, 12, 12],
            'padding': [16, 16, 16, 16],
            'orientation': 'vertical'
        }
    },
    'NotificationCenter': {
        'class': 'app.components.notification_center.NotificationCenter',
        'default_config': {
            'max_items': 5,
            'auto_dismiss': True,
            'timeout': 5
        }
    },
    'RoleSelector': {
        'class': 'app.components.role_selector.RoleSelector',
        'default_config': {
            'width': 600,
            'max_height': 400,
            'radius': [24, 24, 24, 24],
            'elevation': 4
        }
    },
    'OperationsStatus': {
        'class': 'app.components.operations_status.OperationsStatus',
        'default_config': {
            'refresh_interval': 30,
            'show_details': True
        }
    },
    'MaintenanceStatus': {
        'class': 'app.components.maintenance_status.MaintenanceStatus',
        'default_config': {
            'refresh_interval': 60,
            'show_alerts': True
        }
    },
    'PersonnelStatus': {
        'class': 'app.components.personnel_status.PersonnelStatus',
        'default_config': {
            'show_availability': True,
            'show_qualifications': True
        }
    },
    'TrainingSchedule': {
        'class': 'app.components.training_schedule.TrainingSchedule',
        'default_config': {
            'days_ahead': 30,
            'show_completed': False
        }
    },
    'WeatherWidget': {
        'class': 'app.components.weather_widget.WeatherWidget',
        'default_config': {
            'refresh_interval': 300,
            'show_forecast': True
        }
    },
    'FlightLog': {
        'class': 'app.components.flight_log.FlightLog',
        'default_config': {
            'max_entries': 50,
            'auto_refresh': True
        }
    },
    'DocumentViewer': {
        'class': 'app.components.document_viewer.DocumentViewer',
        'default_config': {
            'show_preview': True,
            'cache_enabled': True
        }
    }
}
