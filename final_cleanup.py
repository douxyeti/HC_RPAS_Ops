import os
import sys
import time
from dotenv import load_dotenv

# Add project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    import paho.mqtt.client as mqtt
except ImportError:
    print("ERREUR: Le paquet 'paho-mqtt' n'est pas installé.")
    print("Veuillez l'installer en exécutant : pip install paho-mqtt")
    sys.exit(1)

def main():
    """
    Se connecte au broker MQTT et nettoie un topic SSO spécifique et hardcodé.
    """
    print("--- Lancement du script de nettoyage FINAL et CIBLÉ ---")

    # Charger les variables d'environnement depuis le fichier .env
    dotenv_path = os.path.join(project_root, '.env')
    if not os.path.exists(dotenv_path):
        print(f"ERREUR: Fichier .env non trouvé à l'emplacement: {dotenv_path}")
        sys.exit(1)
    load_dotenv(dotenv_path=dotenv_path)

    # --- Récupération de la configuration MQTT ---
    broker = os.getenv("MQTT_BROKER")
    port = int(os.getenv("MQTT_PORT", 1883))
    username = os.getenv("MQTT_USERNAME")
    password = os.getenv("MQTT_PASSWORD")

    if not all([broker, port]):
        print("ERREUR: Configuration MQTT (BROKER, PORT) manquante dans le .env.")
        sys.exit(1)

    # --- Topic SSO Hardcodé basé sur les logs de l'application ---
    sso_topic_to_clear = "hc_rpas/sso/token/86409dd1-0983-4708-aef5-9973f8b4d806"
    print(f"Configuration chargée. Topic à nettoyer : {sso_topic_to_clear}")

    # --- Connexion et Nettoyage ---
    client_id = f"final-cleanup-script-{os.getpid()}"
    client = mqtt.Client(client_id=client_id)
    
    if username:
        client.username_pw_set(username, password)

    connection_status = {"connected": False}

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Succès: Connecté au broker MQTT.")
            connection_status["connected"] = True
        else:
            print(f"ERREUR: Connexion au broker MQTT échouée. Code de retour: {rc}")

    client.on_connect = on_connect

    try:
        print(f"Tentative de connexion à {broker}:{port}...")
        client.connect(broker, port, 60)
        client.loop_start()

        # Attendre la connexion
        timeout = 10
        start_time = time.time()
        while not connection_status["connected"] and time.time() - start_time < timeout:
            time.sleep(0.1)

        if connection_status["connected"]:
            print(f"Publication d'un message vide pour nettoyer le topic...")
            # La méthode correcte pour supprimer un message retenu est d'envoyer un payload nul.
            client.publish(sso_topic_to_clear, payload=None, qos=1, retain=True)
            print("Succès: Le message de nettoyage a été envoyé.")
            time.sleep(2) # Laisser le temps au message de partir
        else:
            print("Échec de la connexion. Le nettoyage n'a pas pu être effectué.")

    except Exception as e:
        print(f"ERREUR: Une exception est survenue: {e}")
    finally:
        client.loop_stop()
        client.disconnect()
        print("Déconnecté du broker.")
        print("--- Script terminé ---")

if __name__ == "__main__":
    main()
