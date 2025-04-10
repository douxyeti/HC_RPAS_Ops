"""
Configuration générale du module Contrôle des Vols.
"""

# Informations sur l'application
APP_NAME = "Contrôle des Vols"
VERSION = "1.0.0"
DESCRIPTION = "Module de gestion et contrôle des vols RPAS"

# Configuration de l'interface
UI_CONFIG = {
    'theme_style': "Light",
    'primary_palette': "Blue",
    'accent_palette': "Amber",
}

# Configuration des rôles autorisés pour ce module
AUTHORIZED_ROLES = [
    'SUPER_ADMIN',
    'ADMIN',
    'PILOT',
    'COPILOT',
    'MISSION_SPECIALIST',
    'GROUND_OBSERVER'
]

# Configuration des permissions par rôle
ROLE_PERMISSIONS = {
    'SUPER_ADMIN': ['ALL'],
    'ADMIN': ['READ', 'WRITE', 'UPDATE', 'DELETE'],
    'PILOT': ['READ', 'WRITE', 'UPDATE'],
    'COPILOT': ['READ', 'UPDATE'],
    'MISSION_SPECIALIST': ['READ', 'UPDATE'],
    'GROUND_OBSERVER': ['READ']
}
