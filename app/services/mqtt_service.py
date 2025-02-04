import paho.mqtt.client as mqtt
from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.properties import StringProperty, DictProperty
import json
import logging
import os

class MQTTService(EventDispatcher):
    """Service gérant les communications MQTT pour l'application"""
    
    connection_state = StringProperty('disconnected')
    last_message = DictProperty({})
    
    def __init__(self):
        super().__init__()
        # Configuration du client MQTT
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        
        # Topics de base
        self.base_topics = {
            'dashboard': {
                'general': 'hc_rpas/dashboard/general/#',
                'stats': 'hc_rpas/dashboard/stats/#',
                'alerts': 'hc_rpas/dashboard/alerts/#'
            },
            'roles': {
                'tasks': 'hc_rpas/roles/{role}/tasks/#',
                'notifications': 'hc_rpas/roles/{role}/notifications/#',
                'status': 'hc_rpas/roles/{role}/status/#'
            },
            'modules': {
                'operations': 'hc_rpas/modules/operations/#',
                'maintenance': 'hc_rpas/modules/maintenance/#',
                'personnel': 'hc_rpas/modules/personnel/#'
            }
        }
        
        # Callbacks pour les topics
        self.topic_callbacks = {}
        
    def connect(self, broker="localhost", port=1883):
        """Connexion au broker MQTT"""
        try:
            # Configurer les credentials si disponibles
            if 'MQTT_USERNAME' in os.environ and 'MQTT_PASSWORD' in os.environ:
                self.client.username_pw_set(
                    os.environ['MQTT_USERNAME'],
                    os.environ['MQTT_PASSWORD']
                )
            self.client.connect(broker, port)
            self.client.loop_start()
            return True
        except Exception as e:
            logging.error(f"Erreur de connexion MQTT: {str(e)}")
            return False
            
    def disconnect(self):
        """Déconnexion du broker MQTT"""
        self.client.loop_stop()
        self.client.disconnect()
        
    def on_connect(self, client, userdata, flags, rc):
        """Callback lors de la connexion"""
        if rc == 0:
            self.connection_state = 'connected'
            # Souscription aux topics généraux
            for category in self.base_topics:
                for topic in self.base_topics[category].values():
                    if '{role}' not in topic:  # Ne pas souscrire aux topics de rôle tout de suite
                        self.client.subscribe(topic)
        else:
            self.connection_state = 'error'
            
    def on_disconnect(self, client, userdata, rc):
        """Callback lors de la déconnexion"""
        self.connection_state = 'disconnected'
        
    def on_message(self, client, userdata, msg):
        """Callback lors de la réception d'un message"""
        try:
            payload = json.loads(msg.payload.decode())
            self.last_message = {
                'topic': msg.topic,
                'payload': payload
            }
            
            # Appeler les callbacks enregistrés pour ce topic
            for topic_pattern, callback in self.topic_callbacks.items():
                if mqtt.topic_matches_sub(topic_pattern, msg.topic):
                    Clock.schedule_once(lambda dt: callback(msg.topic, payload))
                    
        except json.JSONDecodeError:
            logging.error(f"Erreur de décodage JSON pour le message: {msg.payload}")
            
    def subscribe_role(self, role):
        """Souscription aux topics spécifiques à un rôle"""
        for topic in self.base_topics['roles'].values():
            formatted_topic = topic.format(role=role)
            self.client.subscribe(formatted_topic)
            
    def unsubscribe_role(self, role):
        """Désinscription des topics d'un rôle"""
        for topic in self.base_topics['roles'].values():
            formatted_topic = topic.format(role=role)
            self.client.unsubscribe(formatted_topic)
            
    def register_callback(self, topic, callback):
        """Enregistre un callback pour un topic spécifique"""
        self.topic_callbacks[topic] = callback
        
    def unregister_callback(self, topic):
        """Supprime un callback pour un topic"""
        if topic in self.topic_callbacks:
            del self.topic_callbacks[topic]
            
    def publish(self, topic, message):
        """Publication d'un message sur un topic"""
        try:
            if isinstance(message, (dict, list)):
                message = json.dumps(message)
            self.client.publish(topic, message)
            return True
        except Exception as e:
            logging.error(f"Erreur de publication MQTT: {str(e)}")
            return False
