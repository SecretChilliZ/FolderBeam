"""
STERILISED WAN EXPOSURE SEAM. Inert by default. Do not arm casually.

This module is the single, isolated place where future internet (WAN)
exposure code will live. It is intentionally non-functional right now so
folderbeam has ZERO public attack surface until someone deliberately and
correctly enables it.

To un-sterilise later you MUST add, inside _build_public_gateway():
  1. TLS termination (real certificate, not self-signed for anything shared).
  2. Hashed credential storage (drop the plaintext config password path).
  3. Rate limiting / fail2ban-style lockout on the auth endpoint.
  4. An explicit, logged opt-in (config.enable_wan True is necessary, not
     sufficient: the checks below must also pass).

Until all of that exists, arm_wan_gateway() refuses to expose anything.
"""
from __future__ import annotations

from ..config import Config


class WanNotArmed(RuntimeError):
    """Raised when WAN exposure is requested but prerequisites are unmet."""


def arm_wan_gateway(cfg: Config):
    """Entry point the panel would call to expose folderbeam to the internet.

    Returns None (no-op) while disabled. Refuses loudly if enabled before
    the security prerequisites exist. Never silently exposes anything.
    """
    if not cfg.enable_wan:
        return None  # inert: nothing bound, nothing exposed

    # Prerequisites not implemented yet. This is the sterilisation barrier.
    raise WanNotArmed(
        "WAN exposure is not implemented. Required before arming: TLS, "
        "hashed credentials, rate limiting. See module docstring. Refusing "
        "to expose the folder over the public internet."
    )


def _build_public_gateway(cfg: Config):  # pragma: no cover - intentional stub
    """FUTURE drop-in point. Build the TLS + hardened-auth public listener
    here. Leave empty until the prerequisites in the module docstring are met.
    """
    raise NotImplementedError
