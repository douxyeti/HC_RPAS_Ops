import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app.services.firebase_service import FirebaseService

def list_all_collections():
    """
    Connects to Firestore and lists all top-level collections.
    """
    print("Initializing Firebase Service...")
    # This will use the gcloud config, which should be set to the restored project.
    try:
        firebase_service = FirebaseService()
        db = firebase_service.db
        print("Firebase Service initialized successfully.")
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        return

    print("\n--- Listing all top-level collections ---")
    collections = db.collections()
    collection_names = [col.id for col in collections]

    if not collection_names:
        print("No collections found in the database.")
    else:
        print("Found the following collections:")
        for name in collection_names:
            print(f"- {name}")

    print("\n--- Check complete ---")

if __name__ == "__main__":
    list_all_collections()
