"""MariaDB connection helpers for the existing LaundryKu database."""

import os
from pathlib import Path

try:
    import mysql.connector
    from mysql.connector import Error
except ImportError:  # Keep the Tkinter UI launchable before dependencies are installed.
    mysql = None

    class Error(Exception):
        """Fallback exception type while mysql-connector-python is unavailable."""

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(path):
        """Small .env reader fallback; supports simple KEY=VALUE lines."""
        path = Path(path)
        if not path.is_file():
            return False
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key, value = key.strip(), value.strip().strip("\"'")
            if key:
                os.environ.setdefault(key, value)
        return True


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


def _settings():
    required = ("DB_HOST", "DB_PORT", "DB_NAME", "DB_USER")
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        raise RuntimeError(
            "Konfigurasi database belum lengkap di .env: " + ", ".join(missing)
        )
    try:
        port = int(os.getenv("DB_PORT", "3306"))
    except ValueError as exc:
        raise RuntimeError("DB_PORT harus berupa angka.") from exc
    return {
        "host": os.environ["DB_HOST"],
        "port": port,
        "database": os.environ["DB_NAME"],
        "user": os.environ["DB_USER"],
        "password": os.getenv("DB_PASSWORD", ""),
        "connection_timeout": 5,
        "charset": "utf8mb4",
        "use_unicode": True,
    }


def get_connection():
    """Open a new database connection using local .env settings."""
    if mysql is None:
        raise RuntimeError(
            "Driver database belum terpasang. Jalankan: python -m pip install -r requirements.txt"
        )
    return mysql.connector.connect(**_settings())


def test_connection():
    """Check connectivity and read the selected database name; writes nothing."""
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT DATABASE()")
            row = cursor.fetchone()
            return True, f"Terhubung ke database: {row[0] if row else '(tidak diketahui)'}"
        finally:
            cursor.close()
    except Exception as exc:
        return False, f"Koneksi database gagal: {exc}"
    finally:
        close_connection(connection)


def close_connection(connection):
    """Close a connection safely, including when initialization failed."""
    if connection is not None:
        try:
            if connection.is_connected():
                connection.close()
        except (AttributeError, Error):
            try:
                connection.close()
            except (AttributeError, Error):
                pass
