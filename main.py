"""LaundryKu desktop UI built with Python's standard Tkinter library."""

import tkinter as tk
import logging
from datetime import date
from pathlib import Path
from tkinter import ttk
from app.database.dashboard import get_dashboard_data
from app.database.connection import PROJECT_ROOT
from app.services.authentication import (
    AuthenticationServiceError,
    InactiveAccount,
    InvalidCredentials,
    authenticate,
)
from app.services.authorization import ROLE_NAMES, can_access, menus_for
from app.ui import login_template1, login_template2

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = ImageTk = None

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("laundryku.ui")

# Change to "template1" to restore the approved Blue Wave Premium login.
LOGIN_TEMPLATE = "template2"


class LaundryKuApp:
    BG = "#F4F7FC"
    WHITE = "#FFFFFF"
    NAVY = "#15345B"
    BLUE = "#2563EB"
    MUTED = "#64748B"
    BORDER = "#E3EAF3"
    FONT = "Segoe UI"

    MENUS = ("Transaksi", "Pelanggan", "Layanan", "Pembayaran", "Laporan", "Pengguna")
    STATUS_COLORS = {"sedang diproses": ("#FFF4DB", "#946200"), "siap diambil": ("#EAF1FF", "#2455B7"),
                     "selesai": ("#E8F6EE", "#26734D"), "menunggu": ("#F1ECFF", "#6842A6")}
    def __init__(self, root):
        self.root = root
        self.active_menu = "Dashboard"
        self.nav_buttons = {}
        self.root.title("LaundryKu | Sistem Manajemen Laundry")
        self.root.geometry("1280x800")
        self.root.minsize(980, 650)
        self.root.configure(bg=self.BG)
        self.user_session = None
        self.logo_image = None
        self.setup_style()
        self.build_login()

    def _load_logo(self, size):
        candidates = (
            PROJECT_ROOT / "assets" / "laundryku_logo.png",
            PROJECT_ROOT / "assets" / "laundryku_logo_transparan.png",
        )
        logo_path = next((path for path in candidates if path.is_file()), None)
        if logo_path is None:
            logger.warning("Logo LaundryKu tidak ditemukan. Lokasi yang diperiksa: %s", candidates[0])
            return None
        try:
            if Image is None:
                image = tk.PhotoImage(file=str(logo_path))
                factor = max(1, (max(image.width(), image.height()) + size - 1) // size)
                return image.subsample(factor, factor) if factor > 1 else image
            with Image.open(logo_path) as source:
                source = source.convert("RGBA")
                source.thumbnail((size, size), Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(source.copy())
        except Exception:
            logger.exception("Logo tidak dapat dimuat dari %s", logo_path)
            return None

    def build_login(self):
        """Render configured login design; templates share this app's auth/session."""
        templates = {"template1": login_template1.build_login,
                     "template2": login_template2.build_login}
        selected = str(LOGIN_TEMPLATE).strip().casefold()
        if selected not in templates:
            raise ValueError(f"LOGIN_TEMPLATE tidak dikenal: {LOGIN_TEMPLATE!r}")
        self.login_template = selected
        templates[selected](self)

    @staticmethod
    def draw_input_icon(canvas, kind):
        """Draw matching user and lock outline icons in native Tkinter."""
        color = "#71829A"
        if kind == "user":
            canvas.create_oval(15, 8, 23, 16, outline=color, width=1.6)
            canvas.create_line(10, 33, 10, 30, 12, 25, 16, 22, 22, 22, 26, 25, 28, 30, 28, 33,
                               fill=color, width=1.6, capstyle=tk.ROUND, joinstyle=tk.ROUND)
        else:
            canvas.create_line(14, 20, 14, 15, 16, 11, 19, 9, 23, 11, 25, 15, 25, 20,
                               fill=color, width=1.6, capstyle=tk.ROUND, joinstyle=tk.ROUND)
            canvas.create_rectangle(11, 19, 28, 33, outline=color, width=1.6)
            canvas.create_oval(18, 23, 21, 26, fill=color, outline=color)
            canvas.create_line(19.5, 26, 19.5, 29, fill=color, width=1.5)

    def _draw_eye_icon(self):
        self.eye_canvas.delete("all")
        color = "#71829A"
        self.eye_canvas.create_line(7, 21, 12, 15, 19, 12, 26, 15, 32, 21,
                                    26, 27, 19, 30, 12, 27, 7, 21,
                                    fill=color, width=1.7, smooth=True, capstyle=tk.ROUND)
        self.eye_canvas.create_oval(16, 18, 22, 24, outline=color, width=1.6)
        self.eye_canvas.create_oval(18, 20, 20, 22, fill=color, outline=color)
        if self.password_visible:
            self.eye_canvas.create_line(9, 31, 30, 10, fill=color, width=1.7, capstyle=tk.ROUND)

    def toggle_password(self):
        """Toggle visibility without clearing the entry or losing its caret/focus."""
        focused = self.password_entry.focus_get() == self.password_entry
        caret = self.password_entry.index("insert")
        self.password_visible = not self.password_visible
        self.password_entry.configure(show="" if self.password_visible else "*")
        self._draw_eye_icon()
        if focused:
            self.password_entry.focus_set()
            self.password_entry.icursor(caret)

    def _draw_brand_accents(self, event):
        """Compatibility hook for the preserved Template 1 canvas renderer."""
        login_template1.draw_brand_accents(self, event)

    def _set_login_button_color(self, color):
        if self.login_button.winfo_exists() and str(self.login_button.cget("state")) != "disabled":
            self.login_button.configure(bg=color, activebackground=color)

    def submit_login(self):
        self.login_button.configure(state="disabled", text="Memeriksa...")
        self.login_message.configure(text="", fg="#C24141")
        self.root.update_idletasks()
        try:
            self.user_session = authenticate(self.username_entry.get(), self.password_entry.get())
        except InvalidCredentials:
            self.login_message.configure(text="Username atau password salah.")
        except InactiveAccount:
            self.login_message.configure(text="Akun Anda tidak aktif. Hubungi administrator.")
        except AuthenticationServiceError as exc:
            self.login_message.configure(text=str(exc))
        else:
            self.build_layout()
            self.show_page("Dashboard")
            return
        self.login_button.configure(state="normal", text="Masuk ke LaundryKu", bg=self.BLUE, activebackground="#1D4ED8")

    def logout(self):
        self.user_session = None
        self.nav_buttons.clear()
        self.build_login()

    @staticmethod
    def draw_menu_icon(canvas, menu, color):
        """Draw matching 18 px outline icons using Tkinter Canvas primitives."""
        canvas.delete("all")
        line = {"fill": color, "width": 1.7, "capstyle": tk.ROUND, "joinstyle": tk.ROUND}
        if menu == "Transaksi":  # receipt / clipboard list
            canvas.create_rectangle(4, 2, 16, 18, outline=color, width=1.7)
            for y in (7, 11, 15):
                canvas.create_line(7, y, 13, y, **line)
        elif menu == "Pelanggan":  # clearly recognizable person
            canvas.create_oval(7, 2, 13, 8, outline=color, width=1.7)
            canvas.create_line(3, 18, 3, 16, 5, 12, 8, 10, 12, 10, 15, 12, 17, 16, 17, 18, **line)
        elif menu == "Layanan":  # washing machine
            canvas.create_rectangle(2, 2, 18, 18, outline=color, width=1.7)
            canvas.create_line(3, 6, 17, 6, **line)
            canvas.create_oval(6, 8, 15, 17, outline=color, width=1.7)
            canvas.create_oval(5, 3, 6.5, 4.5, fill=color, outline=color)
            canvas.create_oval(8, 3, 9.5, 4.5, fill=color, outline=color)
        elif menu == "Pembayaran":  # payment card / wallet
            canvas.create_rectangle(2, 4, 18, 16, outline=color, width=1.7)
            canvas.create_line(3, 8, 17, 8, **line)
            canvas.create_line(5, 13, 9, 13, **line)
        elif menu == "Laporan":  # chart
            canvas.create_line(3, 2, 3, 18, 18, 18, **line)
            canvas.create_rectangle(6, 11, 9, 16, outline=color, width=1.5)
            canvas.create_rectangle(11, 7, 14, 16, outline=color, width=1.5)
            canvas.create_rectangle(16, 4, 18, 16, outline=color, width=1.5)
        elif menu == "Pengguna":  # user with settings cue
            canvas.create_oval(4, 2, 10, 8, outline=color, width=1.7)
            canvas.create_line(1, 18, 1, 16, 3, 12, 6, 10, 10, 10, 12, 12, **line)
            canvas.create_oval(13, 12, 18, 17, outline=color, width=1.5)
            canvas.create_line(15.5, 10, 15.5, 12, 15.5, 17, 15.5, 19, **line)
            canvas.create_line(11, 14.5, 13, 14.5, 18, 14.5, 20, 14.5, **line)

    def _on_table_mousewheel(self, event):
        """Scroll transaction rows while the pointer is over the table, without a bar."""
        body = getattr(self, "transaction_body", None)
        canvas = getattr(self, "transaction_canvas", None)
        if body is None or canvas is None or not body.winfo_exists():
            return
        x0, y0 = body.winfo_rootx(), body.winfo_rooty()
        if not (x0 <= event.x_root < x0 + body.winfo_width()
                and y0 <= event.y_root < y0 + body.winfo_height()):
            return
        if getattr(event, "num", None) == 4:
            units = -1
        elif getattr(event, "num", None) == 5:
            units = 1
        else:
            delta = getattr(event, "delta", 0)
            units = int(-delta / 120) if abs(delta) >= 120 else (-1 if delta > 0 else 1)
        canvas.yview_scroll(units, "units")
        return "break"

    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        available = set(self.root.tk.call("font", "families"))
        self.font_family = next((name for name in ("Segoe UI", "Arial", "TkDefaultFont") if name in available), "TkDefaultFont")
        style.configure("Laundry.Treeview", background=self.WHITE, fieldbackground=self.WHITE,
                        foreground=self.NAVY, rowheight=48, font=(self.font_family, 10), borderwidth=0)
        style.configure("Laundry.Treeview.Heading", background="#F8FAFD", foreground=self.MUTED,
                        font=(self.font_family, 9, "bold"), relief="flat", padding=(12, 12))
        style.map("Laundry.Treeview", background=[("selected", "#EAF1FF")], foreground=[("selected", self.NAVY)])

    def build_layout(self):
        for child in self.root.winfo_children():
            child.destroy()
        self.root.title("LaundryKu | Sistem Manajemen Laundry")
        self.root.geometry("1280x800")
        self.root.minsize(980, 650)
        self.nav_buttons.clear()
        self.sidebar = tk.Frame(self.root, bg=self.NAVY, width=238)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        brand = tk.Frame(self.sidebar, bg=self.NAVY)
        brand.pack(fill="x", padx=18, pady=(27, 34))
        self.logo_image = self._load_logo(44)
        logo_label = None
        if self.logo_image is not None:
            logo_label = tk.Label(brand, image=self.logo_image, bg=self.NAVY, bd=0)
            logo_label.pack(side="left", padx=(0, 9))
        brand_text = tk.Frame(brand, bg=self.NAVY)
        brand_text.pack(side="left", anchor="center")
        tk.Label(brand_text, text="LaundryKu", bg=self.NAVY, fg=self.WHITE,
                 font=(self.font_family, 20, "bold")).pack(anchor="w")
        tk.Label(brand_text, text="MANAJEMEN LAUNDRY", bg=self.NAVY, fg="#AFC8EE",
                 font=(self.font_family, 8, "bold")).pack(anchor="w", pady=(1, 0))
        clickable_brand = (brand, brand_text, *brand_text.winfo_children())
        if logo_label is not None:
            clickable_brand += (logo_label,)
        for widget in clickable_brand:
            widget.configure(cursor="hand2")
            widget.bind("<Button-1>", lambda _event: self.show_page("Dashboard"))

        for menu in menus_for(self.user_session):
            item = tk.Frame(self.sidebar, bg=self.NAVY)
            item.pack(fill="x", padx=12, pady=2)
            icon = tk.Canvas(item, width=20, height=20, bg=self.NAVY, highlightthickness=0, bd=0,
                             cursor="hand2")
            icon.pack(side="left", padx=(10, 9), pady=10)
            self.draw_menu_icon(icon, menu, "#B9CBE3")
            button = tk.Button(item, text=menu, anchor="w", command=lambda name=menu: self.show_page(name),
                               relief="flat", bd=0, cursor="hand2", font=(self.font_family, 10),
                               padx=0, pady=10, bg=self.NAVY, fg="#D9E5F5",
                               activebackground="#254974", activeforeground=self.WHITE)
            button.pack(side="left", fill="x", expand=True)
            item.bind("<Button-1>", lambda event, name=menu: self.show_page(name))
            icon.bind("<Button-1>", lambda event, name=menu: self.show_page(name))
            self.nav_buttons[menu] = (item, icon, button)

        tk.Frame(self.sidebar, bg="#345273", height=1).pack(fill="x", padx=20, pady=(20, 14))
        account = tk.Frame(self.sidebar, bg=self.NAVY)
        account.pack(side="bottom", fill="x", padx=20, pady=18)
        tk.Label(account, text=self.user_session.name or self.user_session.username,
                 bg=self.NAVY, fg=self.WHITE, font=(self.font_family, 9, "bold"),
                 anchor="w").pack(fill="x")
        tk.Label(account, text=ROLE_NAMES.get(self.user_session.level, "Akun"),
                 bg=self.NAVY, fg="#AFC8EE", font=(self.font_family, 8),
                 anchor="w").pack(fill="x", pady=(2, 8))
        tk.Button(account, text="Keluar", command=self.logout, bg="#214875", fg=self.WHITE,
                  activebackground="#2B5686", activeforeground=self.WHITE, relief="flat", bd=0,
                  cursor="hand2", font=(self.font_family, 9), padx=10, pady=7,
                  anchor="w").pack(fill="x")

        self.main = tk.Frame(self.root, bg=self.BG)
        self.main.pack(side="left", fill="both", expand=True)
        self.header = tk.Frame(self.main, bg=self.WHITE, height=68,
                               highlightbackground=self.BORDER, highlightthickness=1)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)
        self.header_title = tk.Label(self.header, text="", bg=self.WHITE, fg=self.NAVY,
                                     font=(self.font_family, 11, "bold"))
        self.header_title.pack(side="left", padx=28)
        self.header_connection_dot = tk.Canvas(self.header, width=12, height=12, bg=self.WHITE,
                                               highlightthickness=0, bd=0)
        self._db_dot = self.header_connection_dot.create_oval(3, 3, 9, 9, fill="#94A3B8", outline="")
        self.header_connection_dot.pack(side="right", padx=28)
        self.page = tk.Frame(self.main, bg=self.BG)
        self.page.pack(fill="both", expand=True, padx=28, pady=25)

    def show_page(self, name):
        if self.user_session is None:
            return
        if not can_access(self.user_session, name):
            logger.warning("Akses menu %s ditolak untuk role %s", name, self.user_session.level)
            self.show_page("Dashboard")
            return
        self.active_menu = name
        self.header_title.configure(text=f"LaundryKu   /   {name}")
        for menu, widgets in self.nav_buttons.items():
            active = menu == name
            item, icon, button = widgets
            background = "#214875" if active else self.NAVY
            item.configure(bg=background)
            icon.configure(bg=background)
            self.draw_menu_icon(icon, menu, self.WHITE if active else "#B9CBE3")
            button.configure(bg=background, fg=self.WHITE if active else "#D9E5F5",
                             font=(self.font_family, 10, "bold" if active else "normal"))
        for widget in self.page.winfo_children():
            widget.destroy()
        if name == "Dashboard":
            self.build_dashboard()
        else:
            self.build_placeholder(name)

    def build_role_dashboard(self):
        role_name = ROLE_NAMES.get(self.user_session.level, "Pengguna")
        heading = "Ruang kerja pelanggan" if self.user_session.level == 1 else "Antrean operasional"
        detail = ("Akun pelanggan hanya dapat membuka fitur dan data miliknya sendiri."
                  if self.user_session.level == 1 else
                  "Ringkasan antrean laundry akan tersedia pada tahap fitur operasional.")
        tk.Label(self.page, text=heading, bg=self.BG, fg=self.NAVY,
                 font=(self.font_family, 26, "bold")).pack(anchor="w")
        tk.Label(self.page, text=f"Selamat datang, {self.user_session.name or role_name}.",
                 bg=self.BG, fg=self.MUTED, font=(self.font_family, 10)).pack(anchor="w", pady=(5, 20))
        panel = tk.Frame(self.page, bg=self.WHITE, highlightbackground=self.BORDER, highlightthickness=1)
        panel.pack(fill="both", expand=True)
        tk.Label(panel, text=detail, bg=self.WHITE, fg=self.MUTED,
                 font=(self.font_family, 11), wraplength=600).place(relx=0.5, rely=0.5, anchor="center")

    def set_database_indicator(self, color):
        if hasattr(self, "_db_dot"):
            self.header_connection_dot.itemconfigure(self._db_dot, fill=color)

    def build_dashboard(self):
        if self.user_session.level not in (2, 4):
            self.build_role_dashboard()
            return
        try:
            data = get_dashboard_data(self.user_session)
            self.dashboard_error = None
        except RuntimeError as exc:
            data = None
            self.dashboard_error = str(exc)
            logger.error("Dashboard tidak dapat dimuat: %s", exc)
            self.set_database_indicator("#DC4C4C")
        else:
            self.set_database_indicator("#22A06B")
        heading = tk.Frame(self.page, bg=self.BG)
        heading.pack(fill="x", pady=(0, 20))
        left = tk.Frame(heading, bg=self.BG)
        left.pack(side="left", anchor="w")
        tk.Label(left, text="Ringkasan hari ini", bg=self.BG, fg=self.NAVY,
                 font=(self.font_family, 26, "bold")).pack(anchor="w")
        tk.Label(left, text="Pantau aktivitas operasional laundry Anda.", bg=self.BG, fg=self.MUTED,
                 font=(self.font_family, 10)).pack(anchor="w", pady=(4, 0))
        tk.Label(heading, text=date.today().strftime("%d %b %Y"), bg=self.BG, fg=self.MUTED,
                 font=(self.font_family, 9)).pack(side="right", anchor="s", pady=(0, 4))

        cards = tk.Frame(self.page, bg=self.BG)
        cards.pack(fill="x", pady=(0, 20))
        stats = (("Transaksi Hari Ini", f"{data['transactions_today']:,}".replace(",", ".") if data else "—", "Dari database", self.BLUE, "▣"),
                 ("Pendapatan Hari Ini", self.format_currency(data["revenue_today"]) if data else "—", "Pembayaran berhasil", "#16A36A", "↗"),
                 ("Sedang Diproses", f"{data['processing']:02d}" if data else "—", "Pesanan aktif", "#D99013", "◷"),
                 ("Siap Diambil", f"{data['ready']:02d}" if data else "—", "Menunggu pelanggan", "#7C3AED", "✓"))
        for column in range(4):
            cards.grid_columnconfigure(column, weight=1, uniform="stat")
        for index, (title, value, note, accent, icon) in enumerate(stats):
            card = tk.Frame(cards, bg=self.WHITE, highlightbackground=self.BORDER, highlightthickness=1)
            card.grid(row=0, column=index, sticky="nsew", padx=(0 if index == 0 else 7, 0 if index == 3 else 7))
            top = tk.Frame(card, bg=self.WHITE)
            top.pack(fill="x", padx=15, pady=(15, 9))
            tk.Label(top, text=title, bg=self.WHITE, fg=self.MUTED,
                     font=(self.font_family, 10)).pack(side="left", anchor="w")
            tk.Label(top, text=icon, bg="#EEF4FF", fg=accent, width=3, height=1,
                     font=(self.font_family, 11, "bold")).pack(side="right")
            tk.Label(card, text=value, bg=self.WHITE, fg=self.NAVY,
                     font=(self.font_family, 25, "bold")).pack(anchor="w", padx=15)
            tk.Label(card, text=note, bg=self.WHITE, fg=accent if index < 2 else self.MUTED,
                     font=(self.font_family, 8)).pack(anchor="w", padx=15, pady=(5, 15))

        panel = tk.Frame(self.page, bg=self.WHITE, highlightbackground=self.BORDER, highlightthickness=1)
        panel.pack(fill="both", expand=True)
        panel_head = tk.Frame(panel, bg=self.WHITE)
        panel_head.pack(fill="x", padx=18, pady=(15, 13))
        title_block = tk.Frame(panel_head, bg=self.WHITE)
        title_block.pack(side="left")
        tk.Label(title_block, text="Transaksi terbaru", bg=self.WHITE, fg=self.NAVY,
                 font=(self.font_family, 13, "bold")).pack(anchor="w")
        tk.Label(title_block, text="Data transaksi dari database LaundryKu", bg=self.WHITE,
                 fg=self.MUTED, font=(self.font_family, 8)).pack(anchor="w", pady=(3, 0))
        actions = tk.Frame(panel_head, bg=self.WHITE)
        actions.pack(side="right")
        self.make_button(actions, "↻  Muat Ulang", "#EEF4FF", self.BLUE,
                         lambda: self.show_page("Dashboard")).pack(side="left", padx=(0, 8))
        self.make_button(actions, "+  Transaksi", self.BLUE, self.WHITE,
                         lambda: self.show_page("Transaksi")).pack(side="left", padx=(0, 8))
        self.make_button(actions, "+  Pelanggan", "#EEF4FF", self.BLUE,
                         lambda: self.show_page("Pelanggan")).pack(side="left")

        table_wrap = tk.Frame(panel, bg=self.WHITE)
        table_wrap.pack(fill="both", expand=True, padx=16, pady=(0, 14))
        columns = (("NOMOR TRANSAKSI", 2.0), ("PELANGGAN", 1.55), ("TANGGAL", 1.0),
                   ("TOTAL HARGA", 1.25), ("STATUS", 1.35))
        header_row = tk.Frame(table_wrap, bg="#F8FAFD")
        header_row.pack(fill="x")
        for index, (label, weight) in enumerate(columns):
            header_row.grid_columnconfigure(index, weight=int(weight * 100), uniform="transaction_columns")
            tk.Label(header_row, text=label, anchor="w", bg="#F8FAFD", fg=self.MUTED,
                     font=(self.font_family, 9, "bold"), padx=12, pady=12).grid(
                         row=0, column=index, sticky="ew")

        body = tk.Frame(table_wrap, bg=self.WHITE)
        body.pack(fill="both", expand=True)
        canvas = tk.Canvas(body, bg=self.WHITE, highlightthickness=0, bd=0)
        canvas.pack(fill="both", expand=True)
        self.transaction_canvas = canvas
        self.transaction_body = body
        if not getattr(self, "_mousewheel_bound", False):
            self.root.bind_all("<MouseWheel>", self._on_table_mousewheel)
            self.root.bind_all("<Button-4>", self._on_table_mousewheel)
            self.root.bind_all("<Button-5>", self._on_table_mousewheel)
            self._mousewheel_bound = True
        rows_frame = tk.Frame(canvas, bg=self.WHITE)
        window_id = canvas.create_window((0, 0), window=rows_frame, anchor="nw")
        rows_frame.bind("<Configure>", lambda _event: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda event: canvas.itemconfigure(window_id, width=event.width))
        for index, (_label, weight) in enumerate(columns):
            rows_frame.grid_columnconfigure(index, weight=int(weight * 100), uniform="transaction_columns")

        if data is None:
            self.add_table_message(rows_frame, "Database tidak tersedia. Lihat detail error di terminal.")
        elif not data["recent_transactions"]:
            self.add_table_message(rows_frame, "Belum ada transaksi.")
        else:
            for row_index, row in enumerate(data["recent_transactions"]):
                background = self.WHITE if row_index % 2 == 0 else "#FBFCFE"
                entered = row["tanggal_masuk"]
                entered = entered.strftime("%d %b %Y") if hasattr(entered, "strftime") else str(entered)
                raw_status = str(row["status_laundry"] or "-")
                status = raw_status.replace("_", " ").title()
                status_bg, status_fg = self.STATUS_COLORS.get(status.casefold(), ("#F1F5F9", self.MUTED))
                values = (row["kode_transaksi"], row["nama_pelanggan"], entered,
                          self.format_currency(row["total_harga"]), None)
                table_row = tk.Frame(rows_frame, bg=background,
                                     highlightbackground=self.BORDER, highlightthickness=1)
                table_row.grid(row=row_index, column=0, columnspan=5, sticky="ew")
                for column_index, (_label, weight) in enumerate(columns):
                    table_row.grid_columnconfigure(column_index, weight=int(weight * 100), uniform="transaction_columns")
                    if column_index < 4:
                        tk.Label(table_row, text=values[column_index], anchor="w", bg=background,
                                 fg=self.NAVY, font=(self.font_family, 10), padx=12, pady=14).grid(
                                     row=0, column=column_index, sticky="ew")
                    else:
                        badge = tk.Label(table_row, text=status, bg=status_bg, fg=status_fg,
                                         font=(self.font_family, 9, "bold"), padx=10, pady=5)
                        badge.grid(row=0, column=column_index, sticky="w", padx=12, pady=8)

    def add_table_message(self, parent, message):
        tk.Label(parent, text=message, bg=self.WHITE, fg=self.MUTED,
                 font=(self.font_family, 10), anchor="center", pady=28).grid(
                     row=0, column=0, columnspan=5, sticky="ew")

    def make_button(self, parent, text, background, foreground, command):
        return tk.Button(parent, text=text, command=command, bg=background, fg=foreground,
                         activebackground=background, activeforeground=foreground, relief="flat", bd=0,
                         cursor="hand2", font=(self.font_family, 9, "bold"), padx=12, pady=8)

    @staticmethod
    def format_currency(amount):
        try:
            return "Rp " + f"{int(amount or 0):,}".replace(",", ".")
        except (TypeError, ValueError):
            return "Rp 0"

    def build_placeholder(self, name):
        tk.Label(self.page, text=name, bg=self.BG, fg=self.NAVY,
                 font=(self.font_family, 26, "bold")).pack(anchor="w")
        tk.Label(self.page, text="Kelola aktivitas operasional LaundryKu.", bg=self.BG,
                 fg=self.MUTED, font=(self.font_family, 10)).pack(anchor="w", pady=(4, 20))
        panel = tk.Frame(self.page, bg=self.WHITE, highlightbackground=self.BORDER, highlightthickness=1)
        panel.pack(fill="both", expand=True)
        inner = tk.Frame(panel, bg=self.WHITE)
        inner.place(relx=0.5, rely=0.46, anchor="center")
        page_icon = tk.Canvas(inner, width=24, height=24, bg=self.WHITE, highlightthickness=0)
        page_icon.pack(pady=(0, 15))
        self.draw_menu_icon(page_icon, name, self.BLUE)
        tk.Label(inner, text=f"Halaman {name}", bg=self.WHITE, fg=self.NAVY,
                 font=(self.font_family, 17, "bold")).pack()
        tk.Label(inner, text="Kerangka halaman siap dikembangkan. Belum terhubung ke database.",
                 bg=self.WHITE, fg=self.MUTED, font=(self.font_family, 10)).pack(pady=(7, 0))


if __name__ == "__main__":
    root = tk.Tk()
    LaundryKuApp(root)
    root.mainloop()
