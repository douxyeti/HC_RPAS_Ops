import unittest
from app.services.config_service import ConfigService

class TestConfigService(unittest.TestCase):
    def setUp(self):
        self.config_service = ConfigService()
        
    def test_load_config(self):
        """Test le chargement de la configuration"""
        config = self.config_service.load_config()
        self.assertIsNotNone(config)
        self.assertIsInstance(config, dict)
        
    def test_get_firebase_config(self):
        """Test la récupération de la configuration Firebase"""
        firebase_config = self.config_service.get_firebase_config()
        required_keys = ['apiKey', 'authDomain', 'projectId', 'storageBucket', 'messagingSenderId', 'appId']
        for key in required_keys:
            self.assertIn(key, firebase_config)

if __name__ == '__main__':
    unittest.main()
