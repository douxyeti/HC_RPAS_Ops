import os
import sys
import time
from dotenv import load_dotenv

# Add project root to the Python path to allow importing app modules
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    import paho.mqtt.client as mqtt
except ImportError:
    print("ERREUR: Le paquet 'paho-mqtt' n'est pas installé.")
    print("Veuillez l'installer en exécutant : pip install paho-mqtt")
    sys.exit(1)

import uuid

def get_standalone_device_id():
    """
    Récupère ou crée un device_id de manière autonome.
    Logique copiée de app.utils.device_utils.get_or_create_device_id
    """
    home_dir = os.path.expanduser("~")
    app_data_dir = os.path.join(home_dir, '.hc_rpas_ops')
    device_id_file = os.path.join(app_data_dir, '.device_id')

    os.makedirs(app_data_dir, exist_ok=True)

    if os.path.exists(device_id_file):
        with open(device_id_file, 'r') as f:
            device_id = f.read().strip()
        if device_id:
            return device_id

    # Si le fichier n'existe pas, est vide, ou en cas d'erreur, en créer un nouveau
    device_id = str(uuid.uuid4())
    with open(device_id_file, 'w') as f:
        f.write(device_id)
    return device_id

def main():
    """
    Se connecte au broker MQTT et nettoie le message SSO retenu.
    """
    print("--- Lancement du script de nettoyage du token SSO ---")

    # Load environment variables from .env file at the project root
    dotenv_path = os.path.join(project_root, '.env')
    if not os.path.exists(dotenv_path):
        print(f"ERREUR: Fichier .env non trouvé à l'emplacement: {dotenv_path}")
        sys.exit(1)
    load_dotenv(dotenv_path=dotenv_path)

    # --- Récupération de la configuration ---
    broker = os.getenv("MQTT_BROKER")
    port = int(os.getenv("MQTT_PORT", 1883))
    username = os.getenv("MQTT_USERNAME")
    password = os.getenv("MQTT_PASSWORD")
    # Forcer le bon template pour éviter les erreurs de configuration du .env
    sso_topic_template = "hc_rpas/sso/token/{}"

    if not all([broker, port]):
        print("ERREUR: Configuration MQTT de base (BROKER, PORT) manquante dans le fichier .env.")
        sys.exit(1)
        
    print("Configuration MQTT chargée.")

    # --- Construction du topic SSO dynamique ---
    try:
        device_id = get_standalone_device_id()
        sso_topic = sso_topic_template.format(device_id)
        print(f"Topic SSO à nettoyer: {sso_topic}")
    except Exception as e:
        print(f"ERREUR: Impossible de déterminer le topic SSO: {e}")
        sys.exit(1)

    # --- Connexion et nettoyage MQTT ---
    client_id = f"sso-cleanup-script-{os.getpid()}"
    client = mqtt.Client(client_id=client_id)
    
    if username:
        client.username_pw_set(username, password)

    connection_status = {"connected": False, "rc": -1}

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Succès: Connecté au broker MQTT.")
            connection_status["connected"] = True
        else:
            print(f"ERREUR: Connexion au broker MQTT échouée. Code: {rc}")
            connection_status["rc"] = rc
        
    client.on_connect = on_connect

    try:
        print(f"Connexion à {broker}:{port}...")
        client.connect(broker, port, 60)
        
        client.loop_start()
        # Attendre la connexion (avec un timeout)
        timeout = 5
        start_time = time.time()
        while not connection_status["connected"] and time.time() - start_time < timeout:
            if connection_status["rc"] != -1: # Connection failed
                break
            time.sleep(0.1)
        
        if connection_status["connected"]:
            print(f"Publication d'un message vide (retenu) pour nettoyer le topic...")
            # Publier un message vide avec retain=True pour effacer le message retenu
            client.publish(sso_topic, payload="", qos=1, retain=True)
            print("Succès: Message de nettoyage envoyé.")
            # Attendre un court instant pour s'assurer que le message est parti
            time.sleep(2)
        else:
            print("Abandon: La publication a été annulée car la connexion a échoué.")

    except Exception as e:
        print(f"ERREUR: Une exception est survenue durant l'opération MQTT: {e}")
    finally:
        client.loop_stop()
        client.disconnect()
        print("Déconnecté du broker MQTT.")
        print("--- Script terminé ---")

if __name__ == "__main__":
    main()
