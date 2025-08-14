import os
from app.services.firebase_service import FirebaseService

PFX_SCREENS = "module_indexes_screens_"
PFX_MODULES = "module_indexes_modules_"
MODE = os.getenv("HC_BRANCHLESS_MODE", "prefer_new").lower()  # prefer_new | prefer_old | off

_ALIAS = {"HC-ops-master": "RPAS_ops_master", "master": "master", "develop": "develop"}

def _branch_alias():
    br = os.getenv("HC_GIT_BRANCH", "HC-ops-master")
    return _ALIAS.get(br, br.replace("-", "_"))

# ---- helpers pour compat des screens (ancien / nouveau)
def _split_old_pair(tail: str):
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
    if not coll.startswith(PFX_SCREENS):
        return None
    tail = coll[len(PFX_SCREENS):]
    mid, branch = _split_old_pair(tail)
    return (PFX_SCREENS + mid) if mid else None

def _to_old_name(coll: str):
    if not coll.startswith(PFX_SCREENS):
        return None
    tail = coll[len(PFX_SCREENS):]
    mid, branch = _split_old_pair(tail)
    if mid is not None:
        return None
    if not tail.startswith("module_"):
        return None
    return f"{coll}_{tail.replace('module_', '', 1)}"

if not getattr(FirebaseService, "_hc_branch_filter_v2", False):
    _orig = FirebaseService.get_collection

    def _patched(self, coll_name: str, *args, **kwargs):
        # --- FILTRE DÉCISIF: n'autoriser qu'UN SEUL module_indexes_modules_* (branche courante)
        if coll_name.startswith(PFX_MODULES):
            alias = _branch_alias()
            expect = f"{PFX_MODULES}{alias}"
            if coll_name != expect:
                return []  # masque les modules d'autres branches
            # sinon, on laisse passer

        if MODE != "off" and coll_name.startswith(PFX_SCREENS):
            new_name = _to_new_name(coll_name)
            old_name = _to_old_name(coll_name)

            if MODE == "prefer_new":
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

            # prefer_old
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
    FirebaseService._hc_branch_filter_v2 = True
