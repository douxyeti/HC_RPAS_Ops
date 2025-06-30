import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app.services.firebase_service import FirebaseService

def inspect_pilots_collection():
    """
    Connects to Firestore and inspects the 'pilots' collection.
    """
    print("Initializing Firebase Service for restored project...")
    # This will use the gcloud config, which should be set to 'highcloud-rpas-ecosystem-86a4f'
    try:
        firebase_service = FirebaseService()
        db = firebase_service.db
        print("Firebase Service initialized successfully.")
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        return

    print("\n--- Inspecting 'pilots' collection (limit 5 documents) ---")
    pilots_ref = db.collection('pilots')
    # Let's try to find the specific user we've been testing with
    specific_user_id = "Ta5xjw6gsShzoaXNYS5SriTkbAi2"
    doc_ref = pilots_ref.document(specific_user_id)
    doc = doc_ref.get()

    if doc.exists:
        print(f"Found document for specific user '{specific_user_id}':")
        print(f"  [Document ID]: {doc.id}")
        print(f"  Data: {doc.to_dict()}")
    else:
        print(f"Document for specific user '{specific_user_id}' not found.")
        print("\nShowing first 5 documents instead:")
        docs = pilots_ref.limit(5).stream()
        doc_count = 0
        for doc in docs:
            doc_count += 1
            print(f"\n[Document ID]: {doc.id}")
            print(f"  Data: {doc.to_dict()}")
        if doc_count == 0:
            print("The 'pilots' collection appears to be empty.")


    print("\n--- Inspection complete ---")

if __name__ == "__main__":
    inspect_pilots_collection()
