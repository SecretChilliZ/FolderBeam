from folderbeam.netutil import lan_ip, client_urls


def test_lan_ip_is_string():
    ip = lan_ip()
    assert isinstance(ip, str)
    assert ip.count(".") == 3


def test_client_urls():
    urls = client_urls("192.168.1.50", dav_port=8080, ui_port=8081)
    assert urls["webdav"] == "http://192.168.1.50:8080/"
    assert urls["browser"] == "http://192.168.1.50:8081/"
