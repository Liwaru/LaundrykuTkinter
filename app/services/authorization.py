"""Role permissions for the desktop shell and service layer."""

ROLE_NAMES = {
    1: "Pelanggan",
    2: "Kasir/Admin",
    3: "Staff Laundry",
    4: "Owner",
}

# Dashboard is a landing page for every role. The actual global dashboard query
# is separately restricted to cashier/admin and owner in the service layer.
ROLE_MENUS = {
    1: ("Transaksi", "Layanan", "Pembayaran"),
    2: ("Transaksi", "Pelanggan", "Layanan", "Pembayaran", "Laporan"),
    3: ("Transaksi",),
    4: ("Transaksi", "Pelanggan", "Layanan", "Pembayaran", "Laporan", "Pengguna"),
}


def level_of(user):
    """Read a trusted session's role level; missing/invalid sessions fail closed."""
    try:
        return int(user.level)
    except (AttributeError, TypeError, ValueError):
        return None


def menus_for(user):
    level = level_of(user)
    return ROLE_MENUS.get(level, ())


def can_access(user, page):
    if level_of(user) not in ROLE_NAMES:
        return False
    if page == "Dashboard":
        return True
    return page in menus_for(user)


def require_role(user, allowed_levels):
    """Guard privileged service operations independently of visible menus."""
    level = level_of(user)
    if level not in allowed_levels:
        raise PermissionError("Akun tidak memiliki izin untuk operasi ini.")
