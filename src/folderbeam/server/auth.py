from __future__ import annotations

import hmac


def check_credentials(user: str, password: str, want_user: str, want_password: str) -> bool:
    """Compare supplied creds against the single configured credential.

    Uses hmac.compare_digest to avoid timing leaks. Single tier: a True
    result grants full read/write/delete inside the jailed root.
    """
    u_ok = hmac.compare_digest(user.encode(), want_user.encode())
    p_ok = hmac.compare_digest(password.encode(), want_password.encode())
    return u_ok and p_ok
