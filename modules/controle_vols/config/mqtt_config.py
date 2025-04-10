"""
Configuration MQTT pour le module Contrôle des Vols.
"""

# Configuration de base MQTT
MQTT_CONFIG = {
    'broker': 'localhost',
    'port': 1883,
    'keepalive': 60,
    'client_id': 'controle_vols_module'
}

# Topics MQTT pour le module
MQTT_TOPICS = {
    # Topics pour les vols
    'VOL_STATUS': 'hc_rpas/controle_vols/vol/status',
    'VOL_UPDATE': 'hc_rpas/controle_vols/vol/update',
    'VOL_CREATE': 'hc_rpas/controle_vols/vol/create',
    'VOL_DELETE': 'hc_rpas/controle_vols/vol/delete',
    
    # Topics pour la planification
    'PLANNING_UPDATE': 'hc_rpas/controle_vols/planning/update',
    'PLANNING_STATUS': 'hc_rpas/controle_vols/planning/status',
    
    # Topics pour les notifications
    'NOTIFICATIONS': 'hc_rpas/controle_vols/notifications',
    
    # Topics pour la synchronisation avec l'app principale
    'SYNC_REQUEST': 'hc_rpas/controle_vols/sync/request',
    'SYNC_RESPONSE': 'hc_rpas/controle_vols/sync/response'
}

# QoS par défaut pour les différents types de messages
QOS_CONFIG = {
    'status': 0,      # QoS 0 pour les mises à jour de statut fréquentes
    'update': 1,      # QoS 1 pour les mises à jour importantes
    'create': 2,      # QoS 2 pour la création de nouveaux vols
    'delete': 2,      # QoS 2 pour la suppression de vols
    'sync': 1         # QoS 1 pour la synchronisation
}
