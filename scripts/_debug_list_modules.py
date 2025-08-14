from hc_rpas.module_discovery import ModuleDiscovery
md = ModuleDiscovery()  # la branche est détectée par le module (logs la montrent)
lst = None
for fn in ("get_all_modules","fetch_all_modules","list_all_modules"):
    if hasattr(md, fn):
        lst = getattr(md, fn)(); break
print("COUNT =", len(lst) if lst else 0)
for m in (lst or []):
    print(f"{m.get('id')} | branch={m.get('branch')}")
