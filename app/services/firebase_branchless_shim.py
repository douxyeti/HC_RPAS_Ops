import os
from app.services.firebase_service import FirebaseService

PFX = "module_indexes_screens_"
MODE = os.getenv("HC_BRANCHLESS_MODE", "prefer_new").lower()  # prefer_new | prefer_old | off

def _split_old_pair(tail: str):
    """
    tail = '{mid}_{branch}', on cherche une position '_' telle que
    branch == mid.replace('module_', '', 1).
    Retourne (mid, branch) si trouvé, sinon (None, None).
    """
    if not tail.startswith("module_"):
        return None, None
    for i, ch in enumerate(tail):
        if ch != "_":
            continue
        mid = tail[:i]
        branch = tail[i+1:]
        if branch == mid.replace("module_", "", 1):
            return mid, branch
    return None, None

def _to_new_name(coll: str):
    if not coll.startswith(PFX):
        return None
    tail = coll[len(PFX):]
    mid, branch = _split_old_pair(tail)
    return (PFX + mid) if mid else None

def _to_old_name(coll: str):
    # Ne calcule l'ancien nom QUE si coll est au format "nouveau"
    if not coll.startswith(PFX):
        return None
    tail = coll[len(PFX):]

    # Si c'est déjà au format ancien ({mid}_{branch}), ne rien faire
    mid, branch = _split_old_pair(tail)
    if mid is not None:
        return None

    if not tail.startswith("module_"):
        return None

    # Ajoute une seule fois le suffixe
    return f"{coll}_{tail.replace('module_', '', 1)}"

if not getattr(FirebaseService, "_branchless_patched", False):
    _orig = FirebaseService.get_collection

    def _patched(self, coll_name: str, *args, **kwargs):
        if MODE == "off":
            return _orig(self, coll_name, *args, **kwargs) or []

        if coll_name.startswith(PFX):
            new_name = _to_new_name(coll_name)  # si ancien -> nom nouveau
            old_name = _to_old_name(coll_name)  # si nouveau -> nom ancien

            if MODE == "prefer_new":
                # 1) nouveau 2) original 3) ancien
                if new_name:
                    docs = _orig(self, new_name, *args, **kwargs) or []
                    if docs: return docs
                    docs = _orig(self, coll_name, *args, **kwargs) or []
                    if docs: return docs
                if old_name:
                    docs = _orig(self, coll_name, *args, **kwargs) or []
                    if docs: return docs
                    return _orig(self, old_name, *args, **kwargs) or []
                return _orig(self, coll_name, *args, **kwargs) or []

            # MODE == prefer_old
            if old_name:
                docs = _orig(self, old_name, *args, **kwargs) or []
                if docs: return docs
                return _orig(self, coll_name, *args, **kwargs) or []
            if new_name:
                docs = _orig(self, coll_name, *args, **kwargs) or []
                if docs: return docs
                return _orig(self, new_name, *args, **kwargs) or []
            return _orig(self, coll_name, *args, **kwargs) or []

        return _orig(self, coll_name, *args, **kwargs) or []

    FirebaseService.get_collection = _patched
    FirebaseService._branchless_patched = True
