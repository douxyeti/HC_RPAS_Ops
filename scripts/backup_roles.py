from app.services.firebase_service import FirebaseService
import json, os, datetime

def main():
    fs = FirebaseService()
    docs = fs.get_collection("roles") or []
    os.makedirs("backups", exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    outp = f"backups/roles_backup_{stamp}.json"
    with open(outp, "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)
    print(f"Sauvegarde: {outp} ({len(docs)} documents)")

if __name__ == "__main__":
    main()
