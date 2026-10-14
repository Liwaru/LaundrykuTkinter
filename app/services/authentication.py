"""Database-backed login using PHP-compatible bcrypt hashes."""

import logging
from dataclasses import dataclass

import bcrypt
from mysql.connector import Error

from app.database.connection import close_connection, get_connection

logger = logging.getLogger(__name__)


class InvalidCredentials(Exception):
    """Username/password pair is invalid."""


class InactiveAccount(Exception):
    """Credentials are valid, but the account is disabled."""


class AuthenticationServiceError(Exception):
    """Authentication could not be completed due to a service/database error."""


@dataclass(frozen=True)
class AuthenticatedUser:
    user_id: int
    name: str
    phone: str
    username: str
    level: int


def verify_php_bcrypt(password, password_hash):
    """Verify PHP password_hash(PASSWORD_BCRYPT) values (2y/2a/2b prefixes)."""
    if not isinstance(password, str) or "\x00" in password:
        return False
    if not isinstance(password_hash, str):
        return False
    candidate = password_hash.encode("ascii", errors="ignore")
    if candidate.startswith(b"$2y$"):
        candidate = b"$2b$" + candidate[4:]
    try:
        # PHP bcrypt uses the first 72 input bytes, matching its historical behavior.
        password_bytes = password.encode("utf-8")[:72]
        return bcrypt.checkpw(password_bytes, candidate)
    except (ValueError, TypeError):
        return False


def authenticate(username, password):
    """Validate credentials and active status, then return a minimal session."""
    if not isinstance(username, str) or not isinstance(password, str):
        raise InvalidCredentials
    username = username.strip()
    if not username or not password:
        raise InvalidCredentials

    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT id_user, nama, no_hp, username, password, level, status_akun "
            "FROM users WHERE username = %s LIMIT 1",
            (username,),
        )
        row = cursor.fetchone()
        if not row or not verify_php_bcrypt(password, row.get("password")):
            raise InvalidCredentials
        if str(row.get("status_akun") or "").strip().casefold() != "aktif":
            raise InactiveAccount
        try:
            level = int(row["level"])
            user_id = int(row["id_user"])
        except (KeyError, TypeError, ValueError) as exc:
            logger.error("Akun %s memiliki data role/id yang tidak valid", username)
            raise AuthenticationServiceError("Data akun tidak lengkap. Hubungi administrator.") from exc
        if level not in (1, 2, 3, 4):
            logger.error("Akun %s memiliki level di luar rentang aplikasi", username)
            raise AuthenticationServiceError("Role akun belum didukung aplikasi.")
        return AuthenticatedUser(
            user_id=user_id,
            name=str(row.get("nama") or ""),
            phone=str(row.get("no_hp") or ""),
            username=str(row.get("username") or username),
            level=level,
        )
    except (InvalidCredentials, InactiveAccount, AuthenticationServiceError):
        raise
    except Exception as exc:
        logger.exception("Autentikasi database gagal")
        raise AuthenticationServiceError(
            "Tidak dapat memeriksa akun. Periksa koneksi database dan coba lagi."
        ) from exc
    finally:
        if cursor is not None:
            try:
                cursor.close()
            except Error:
                logger.exception("Gagal menutup cursor autentikasi")
        close_connection(connection)
