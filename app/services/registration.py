"""Public customer registration for the existing LaundryKu users table."""

import logging
import re

import bcrypt

from app.database.connection import close_connection, get_connection

logger = logging.getLogger(__name__)

CUSTOMER_LEVEL = 1
MAX_NAME_LENGTH = 9
MAX_PHONE_LENGTH = 12
MAX_USERNAME_LENGTH = 12
MIN_PASSWORD_LENGTH = 8
MAX_BCRYPT_BYTES = 72


class RegistrationValidationError(ValueError):
    """Submitted registration data is invalid."""


class AccountAlreadyExists(RegistrationValidationError):
    """Username or phone number is already in use."""


class RegistrationServiceError(RuntimeError):
    """Database registration failed."""


def validate_registration(name, phone, username, password, confirmation):
    """Validate and normalize fields against the live users table limits."""
    if not all(isinstance(value, str) for value in
               (name, phone, username, password, confirmation)):
        raise RegistrationValidationError("Semua field wajib diisi dengan teks yang valid.")
    name = name.strip() if isinstance(name, str) else ""
    raw_phone = phone.strip() if isinstance(phone, str) else ""
    username = username.strip() if isinstance(username, str) else ""

    if not all((name, raw_phone, username, password, confirmation)):
        raise RegistrationValidationError("Semua field wajib diisi.")
    if len(name) > MAX_NAME_LENGTH:
        raise RegistrationValidationError(
            f"Nama maksimal {MAX_NAME_LENGTH} karakter sesuai batas database."
        )
    if not re.fullmatch(r"\+?[0-9][0-9()\-\s]*", raw_phone):
        raise RegistrationValidationError("Nomor HP hanya boleh berisi angka dan pemisah nomor.")
    normalized_phone = re.sub(r"\D", "", raw_phone)
    if not 8 <= len(normalized_phone) <= MAX_PHONE_LENGTH:
        raise RegistrationValidationError(
            f"Nomor HP harus terdiri dari 8–{MAX_PHONE_LENGTH} digit."
        )
    if len(username) > MAX_USERNAME_LENGTH or not re.fullmatch(r"[A-Za-z0-9_.-]{3,12}", username):
        raise RegistrationValidationError(
            f"Username harus 3–{MAX_USERNAME_LENGTH} karakter: huruf, angka, titik, garis bawah, atau tanda hubung."
        )
    if "\x00" in password:
        raise RegistrationValidationError("Password mengandung karakter yang tidak didukung.")
    if len(password) < MIN_PASSWORD_LENGTH:
        raise RegistrationValidationError(
            f"Password minimal {MIN_PASSWORD_LENGTH} karakter."
        )
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > MAX_BCRYPT_BYTES:
        raise RegistrationValidationError(
            "Password terlalu panjang; batas kompatibel bcrypt adalah 72 byte."
        )
    if password != confirmation:
        raise RegistrationValidationError("Konfirmasi password tidak sama.")

    return name, normalized_phone, username, password_bytes


def register_customer(name, phone, username, password, confirmation):
    """Create one active customer; the public caller cannot supply a role."""
    name, phone, username, password_bytes = validate_registration(
        name, phone, username, password, confirmation
    )
    password_hash = bcrypt.hashpw(password_bytes, bcrypt.gensalt(rounds=12)).decode("ascii")

    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id_user FROM users WHERE username = %s LIMIT 1", (username,))
        if cursor.fetchone():
            raise AccountAlreadyExists("Username sudah digunakan.")
        cursor.execute("SELECT id_user FROM users WHERE no_hp = %s LIMIT 1", (phone,))
        if cursor.fetchone():
            raise AccountAlreadyExists("Nomor HP sudah digunakan.")

        cursor.execute(
            "INSERT INTO users (nama, no_hp, username, password, level, status_akun) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (name, phone, username, password_hash, CUSTOMER_LEVEL, "aktif"),
        )
        connection.commit()
        return int(cursor.lastrowid)
    except RegistrationValidationError:
        if connection is not None:
            try:
                connection.rollback()
            except Exception:
                logger.exception("Gagal membatalkan transaksi registrasi")
        raise
    except Exception as exc:
        if connection is not None:
            try:
                connection.rollback()
            except Exception:
                logger.exception("Gagal membatalkan transaksi registrasi")
        error_code = getattr(exc, "errno", None)
        error_message = str(exc).casefold()
        if error_code == 1062:
            if "no_hp" in error_message:
                raise AccountAlreadyExists("Nomor HP sudah digunakan.") from exc
            if "username" in error_message:
                raise AccountAlreadyExists("Username sudah digunakan.") from exc
            raise AccountAlreadyExists("Username atau nomor HP sudah digunakan.") from exc
        logger.exception("Pendaftaran pelanggan gagal")
        raise RegistrationServiceError(
            "Registrasi gagal karena masalah database. Periksa koneksi lalu coba lagi."
        ) from exc
    finally:
        if cursor is not None:
            try:
                cursor.close()
            except Exception:
                logger.exception("Gagal menutup cursor registrasi")
        close_connection(connection)
