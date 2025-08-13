import time
from typing import Any, Dict, Optional


def create_invocation(
    firebase,
    user_id: str,
    module: str,
    route: str,
    params: Dict[str, Any],
    ttl_sec: int = 120,
) -> None:
    """
    Crée une invocation single-use pour {user_id}+{module}.
    Écrit dans la collection invocations_{user_id} le document {user_id}_{module}.
    Champs:
      - route: str
      - params: dict
      - expires_at: int (epoch seconds)
    """
    doc_id = f"{user_id}_{module}"
    expires_at = int(time.time()) + int(ttl_sec)
    data = {
        "route": route,
        "params": params or {},
        "expires_at": expires_at,
    }
    firebase.set_data_with_id(f"invocations_{user_id}", doc_id, data)


def fetch_and_consume_invocation(
    firebase,
    user_id: str,
    module: str,
) -> Optional[Dict[str, Any]]:
    """Lit et supprime immédiatement une invocation si non expirée."""
    doc_id = f"{user_id}_{module}"
    path = f"invocations_{user_id}/{doc_id}"
    data = firebase.get_data(path)
    if not data:
        return None
    if "expires_at" in data and int(time.time()) > int(data["expires_at"]):
        firebase.delete_data(path)
        return None
    firebase.delete_data(path)
    return data
