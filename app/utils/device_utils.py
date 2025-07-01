import os
import uuid
from kivy.app import App

def get_or_create_device_id(app):
    """
    Récupère l'identifiant unique de l'appareil depuis le stockage local,
    ou en crée un s'il n'existe pas.

    Cette méthode est conçue pour être multiplateforme (Windows, macOS, Linux, Android, iOS)
    en utilisant le répertoire de données utilisateur fourni par Kivy.

    Args:
        app (kivy.app.App): L'instance de l'application Kivy.

    Returns:
        str: L'identifiant unique de l'appareil.
    """
    if not app:
        # Fallback si l'instance de l'app n'est pas passée
        print("[ERROR] App instance not provided to get_or_create_device_id.")
        return str(uuid.uuid4())

    device_id_file = os.path.join(app.user_data_dir, 'device_id.txt')

    if os.path.exists(device_id_file):
        with open(device_id_file, 'r') as f:
            device_id = f.read().strip()
            if device_id:
                return device_id

    # Si le fichier n'existe pas, est vide, ou si la lecture a échoué,
    # on en génère un nouveau.
    device_id = str(uuid.uuid4())
    try:
        with open(device_id_file, 'w') as f:
            f.write(device_id)
    except IOError as e:
        # Gérer le cas où l'écriture échoue, par exemple, problème de permissions
        # Dans ce cas, on retourne un ID non persistant pour la session actuelle.
        print(f"[ERROR] Could not write device ID to {device_id_file}: {e}")
        return str(uuid.uuid4()) # Fallback to a non-persistent ID

    return device_id
