import unittest
from unittest.mock import patch, MagicMock
from app.services.firebase_service import FirebaseService

class TestFirebaseService(unittest.TestCase):
    def setUp(self):
        self.firebase_service = FirebaseService()
        
    @patch('pyrebase.initialize_app')
    def test_initialize_firebase(self, mock_initialize):
        """Test l'initialisation de Firebase"""
        mock_initialize.return_value = MagicMock()
        self.firebase_service.initialize_firebase()
        mock_initialize.assert_called_once()
        
    @patch('app.services.firebase_service.FirebaseService.auth')
    def test_login(self, mock_auth):
        """Test la connexion utilisateur"""
        mock_auth.sign_in_with_email_and_password.return_value = {'idToken': 'test_token'}
        result = self.firebase_service.login('test@test.com', 'password')
        self.assertTrue(result['success'])
        mock_auth.sign_in_with_email_and_password.assert_called_once_with('test@test.com', 'password')

if __name__ == '__main__':
    unittest.main()
