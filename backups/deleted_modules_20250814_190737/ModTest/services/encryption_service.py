from cryptography.fernet import Fernet
import os

class EncryptionService:
    """
    Service pour chiffrer et déchiffrer des données en utilisant Fernet.
    La clé de chiffrement est stockée dans un fichier pour la persistance.
    """
    def __init__(self, key_path='secret.key'):
        """
        Initialise le service en chargeant ou en créant la clé de chiffrement.

        Args:
            key_path (str): Le chemin vers le fichier de la clé.
        """
        self.key_path = key_path
        self.key = self._load_or_generate_key()
        self.fernet = Fernet(self.key)

    def _load_or_generate_key(self):
        """
        Charge la clé depuis le fichier ou en génère une nouvelle si le fichier n'existe pas.
        """
        if os.path.exists(self.key_path):
            with open(self.key_path, 'rb') as key_file:
                return key_file.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_path, 'wb') as key_file:
                key_file.write(key)
            print(f"Nouvelle clé de chiffrement générée et sauvegardée dans {self.key_path}")
            return key

    def encrypt(self, data: str) -> bytes:
        """
        Chiffre une chaîne de caractères.

        Args:
            data (str): La chaîne à chiffrer.

        Returns:
            bytes: Les données chiffrées.
        """
        if not isinstance(data, str):
            raise TypeError("Les données à chiffrer doivent être une chaîne de caractères.")
        return self.fernet.encrypt(data.encode('utf-8'))

    def decrypt(self, encrypted_data: bytes) -> str:
        """
        Déchiffre des données.

        Args:
            encrypted_data (bytes): Les données chiffrées.

        Returns:
            str: La chaîne de caractères déchiffrée.
        """
        decrypted_data = self.fernet.decrypt(encrypted_data)
        return decrypted_data.decode('utf-8')

# Exemple d'utilisation (pour test)
if __name__ == '__main__':
    # Créer une instance du service
    encryption_service = EncryptionService()

    # Données à chiffrer
    original_text = "Ceci est un secret bien gardé."
    print(f"Texte original: {original_text}")

    # Chiffrer les données
    encrypted_text = encryption_service.encrypt(original_text)
    print(f"Texte chiffré: {encrypted_text}")

    # Déchiffrer les données
    decrypted_text = encryption_service.decrypt(encrypted_text)
    print(f"Texte déchiffré: {decrypted_text}")

    # Vérifier que le texte déchiffré correspond à l'original
    assert original_text == decrypted_text
    print("\nLe chiffrement et le déchiffrement fonctionnent correctement.")
