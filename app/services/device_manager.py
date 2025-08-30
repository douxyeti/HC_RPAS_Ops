import os
import json
import platform
import socket
import hashlib
import uuid
from typing import Dict, Optional, List
from datetime import datetime


class DeviceManager:
    """Gestionnaire de sécurité pour les devices autorisés SSO."""

    def __init__(self, config_dir: str = None):
        """Initialise le gestionnaire de devices."""
        if config_dir is None:
            # Répertoire par défaut multiplateforme
            home = os.path.expanduser("~")
            if platform.system() == "Windows":
                config_dir = os.path.join(home, "AppData", "Local", "HC_RPAS_Ops")
            else:
                config_dir = os.path.join(home, ".hc_rpas_ops")

        self.config_dir = config_dir
        self.devices_file = os.path.join(config_dir, "authorized_devices.json")
        self.current_device_file = os.path.join(config_dir, "current_device.json")

        # Créer le répertoire s'il n'existe pas
        os.makedirs(config_dir, exist_ok=True)

        # Charger les devices autorisés
        self.authorized_devices = self._load_authorized_devices()

    def generate_device_fingerprint(self) -> Dict[str, str]:
        """Génère un fingerprint unique pour ce device."""
        try:
            system = platform.system()
            machine = platform.machine()
            hostname = socket.gethostname()

            # Combinaison unique basée sur hardware + système
            device_info = f"{system}-{machine}-{hostname}-{uuid.getnode()}"
            fingerprint = hashlib.sha256(device_info.encode()).hexdigest()[:16]

            return {
                'fingerprint': fingerprint,
                'system': system,
                'machine': machine,
                'hostname': hostname,
                'mac_hash': hashlib.sha256(str(uuid.getnode()).encode()).hexdigest()[:8],
                'created_at': datetime.now().isoformat(),
                'is_authorized': False
            }
        except Exception as e:
            # Fallback sur UUID pur si échec
            fallback_id = str(uuid.uuid4())
            return {
                'fingerprint': hashlib.sha256(fallback_id.encode()).hexdigest()[:16],
                'system': 'unknown',
                'machine': 'unknown',
                'hostname': 'unknown',
                'mac_hash': 'unknown',
                'created_at': datetime.now().isoformat(),
                'is_authorized': False,
                'fallback': True
            }

    def get_current_device(self) -> Dict[str, str]:
        """Récupère ou crée l'identifiant du device actuel."""
        if os.path.exists(self.current_device_file):
            try:
                with open(self.current_device_file, 'r', encoding='utf-8') as f:
                    device = json.load(f)
                return device
            except Exception:
                pass

        # Générer un nouveau device
        device = self.generate_device_fingerprint()

        # Sauvegarder
        try:
            with open(self.current_device_file, 'w', encoding='utf-8') as f:
                json.dump(device, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur sauvegarde device: {e}")

        return device

    def _load_authorized_devices(self) -> Dict[str, Dict]:
        """Charge la liste des devices autorisés."""
        if not os.path.exists(self.devices_file):
            return {}

        try:
            with open(self.devices_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_authorized_devices(self):
        """Sauvegarde la liste des devices autorisés."""
        try:
            with open(self.devices_file, 'w', encoding='utf-8') as f:
                json.dump(self.authorized_devices, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur sauvegarde devices autorisés: {e}")

    def authorize_device(self, device_fingerprint: str, device_name: str = None) -> bool:
        """Autorise un device pour le SSO."""
        try:
            device_info = {
                'fingerprint': device_fingerprint,
                'name': device_name or f"Device-{device_fingerprint[:8]}",
                'authorized_at': datetime.now().isoformat(),
                'authorized_by': 'system'  # Peut être étendu pour tracking utilisateur
            }

            self.authorized_devices[device_fingerprint] = device_info
            self._save_authorized_devices()
            return True
        except Exception as e:
            print(f"Erreur autorisation device: {e}")
            return False

    def revoke_device(self, device_fingerprint: str) -> bool:
        """Révoque l'autorisation d'un device."""
        if device_fingerprint in self.authorized_devices:
            del self.authorized_devices[device_fingerprint]
            self._save_authorized_devices()
            return True
        return False

    def is_device_authorized(self, device_fingerprint: str) -> bool:
        """Vérifie si un device est autorisé."""
        return device_fingerprint in self.authorized_devices

    def get_authorized_devices(self) -> List[Dict]:
        """Retourne la liste des devices autorisés."""
        return list(self.authorized_devices.values())

    def is_first_device(self) -> bool:
        """Vérifie si c'est le premier device (pour auto-autorisation)."""
        return len(self.authorized_devices) == 0

    def auto_authorize_first_device(self) -> bool:
        """Auto-autorise le premier device détecté."""
        if self.is_first_device():
            current_device = self.get_current_device()
            device_name = f"{current_device['system']} {current_device['hostname']}"
            return self.authorize_device(current_device['fingerprint'], device_name)
        return False


# Instance globale
_device_manager = None

def get_device_manager() -> DeviceManager:
    """Retourne l'instance unique du DeviceManager."""
    global _device_manager
    if _device_manager is None:
        _device_manager = DeviceManager()
    return _device_manager
