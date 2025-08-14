from typing import Dict, Any
import json
import os

def load_config() -> Dict[str, Any]:
    """
    Charge la configuration de l'application.
    
    Returns:
        Dict[str, Any]: Configuration de l'application
    """
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config.json')
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    return {
        'firebase': {
            'credentials_path': config.get('firebase', {}).get('credentials_path'),
            'api_key': config.get('firebase', {}).get('apiKey'),
            'auth_domain': config.get('firebase', {}).get('authDomain'),
            'project_id': config.get('firebase', {}).get('projectId'),
            'storage_bucket': config.get('firebase', {}).get('storageBucket'),
            'messaging_sender_id': config.get('firebase', {}).get('messagingSenderId'),
            'app_id': config.get('firebase', {}).get('appId')
        }
    }
