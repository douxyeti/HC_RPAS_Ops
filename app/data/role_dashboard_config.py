"""Configuration des tableaux de bord par rôle"""

ROLE_DASHBOARD_CONFIG = {
    # Tableau de bord par défaut (tous les modules)
    "default": [
        "Cadre Documentaire",
        "Contrôle Opérationnel",
        "Assurance Qualité",
        "Gestion Sécurité",
        "Formation",
        "Maintenance",
        "Contrôle Maintenance",
        "Navigation-Détection",
        "Contrôle Aérien",
        "Gestion Personnel",
        "Contrôle Sites",
        "Gestion Flotte"
    ],
    
    # Commandant de bord
    "pilot_command": [
        "Contrôle Opérationnel",
        "Gestion Sécurité",
        "Navigation-Détection",
        "Contrôle Aérien",
        "Gestion Flotte"
    ],
    
    # Responsable maintenance
    "maintenance_manager": [
        "Maintenance",
        "Contrôle Maintenance",
        "Gestion Flotte",
        "Assurance Qualité"
    ],
    
    # Responsable formation
    "training_manager": [
        "Formation",
        "Cadre Documentaire",
        "Assurance Qualité"
    ],
    
    # Responsable qualité
    "quality_manager": [
        "Assurance Qualité",
        "Cadre Documentaire",
        "Gestion Sécurité",
        "Formation"
    ],
    
    # Responsable sécurité
    "safety_manager": [
        "Gestion Sécurité",
        "Contrôle Sites",
        "Assurance Qualité",
        "Formation"
    ],
    
    # Responsable personnel
    "personnel_manager": [
        "Gestion Personnel",
        "Formation",
        "Assurance Qualité"
    ]
}
