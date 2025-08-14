# app/services/module_picker_filter_shim.py
import os

# essaie d'importer le ModuleDiscovery utilisé par les logs
try:
    from hc_rpas import module_discovery as md
except Exception:
    md = None

# petites aides pour branch alias
_ALIAS_MAP = {
    "HC-ops-master": "RPAS_ops_master",
    "master": "master",
    "develop": "develop",
}

def _current_alias():
    # idéalement, ta détection de branche place déjà une info exploitable;
    # on prend la branche git si disponible, sinon on tombe sur 'HC-ops-master'
    br = os.getenv("HC_GIT_BRANCH", "HC-ops-master")
    return _ALIAS_MAP.get(br, br.replace("-", "_"))

def _keep_current_branch(items):
    alias = _current_alias()
    out = []
    for m in (items or []):
        # tolère différents schémas {branch,id,module_id}
        br = (isinstance(m, dict) and (m.get("branch") or "")) or ""
        mid = (isinstance(m, dict) and (m.get("id") or m.get("module_id") or "")) or ""
        if br == alias or mid == f"module_{alias}":
            out.append(m)
    # si on filtre tout (era d'anciennes données), on rend la liste originale
    return out or (items or [])

if md and hasattr(md, "ModuleDiscovery"):
    # on patch le/les points d'entrée communs
    for fn_name in ("get_all_modules", "fetch_all_modules", "list_all_modules"):
        if hasattr(md.ModuleDiscovery, fn_name):
            _orig = getattr(md.ModuleDiscovery, fn_name)
            def _patched(self, *a, __orig=_orig, **k):
                items = __orig(self, *a, **k)
                return _keep_current_branch(items)
            setattr(md.ModuleDiscovery, fn_name, _patched)
