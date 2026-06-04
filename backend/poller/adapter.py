"""
Physical network adapter detection for Windows.
Uses WMI as primary, psutil as fallback.
Filters out VPN/virtual adapters.
"""

import logging
import psutil
import wmi  # type: ignore[import-untyped]

logger = logging.getLogger(__name__)

# Keywords that indicate VPN or virtual adapters
VPN_KEYWORDS = [
    "vpn",
    "virtual",
    "tap",
    "tun",
    "openvpn",
    "wireguard",
    "pia",
    "nord",
    "expressvpn",
    "cyberghost",
    "protonvpn",
    "multilayer",
    "ndis virtual",
    "hyper-v",
    "vmware",
    "virtualbox",
]


def is_vpn_name(name: str) -> bool:
    """Check if adapter name contains VPN/virtual keywords."""
    lower_name = name.lower()
    return any(keyword in lower_name for keyword in VPN_KEYWORDS)


def get_physical_adapter_wmi() -> tuple:
    """
    Query WMI for physical adapters.
    Returns (adapter_name, hardware_id) or (None, None).
    """
    try:
        c = wmi.WMI()
        # Query Win32_NetworkAdapter
        # Filters: NetEnabled=True, PhysicalAdapter=True (Windows 8+),
        # AdapterType in (0=Ethernet, 6=some physical, 9=Wireless, 71=Wi-Fi)
        adapters = c.Win32_NetworkAdapter(
            NetEnabled=True, PhysicalAdapter=True
        )
        for adapter in adapters:
            name = adapter.Name
            if not name:
                continue
            if is_vpn_name(name):
                continue
            # Check AdapterType
            atype = adapter.AdapterType
            # 0=Ethernet, 6=some wired, 9=Wireless
            if atype not in (0, 6, 9, 71):
                continue
            # Also check if it has a default gateway (optional: later)
            return name, adapter.PNPDeviceID
    except Exception as e:
        logger.warning(f"WMI query failed: {e}. Falling back to psutil.")
    return None, None


def get_physical_adapter_psutil() -> tuple:
    """
    Fallback: use psutil.net_if_stats() and name filtering.
    Returns (adapter_name, None) because hardware_id not available.
    """
    try:
        stats = psutil.net_if_stats()
        addrs = psutil.net_if_addrs()
        for name, stat in stats.items():
            if not stat.isup:
                continue
            if is_vpn_name(name):
                continue
            # Must have at least one IPv4 address (not just loopback)
            has_ipv4 = any(addr.family == 2 for addr in addrs.get(name, []))
            if not has_ipv4:
                continue
            # Reasonable speed (virtual often shows 0 or 1)
            if stat.speed < 10:  # less than 10 Mbps -> unlikely physical
                continue
            return name, None
    except Exception as e:
        logger.error(f"psutil fallback failed: {e}")
    return None, None


def get_physical_adapter() -> tuple:
    """
    Main function: returns (adapter_name, hardware_id) of the physical adapter.
    Returns (None, None) if none found.
    """
    name, hwid = get_physical_adapter_wmi()
    if name:
        logger.info(f"Detected physical adapter via WMI: {name}")
        return name, hwid

    name, _ = get_physical_adapter_psutil()
    if name:
        logger.info(f"Detected physical adapter via psutil fallback: {name}")
        return name, None

    logger.warning("No physical adapter found.")
    return None, None


# Quick test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    name, hwid = get_physical_adapter()
    print(f"Adapter: {name}, HWID: {hwid}")
