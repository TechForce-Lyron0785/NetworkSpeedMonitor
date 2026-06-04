from unittest.mock import patch, MagicMock
from poller.adapter import get_physical_adapter, is_vpn_name


def test_is_vpn_name():
    assert is_vpn_name("Ethernet") is False
    assert is_vpn_name("VPN - OpenVPN TAP") is True
    assert is_vpn_name("VirtualBox Host-Only") is True
    assert is_vpn_name("Wi-Fi") is False


@patch("poller.adapter.wmi.WMI")
def test_get_physical_adapter_wmi_success(mock_wmi):
    mock_adapter = MagicMock()
    mock_adapter.Name = "Realtek Ethernet"
    mock_adapter.PhysicalAdapter = True
    mock_adapter.NetEnabled = True
    mock_adapter.AdapterType = 0
    mock_adapter.PNPDeviceID = r"PCI\VEN_10EC"
    mock_wmi.return_value.Win32_NetworkAdapter.return_value = [mock_adapter]
    name, hwid = get_physical_adapter()
    assert name == "Realtek Ethernet"
    assert hwid == r"PCI\VEN_10EC"


@patch("poller.adapter.get_physical_adapter_wmi", return_value=(None, None))
@patch(
    "poller.adapter.get_physical_adapter_psutil",
    return_value=("Wi-Fi", None),
)
def test_fallback_psutil(mock_wmi, mock_psutil):
    name, hwid = get_physical_adapter()
    assert name == "Wi-Fi"
    assert hwid is None
