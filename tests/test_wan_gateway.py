import pytest
from folderbeam.config import Config
from folderbeam.server.wan_gateway import arm_wan_gateway, WanNotArmed


def test_disabled_by_default_is_noop():
    cfg = Config(enable_wan=False)
    # When disabled, arming is a no-op that returns None (nothing exposed).
    assert arm_wan_gateway(cfg) is None


def test_enabled_without_tls_refuses():
    cfg = Config(enable_wan=True)
    with pytest.raises(WanNotArmed):
        arm_wan_gateway(cfg)
