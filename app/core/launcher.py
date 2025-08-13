import subprocess
import sys
from typing import Optional


def launch_module(mod_name: str) -> Optional[subprocess.Popen]:
    """
    Lance un module comme package Python: modules.<mod_name>.main
    Aucun argument transmis.
    Retourne l'objet Popen, ou None si échec.
    """
    try:
        return subprocess.Popen([sys.executable, "-m", f"modules.{mod_name}.main"])
    except Exception:
        return None
