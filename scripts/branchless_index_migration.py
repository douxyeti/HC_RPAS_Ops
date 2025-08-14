# scripts/branchless_index_migration.py
import os, json, datetime, argparse
from app.services.firebase_service import FirebaseService
from app.services.roles_manager_service import RolesManagerService
from firebase_admin import firestore as fa

def old_coll_name(mid:str)->str:
    # Ex: mid="module_master" -> "module_indexes_screens_module_master_master"
    suffix = mid.replace("module_", "")
    return f"module_indexes_screens_{mid}_{suffix}"

def new_coll_name(mid:str)->str:
    # Nouveau schéma sans suffixe
    return f"module_indexes_screens_{mid}"

def main(apply: bool):
    fs = FirebaseService()   # initialise firebase_admin
    db = fa.client()

    roles = RolesManagerService().get_all_roles()
    if isinstance(roles, dict):
        roles = list(roles.values())

    # Détecte les modules référencés par des tâches
    module_ids = sorted({
        t.get("target_module_id")
        for r in roles for t in (r.get("tasks") or [])
        if isinstance(t, dict) and t.get("target_module_id")
    })

    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("backups", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    report = {"stamp": stamp, "apply": apply, "modules": []}
    total_to_copy = total_copied = 0

    for mid in module_ids:
        src = old_coll_name(mid)
        dst = new_coll_name(mid)

        src_docs = fs.get_collection(src) or []
        dst_docs = fs.get_collection(dst) or []
        dst_ids = {d.get("id") for d in dst_docs if isinstance(d, dict)}

        to_copy = [d for d in src_docs if isinstance(d, dict) and d.get("id") and d.get("id") not in dst_ids]

        # sauvegarde source brute
        if src_docs:
            with open(f"backups/{mid}_src_{stamp}.json","w",encoding="utf-8") as f:
                json.dump(src_docs, f, ensure_ascii=False, indent=2)

        copied = 0
        if apply and to_copy:
            for d in to_copy:
                doc_id = d.get("id")
                if not doc_id: 
                    continue
                # on recopie tel quel (y compris le champ "id" si présent)
                db.collection(dst).document(doc_id).set(d, merge=True)
                copied += 1

        report["modules"].append({
            "module_id": mid,
            "source": {"name": src, "count": len(src_docs)},
            "dest":   {"name": dst, "count_before": len(dst_docs)},
            "to_copy": len(to_copy),
            "copied": copied if apply else 0
        })
        total_to_copy += len(to_copy)
        total_copied  += copied

    report["totals"] = {"to_copy": total_to_copy, "copied": total_copied}
    out = f"reports/branchless_index_migration_{stamp}.json"
    with open(out,"w",encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"OK. Rapport: {out}")
    print(f"A copier: {total_to_copy} | Copiés: {total_copied} (apply={apply})")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--apply", action="store_true", help="Exécute réellement la copie")
    args = p.parse_args()
    main(args.apply)
