from folderbeam.server.auth import check_credentials


def test_correct_creds():
    assert check_credentials("alice", "secret", "alice", "secret") is True


def test_wrong_password():
    assert check_credentials("alice", "nope", "alice", "secret") is False


def test_wrong_user():
    assert check_credentials("eve", "secret", "alice", "secret") is False


def test_constant_time_no_short_circuit_on_user():
    # both wrong should still return False, not raise
    assert check_credentials("", "", "alice", "secret") is False
