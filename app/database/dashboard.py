"""Read-only dashboard queries for the existing LaundryKu schema."""

from datetime import date
import logging

from app.database.connection import close_connection, get_connection
from app.services.authorization import require_role

logger = logging.getLogger(__name__)

PROCESSING_STATUSES = ("dicuci", "dikeringkan", "disetrika", "dipacking")


def get_dashboard_data(user, today=None):
    """Return dashboard counts and recent transactions, without modifying data."""
    require_role(user, (2, 4))
    today = today or date.today()
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT COUNT(*) AS total FROM transaksi WHERE DATE(tanggal_masuk) = %s",
                (today,),
            )
            transactions_today = cursor.fetchone()["total"]

            cursor.execute(
                "SELECT COALESCE(SUM(jumlah), 0) AS total FROM pembayaran "
                "WHERE LOWER(status) = %s AND DATE(tanggal_bayar) = %s",
                ("berhasil", today),
            )
            revenue_today = cursor.fetchone()["total"]

            placeholders = ", ".join("%s" for _ in PROCESSING_STATUSES)
            cursor.execute(
                f"SELECT COUNT(*) AS total FROM transaksi "
                f"WHERE LOWER(status_laundry) IN ({placeholders})",
                PROCESSING_STATUSES,
            )
            processing = cursor.fetchone()["total"]

            cursor.execute(
                "SELECT COUNT(*) AS total FROM transaksi "
                "WHERE LOWER(status_laundry) = %s",
                ("siap_diambil",),
            )
            ready = cursor.fetchone()["total"]

            cursor.execute(
                "SELECT t.kode_transaksi, u.nama AS nama_pelanggan, t.tanggal_masuk, "
                "t.total_harga, t.status_laundry "
                "FROM transaksi AS t "
                "JOIN users AS u ON u.id_user = t.id_pelanggan "
                "ORDER BY t.tanggal_masuk DESC, t.id_transaksi DESC LIMIT %s",
                (10,),
            )
            recent_transactions = cursor.fetchall()
        finally:
            cursor.close()
        return {
            "transactions_today": transactions_today,
            "revenue_today": revenue_today,
            "processing": processing,
            "ready": ready,
            "recent_transactions": recent_transactions,
        }
    except Exception as exc:
        logger.exception("Gagal membaca data dashboard")
        raise RuntimeError(f"Gagal membaca data dashboard: {exc}") from exc
    finally:
        close_connection(connection)
