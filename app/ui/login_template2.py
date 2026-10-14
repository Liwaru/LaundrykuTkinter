"""Template 2: Fluid Blue login UI for LaundryKu Desktop."""

import tkinter as tk
from tkinter import font as tkfont
import logging

from PIL import Image, ImageTk

from app.database.connection import PROJECT_ROOT
from app.services.registration import (
    AccountAlreadyExists,
    RegistrationServiceError,
    RegistrationValidationError,
    register_customer,
)

COMPACT_BREAKPOINT_WIDTH = 480
COMPACT_BREAKPOINT_HEIGHT = 600
logger = logging.getLogger("laundryku.ui.login")
FLUID_BACKGROUND_PATH = PROJECT_ROOT / "assets" / "login_fluid_background.png"


class PlaceholderEntry(tk.Entry):
    """Entry with a visual hint that is never returned as a credential."""

    def __init__(self, master, placeholder, *, password=False, **kwargs):
        self.placeholder = placeholder
        self.password_field = password
        self.placeholder_active = False
        super().__init__(master, **kwargs)
        self.bind("<FocusIn>", self._clear_placeholder, add="+")
        self.bind("<FocusOut>", self._restore_placeholder, add="+")
        self._show_placeholder()

    def get(self):
        if self.placeholder_active:
            return ""
        return super().get()

    def _show_placeholder(self):
        if super().get():
            return
        self.placeholder_active = True
        if self.password_field:
            self.configure(show="")
            self.password_visible = False
        self.configure(fg="#94A3B8")
        self.insert(0, self.placeholder)

    def _clear_placeholder(self, _event=None):
        if not self.placeholder_active:
            return
        self.delete(0, "end")
        self.placeholder_active = False
        self.configure(fg="#15345B")
        if self.password_field:
            self.configure(show="*")

    def _restore_placeholder(self, _event=None):
        if not super().get():
            self._show_placeholder()


def build_login(app):
    """Render login, sharing the same visual shell used by registration."""
    if _activate_cached_auth_page(app, "login"):
        return
    _begin_auth_page_build(app, "login")
    form = _build_auth_shell(app, "LaundryKu | Masuk")
    app.login_template2_mode = "login"
    card, content = _create_auth_card(app, form)

    heading = tk.Label(content, text="Masuk ke LaundryKu", bg=app.WHITE, fg=app.NAVY,
                       font=(app.font_family, 25, "bold"), bd=0, anchor="center")
    description = tk.Label(content, text="Masuk untuk melanjutkan aktivitasmu.", bg=app.WHITE,
                           fg="#64748B", font=(app.font_family, 10), wraplength=400,
                           bd=0, anchor="center", justify="center")
    username_label, username_row, app.username_entry, _ = _create_auth_field(
        app, content, "Username", "Masukkan username", "user"
    )
    password_label, password_row, app.password_entry, app.eye_canvas = _create_auth_field(
        app, content, "Password", "Masukkan password", "lock", password=True,
        visibility_callback=lambda: _toggle_password(app),
    )
    app.password_visible = False
    app.username_entry.bind("<Return>", lambda _event: app.password_entry.focus_set())
    app.password_entry.bind("<Return>", lambda _event: app.submit_login())

    app.login_message = tk.Label(content, text="", bg=app.WHITE, fg="#C24141",
                                 font=(app.font_family, 9), anchor="w", wraplength=420, bd=0)
    app.login_button = tk.Button(content, text="Masuk ke LaundryKu", command=app.submit_login,
                                 bg=app.BLUE, fg=app.WHITE, activebackground="#1D4ED8",
                                 activeforeground=app.WHITE, relief="flat", bd=0,
                                 cursor="hand2", font=(app.font_family, 10, "bold"), pady=13)
    _bind_primary_button(app, app.login_button)
    prompt, app.register_link = _create_link_prompt(
        app, content, "Belum punya akun? ", "Daftar sekarang", lambda: build_register(app)
    )
    flow = [
        (heading, 0, 8), (description, 0, 24),
        (username_label, 0, 8), (username_row, 0, 16),
        (password_label, 0, 8), (password_row, 0, 4),
        (app.login_message, 0, 6), (app.login_button, 0, 0),
    ]
    _finish_auth_form(app, form, card, content, flow, (description, app.login_message),
                      footer=prompt, footer_padding=(16, 0))
    app.username_entry.focus_set()
    _cache_auth_page(app, "login")


def build_register(app):
    """Show customer registration without opening a second application window."""
    if _activate_cached_auth_page(app, "register"):
        return
    _begin_auth_page_build(app, "register")
    form = _build_auth_shell(app, "LaundryKu | Daftar")
    app.login_template2_mode = "register"
    card, content = _create_auth_card(app, form)

    heading = tk.Label(content, text="Buat akun LaundryKu", bg=app.WHITE, fg=app.NAVY,
                       font=(app.font_family, 22, "bold"), bd=0, anchor="center")
    description = tk.Label(
        content, text="Daftar untuk mulai menggunakan LaundryKu.", bg=app.WHITE,
        fg="#64748B", font=(app.font_family, 10), wraplength=400,
        bd=0, anchor="center", justify="center",
    )
    app.login_template2_register_description = description
    fields = (
        ("Nama Lengkap", "Masukkan nama lengkap", "user", False),
        ("Nomor HP", "Contoh: 081234567890", "phone", False),
        ("Username", "Buat username", "user", False),
        ("Password", "Buat password", "lock", True),
        ("Konfirmasi Password", "Ulangi password", "lock", True),
    )
    app.register_entries = {}
    app.login_template2_input_rows = []
    field_widgets = []
    for label_text, placeholder, icon_kind, is_password in fields:
        label, row, entry, _eye = _create_auth_field(
            app, content, label_text, placeholder, icon_kind, password=is_password
        )
        app.register_entries[label_text] = entry
        app.login_template2_input_rows.append(row)
        field_widgets.extend((label, row))
    for index, entry in enumerate(tuple(app.register_entries.values())):
        if index < len(app.register_entries) - 1:
            entry.bind("<Return>", lambda _event, field=entry: _focus_next_register_field(app, field))
        else:
            entry.bind("<Return>", lambda _event: _submit_register(app))

    app.register_message = tk.Label(content, text="", bg=app.WHITE, fg="#C24141",
                                    font=(app.font_family, 9), anchor="w", wraplength=420, bd=0)
    app.register_button = tk.Button(
        content, text="Daftar ke LaundryKu", command=lambda: _submit_register(app),
        bg=app.BLUE, fg=app.WHITE, activebackground="#1D4ED8",
        activeforeground=app.WHITE, relief="flat", bd=0, cursor="hand2",
        font=(app.font_family, 10, "bold"), pady=11,
    )
    _bind_primary_button(app, app.register_button)
    prompt, app.register_back_link = _create_link_prompt(
        app, content, "Sudah punya akun? ", "Masuk", lambda: build_login(app)
    )

    regular_flow = [(heading, 0, 5), (description, 0, 10)]
    compact_flow = [(heading, 0, 1), (description, 0, 1)]
    for index in range(0, len(field_widgets), 2):
        label, row = field_widgets[index:index + 2]
        regular_flow.extend(((label, 0, 3), (row, 0, 8)))
        compact_flow.extend(((label, 3, 1), (row, 0, 4)))
    regular_flow.extend(((app.register_message, 0, 3), (app.register_button, 0, 0)))
    compact_flow.extend(((app.register_message, 0, 0), (app.register_button, 0, 0)))
    _finish_auth_form(
        app, form, card, content, regular_flow,
        (description, app.register_message), compact_flow=compact_flow,
        footer=prompt, footer_padding=(14, 0),
    )
    # An empty feedback label should not reserve vertical space on compact windows.
    app.register_message.pack_forget()
    app.register_entries["Nama Lengkap"].focus_set()
    _cache_auth_page(app, "register")


_AUTH_STATE_EXACT_KEYS = {
    "username_entry", "password_entry", "eye_canvas", "password_visible",
    "login_message", "login_button", "register_link", "login_logo_image",
    "brand_canvas", "login_compact",
}
_AUTH_INTERNAL_KEYS = {
    "_login_template2_pages", "_login_template2_active_page",
    "_login_template2_building_page", "_login_template2_build_page",
    "_login_template2_geometry_initialized",
}


def _auth_state(app):
    return {
        key: value for key, value in app.__dict__.items()
        if (key.startswith("register_")
            or (key not in _AUTH_INTERNAL_KEYS
                and (key in _AUTH_STATE_EXACT_KEYS
                     or key.startswith("login_template2_"))))
    }


def _begin_auth_page_build(app, page_name):
    """Hide the active page while constructing the other page in the same root."""
    pages = getattr(app, "_login_template2_pages", None)
    if pages is None:
        app._login_template2_pages = {}
        app._login_template2_active_page = None
        app._login_template2_geometry_initialized = False
    active = app._login_template2_active_page
    if active and active in app._login_template2_pages:
        try:
            app._login_template2_pages[active]["focus"] = app.root.focus_get()
        except tk.TclError:
            app._login_template2_pages[active]["focus"] = None
        app._login_template2_pages[active]["state"] = _auth_state(app)
        app._login_template2_pages[active]["frame"].pack_forget()
    app._login_template2_building_page = page_name


def _cache_auth_page(app, page_name):
    app._login_template2_pages[page_name] = {
        "frame": app._login_template2_build_page,
        "state": _auth_state(app),
        "title": app.root.title(),
        "focus": app.root.focus_get(),
    }
    app._login_template2_active_page = page_name
    del app._login_template2_build_page
    del app._login_template2_building_page


def _activate_cached_auth_page(app, page_name):
    pages = getattr(app, "_login_template2_pages", {})
    if page_name not in pages:
        return False
    active = getattr(app, "_login_template2_active_page", None)
    if active and active != page_name and active in pages:
        try:
            pages[active]["focus"] = app.root.focus_get()
        except tk.TclError:
            pages[active]["focus"] = None
        pages[active]["state"] = _auth_state(app)
        pages[active]["frame"].pack_forget()
    page = pages[page_name]
    app.__dict__.update(page["state"])
    page["frame"].pack(fill="both", expand=True)
    app.root.title(page["title"])
    app._login_template2_active_page = page_name
    target = page.get("focus")
    if target is None or not target.winfo_exists():
        target = (app.username_entry if page_name == "login"
                  else app.register_entries["Nama Lengkap"])
    app.root.after_idle(lambda widget=target: widget.focus_set() if widget.winfo_exists() else None)
    app.root.after_idle(lambda: layout_login_form(
        app, app.login_template2_form.winfo_width(), app.login_template2_form.winfo_height()))
    return True


def _build_auth_shell(app, title):
    """Create the unchanged two-panel branding and form shell."""
    if not getattr(app, "_login_template2_geometry_initialized", False):
        app.root.geometry("1040x700")
        app._login_template2_geometry_initialized = True
    app.root.title(title)
    # Keep the two-column login usable when restored to a smaller desktop window.
    app.root.minsize(820, 560)

    page = tk.Frame(app.root, bg=app.BG)
    page.pack(fill="both", expand=True, padx=18, pady=18)
    app._login_template2_build_page = page
    shell = tk.Frame(page, bg=app.WHITE, bd=0)
    shell.place(relx=.5, rely=.5, relwidth=.95, relheight=.94, anchor="center")
    shell.grid_columnconfigure(0, weight=44, uniform="login_panel")
    shell.grid_columnconfigure(1, weight=56, uniform="login_panel")
    shell.grid_rowconfigure(0, weight=1)

    app.login_logo_image = app._load_logo(58)
    _load_fluid_background(app)
    app.brand_canvas = tk.Canvas(shell, bg=app.NAVY, highlightthickness=0, bd=0)
    app.brand_canvas.grid(row=0, column=0, sticky="nsew")
    app.brand_canvas.bind("<Configure>", lambda event: draw_fluid_brand(app, event))

    form = tk.Canvas(shell, bg=app.NAVY, highlightthickness=0, bd=0)
    form.grid(row=0, column=1, sticky="nsew")
    app.login_template2_form = form
    app.login_compact = None
    return form


def _create_auth_card(app, form):
    card = tk.Canvas(form, bg=app.NAVY, highlightthickness=0, bd=0)
    content = tk.Frame(card, bg=app.WHITE)
    app.login_template2_card_content_window = card.create_window(
        12, 12, window=content, anchor="nw")
    app.login_template2_card = card
    app.login_template2_content = content
    return card, content


def _create_auth_field(app, parent, label_text, placeholder, icon_kind,
                       password=False, visibility_callback=None):
    label = tk.Label(parent, text=label_text, bg=app.WHITE, fg=app.NAVY,
                     font=(app.font_family, 10, "bold"), bd=0, anchor="w")
    row = _input_row(parent, app)
    icon = tk.Canvas(row, width=38, height=42, bg=app.WHITE,
                     highlightthickness=0, bd=0)
    icon.pack(side="left", padx=(5, 0))
    if icon_kind == "phone":
        _draw_phone_icon(icon)
    else:
        app.draw_input_icon(icon, icon_kind)
    entry = PlaceholderEntry(
        row, placeholder, password=password, font=(app.font_family, 11),
        relief="flat", bd=0, bg=app.WHITE, fg=app.NAVY,
        insertbackground=app.NAVY, show="*" if password else "",
    )
    entry.pack(side="left", fill="x", expand=True, ipady=12, padx=(0, 8))
    entry.bind("<FocusIn>", lambda _event, target=row: target.input_line.configure(bg=app.BLUE), add="+")
    eye = None
    if password:
        entry.password_visible = False
        eye = tk.Canvas(row, width=42, height=42, bg=app.WHITE,
                        highlightthickness=0, bd=0, cursor="hand2")
        eye.pack(side="right", padx=(0, 4))
        _draw_entry_eye(eye, False)
        if visibility_callback is None:
            eye.bind("<Button-1>", lambda _event, field=entry, canvas=eye:
                     _toggle_entry_visibility(field, canvas))
        else:
            eye.bind("<Button-1>", lambda _event: visibility_callback())
    row.field_entry = entry
    row.field_icon = icon
    row.eye_icon = eye
    entry.bind(
        "<FocusOut>",
        lambda _event, target=row, field=entry, canvas=eye:
        _on_auth_field_focus_out(app, target, field, canvas, visibility_callback),
        add="+",
    )
    return label, row, entry, eye


def _on_auth_field_focus_out(app, row, entry, eye, visibility_callback):
    row.input_line.configure(bg="#CBD5E1")
    if entry.password_field and entry.placeholder_active:
        if visibility_callback is not None:
            app.password_visible = False
            app._draw_eye_icon()
        elif eye is not None:
            _draw_entry_eye(eye, False)


def _draw_phone_icon(canvas):
    color = "#71829A"
    canvas.create_line(12, 11, 15, 8, 19, 10, 22, 14, 20, 17,
                       22, 20, 25, 22, 28, 20, 31, 23,
                       29, 27, 26, 29, 21, 28, 16, 25, 12, 21,
                       9, 16, 8, 13, 12, 11,
                       fill=color, width=1.7, smooth=True, capstyle=tk.ROUND,
                       joinstyle=tk.ROUND)


def _draw_entry_eye(canvas, visible):
    canvas.delete("all")
    color = "#71829A"
    canvas.create_line(7, 21, 12, 15, 19, 12, 26, 15, 32, 21,
                       26, 27, 19, 30, 12, 27, 7, 21,
                       fill=color, width=1.7, smooth=True, capstyle=tk.ROUND)
    canvas.create_oval(16, 18, 22, 24, outline=color, width=1.6)
    canvas.create_oval(18, 20, 20, 22, fill=color, outline=color)
    if visible:
        canvas.create_line(9, 31, 30, 10, fill=color, width=1.7, capstyle=tk.ROUND)


def _toggle_entry_visibility(entry, eye):
    if entry.placeholder_active:
        entry.focus_set()
        return
    caret = entry.index("insert")
    has_focus = entry.focus_get() == entry
    entry.password_visible = not entry.password_visible
    entry.configure(show="" if entry.password_visible else "*")
    _draw_entry_eye(eye, entry.password_visible)
    if has_focus:
        entry.focus_set()
        entry.icursor(caret)


def _focus_next_register_field(app, current):
    entries = tuple(app.register_entries.values())
    try:
        entries[entries.index(current) + 1].focus_set()
    except IndexError:
        app.register_button.focus_set()


def _bind_primary_button(app, button):
    button.bind("<Enter>", lambda _event: button.configure(bg="#1D4ED8"))
    button.bind("<Leave>", lambda _event: button.configure(bg=app.BLUE))
    button.bind("<ButtonPress-1>", lambda _event: button.configure(bg="#1E40AF"))
    button.bind("<ButtonRelease-1>", lambda _event: button.configure(bg="#1D4ED8"))


def _create_link_prompt(app, parent, prefix, link_text, callback):
    prompt = tk.Frame(parent, bg=app.WHITE)
    line = tk.Frame(prompt, bg=app.WHITE)
    line.pack(anchor="center")
    tk.Label(line, text=prefix, bg=app.WHITE, fg="#64748B",
             font=(app.font_family, 9)).pack(side="left")
    link = tk.Label(line, text=link_text, bg=app.WHITE, fg=app.BLUE,
                    font=(app.font_family, 9, "bold"), cursor="hand2")
    link.pack(side="left")
    link.bind("<Enter>", lambda _event: link.configure(fg="#1D4ED8"))
    link.bind("<Leave>", lambda _event: link.configure(fg=app.BLUE))
    link.bind("<Button-1>", lambda _event: callback())
    return prompt, link


def _finish_auth_form(app, form, card, content, regular_flow, wrap_widgets,
                      compact_flow=None, footer=None, footer_padding=(16, 0)):
    app.login_template2_regular_flow = regular_flow
    app.login_template2_compact_flow = compact_flow or regular_flow
    app.login_template2_form_flow = regular_flow
    app.login_template2_wrap_widgets = wrap_widgets
    app.login_template2_footer = footer
    app.login_template2_footer_padding = footer_padding
    app.login_template2_compact_active = None
    for widget, before, after in regular_flow:
        widget.pack(fill="x", pady=(before, after))
    if footer is not None:
        footer.pack(fill="x", pady=footer_padding)
    app.login_template2_card_window = form.create_window(0, 0, window=card, anchor="center")
    card.bind("<Configure>", lambda event: draw_login_card(app, event))
    form.bind("<Configure>", lambda event: draw_login_panel(app, event))
    for widget in wrap_widgets:
        widget.bind("<Configure>", lambda _event: form.after_idle(
            lambda: layout_login_form(app, form.winfo_width(), form.winfo_height())))


def _submit_register(app):
    app.register_button.configure(state="disabled", text="Mendaftarkan...")
    app.register_message.pack_forget()
    description = getattr(app, "login_template2_register_description", None)
    if description is not None and not description.winfo_manager():
        flow = app.login_template2_form_flow
        index = next(i for i, (widget, _before, _after) in enumerate(flow)
                     if widget is description)
        before_widget = flow[index + 1][0]
        spacing = flow[index][1:]
        description.pack(fill="x", before=before_widget, pady=spacing)
    app.root.update_idletasks()
    fields = app.register_entries
    try:
        user_id = register_customer(
            fields["Nama Lengkap"].get(), fields["Nomor HP"].get(),
            fields["Username"].get(), fields["Password"].get(),
            fields["Konfirmasi Password"].get(),
        )
    except RegistrationValidationError as exc:
        _show_register_message(app, str(exc), "#B42318")
    except RegistrationServiceError as exc:
        _show_register_message(app, str(exc), "#B42318")
    else:
        _show_register_message(app, "Akun pelanggan berhasil dibuat. Silakan masuk.", "#18794E")
        name_entry = fields["Nama Lengkap"]
        for entry in fields.values():
            entry.delete(0, "end")
            if entry is name_entry:
                entry.placeholder_active = False
                entry.configure(fg=app.NAVY)
            else:
                entry._show_placeholder()
            if entry.password_field:
                _draw_entry_eye(entry.master.eye_icon, False)
        fields["Nama Lengkap"].focus_set()
    finally:
        if app.register_button.winfo_exists():
            app.register_button.configure(state="normal", text="Daftar ke LaundryKu", bg=app.BLUE)


def _show_register_message(app, message, color):
    app.register_message.configure(text=message, fg=color)
    description = getattr(app, "login_template2_register_description", None)
    if app.login_compact and description is not None:
        description.pack_forget()
    flow = app.login_template2_form_flow
    spacing = next(((before, after) for widget, before, after in flow
                    if widget is app.register_message), (0, 3))
    app.register_message.pack(fill="x", before=app.register_button, pady=spacing)
    app.root.after_idle(lambda: layout_login_form(
        app, app.login_template2_form.winfo_width(), app.login_template2_form.winfo_height()))


def _input_row(parent, app):
    row = tk.Frame(parent, bg=app.WHITE, bd=0, height=44)
    row.pack_propagate(False)
    row.input_line = tk.Frame(row, bg="#CBD5E1", height=1, bd=0)
    row.input_line.pack(side="bottom", fill="x")
    return row


def _toggle_password(app):
    if getattr(app.password_entry, "placeholder_active", False):
        app.password_entry.focus_set()
        return
    app.toggle_password()


def _gradient_color(position):
    """Return a restrained navy-to-blue color for a vertical gradient."""
    stops = ((0.0, (21, 52, 91)), (0.55, (31, 75, 132)), (1.0, (37, 99, 235)))
    position = max(0.0, min(1.0, position))
    for (start, first), (end, second) in zip(stops, stops[1:]):
        if position <= end:
            ratio = (position - start) / (end - start)
            rgb = tuple(round(a + (b - a) * ratio) for a, b in zip(first, second))
            return "#%02x%02x%02x" % rgb
    return "#2563EB"


def draw_login_panel(app, event):
    """Paint the form-side gradient and keep the form centered responsively."""
    canvas = app.login_template2_form
    width, height = max(1, event.width), max(1, event.height)
    if width <= 1 or height <= 1:
        return

    canvas.delete("right_gradient")
    bands = min(height, 96)
    for index in range(bands):
        top = round(index * height / bands)
        bottom = round((index + 1) * height / bands) + 1
        color = _gradient_color((top + bottom) / (2 * height))
        canvas.create_rectangle(0, top, width, bottom, fill=color,
                                outline=color, tags="right_gradient")
    canvas.tag_lower("right_gradient")
    layout_login_form(app, width, height)


def layout_login_form(app, width, height):
    """Center a white login card within the gradient panel."""
    canvas = app.login_template2_form
    is_register = app.login_template2_mode == "register"
    compact = width < 480 or height < (660 if is_register else 600)
    card, content = app.login_template2_card, app.login_template2_content
    horizontal_margin = min(40, max(22, round(width * .07)))
    card_width = min(560, width - horizontal_margin * 2)
    card_inset = (10 if compact else 28) if is_register else (24 if compact else 28)
    content_width = max(220, card_width - card_inset * 2)
    if app.login_template2_compact_active != compact:
        app.login_template2_compact_active = compact
        flow = (app.login_template2_compact_flow if compact
                else app.login_template2_regular_flow)
        app.login_template2_form_flow = flow
        for widget, before, after in flow:
            if widget.winfo_manager() == "pack":
                widget.pack_configure(pady=(before, after))
        if app.login_template2_footer is not None:
            footer_top = 12 if compact and is_register else app.login_template2_footer_padding[0]
            app.login_template2_footer.pack_configure(pady=(footer_top, 0))
    if is_register:
        for row in app.login_template2_input_rows:
            row_height = 36 if compact else 44
            icon_height = 34 if compact else 42
            entry_ipady = 5 if compact else 8
            row.configure(height=row_height)
            row.field_icon.configure(height=icon_height)
            row.field_entry.pack_configure(ipady=entry_ipady)
            if row.eye_icon is not None:
                row.eye_icon.configure(height=icon_height)
    for widget in app.login_template2_wrap_widgets:
        if widget is not None:
            if widget.cget("wraplength") != content_width:
                widget.configure(wraplength=content_width)

    content.update_idletasks()
    vertical_margin = 14 if is_register and compact else 40
    card_height = min(max(360, content.winfo_reqheight() + card_inset * 2),
                      max(360, height - vertical_margin))
    canvas.coords(app.login_template2_card_window, width / 2, height / 2)
    canvas.itemconfigure(app.login_template2_card_window,
                         width=card_width, height=card_height)
    card.coords(app.login_template2_card_content_window, card_inset, card_inset)
    card.itemconfigure(app.login_template2_card_content_window,
                       width=content_width, height=max(240, card_height - card_inset * 2))


def draw_login_card(app, event):
    """Draw a clean white card with subtle rounded corners using native Canvas."""
    card = app.login_template2_card
    width, height = max(1, event.width), max(1, event.height)
    if width <= 1 or height <= 1:
        return
    form = app.login_template2_form
    center_y = card.winfo_rooty() - form.winfo_rooty() + height / 2
    panel_height = max(1, form.winfo_height())
    card.configure(bg=_gradient_color(center_y / panel_height))
    card.delete("card_shape")
    radius = min(14, width / 2, height / 2)
    shapes = (
        ("rectangle", (radius, 0, width - radius, height)),
        ("rectangle", (0, radius, width, height - radius)),
        ("oval", (0, 0, radius * 2, radius * 2)),
        ("oval", (width - radius * 2, 0, width, radius * 2)),
        ("oval", (0, height - radius * 2, radius * 2, height)),
        ("oval", (width - radius * 2, height - radius * 2, width, height)),
    )
    for kind, coords in shapes:
        creator = card.create_rectangle if kind == "rectangle" else card.create_oval
        creator(*coords, fill=app.WHITE, outline=app.WHITE, tags="card_shape")
    card.tag_lower("card_shape")


def _load_fluid_background(app):
    """Load the project-local artwork once and retain its high-resolution source."""
    if getattr(app, "login_template2_background_source", None) is not None:
        return
    if not FLUID_BACKGROUND_PATH.is_file():
        logger.error("Background Fluid Blue tidak ditemukan: %s", FLUID_BACKGROUND_PATH)
        app.login_template2_background_source = None
        return
    try:
        with Image.open(FLUID_BACKGROUND_PATH) as source:
            app.login_template2_background_source = source.convert("RGB")
    except Exception:
        logger.exception("Background Fluid Blue gagal dimuat: %s", FLUID_BACKGROUND_PATH)
        app.login_template2_background_source = None


def _draw_resized_background(app, canvas, width, height):
    """Cover the canvas with the artwork, preserving its aspect ratio and detail."""
    size = (width, height)
    if (getattr(app, "login_template2_background_size", None) == size
            and getattr(app, "login_template2_background_image", None) is not None):
        canvas.create_image(0, 0, image=app.login_template2_background_image,
                            anchor="nw", tags="background")
        return

    source = app.login_template2_background_source
    if source is None:
        return
    scale = max(width / source.width, height / source.height)
    resized_width = max(width, round(source.width * scale))
    resized_height = max(height, round(source.height * scale))
    resized = source.resize((resized_width, resized_height), Image.Resampling.LANCZOS)
    # Keep the lower liquid detail in frame when a wide panel needs vertical crop.
    crop_left = (resized_width - width) // 2
    crop_top = resized_height - height
    cropped = resized.crop((crop_left, crop_top, crop_left + width, crop_top + height))
    app.login_template2_background_image = ImageTk.PhotoImage(cropped, master=app.root)
    app.login_template2_background_size = size
    resized.close()
    cropped.close()
    canvas.create_image(0, 0, image=app.login_template2_background_image,
                        anchor="nw", tags="background")


def draw_fluid_brand(app, event):
    """Place the responsive liquid artwork behind the independent brand copy."""
    canvas = app.brand_canvas
    canvas.delete("all")
    width, height = max(1, event.width), max(1, event.height)
    if width <= 1 or height <= 1:
        return
    compact = width < COMPACT_BREAKPOINT_WIDTH or height < COMPACT_BREAKPOINT_HEIGHT
    if compact != app.login_compact:
        app.login_compact = compact

    _draw_resized_background(app, canvas, width, height)

    if app.login_logo_image is not None:
        logo_size = app.login_logo_image.width()
        logo_x = width * .13 + logo_size / 2
        brand_y = height * .19
        canvas.create_image(logo_x, brand_y, image=app.login_logo_image, anchor="center")
        text_x = width * .13 + logo_size + 14
        canvas.create_text(text_x, brand_y - 8, text="LaundryKu", anchor="w",
                           fill=app.WHITE, font=(app.font_family, 22, "bold"))
        canvas.create_text(text_x + 1, brand_y + 17, text="MANAJEMEN LAUNDRY", anchor="w",
                           fill="#C6D8F3", font=(app.font_family, 8, "bold"))
    else:
        canvas.create_text(width * .13, height * .19, text="LaundryKu", anchor="w",
                           fill=app.WHITE, font=(app.font_family, 22, "bold"))
        canvas.create_text(width * .13, height * .19 + 25, text="MANAJEMEN LAUNDRY", anchor="w",
                           fill="#C6D8F3", font=(app.font_family, 8, "bold"))

    if compact:
        headline_width = width * .80
        compact_font = getattr(app, "login_template2_headline_font", None)
        if compact_font is None:
            compact_font = tkfont.Font(root=app.root, family=app.font_family,
                                       size=24, weight="bold")
            app.login_template2_headline_font = compact_font
        for headline_size in range(29, 17, -1):
            compact_font.configure(size=headline_size)
            line_width = max(compact_font.measure("Laundry lebih mudah."),
                             compact_font.measure("Bisnis lebih teratur."))
            if line_width <= headline_width:
                break
        headline_font = compact_font
        headline_options = {"width": headline_width}
    else:
        headline_size = max(26, min(32, int(width / 13)))
        headline_font = (app.font_family, headline_size, "bold")
        headline_options = {}
    headline_x = width * (.10 if compact else .12)
    headline_offset = max(35, min(45, round(height * .065)))
    headline_y = height * .405 - headline_offset
    headline = canvas.create_text(headline_x, headline_y,
                                  text="Laundry lebih mudah.\nBisnis lebih teratur.",
                                  anchor="nw", justify="left", fill=app.WHITE,
                                  font=headline_font,
                                  **headline_options)
    headline_bounds = canvas.bbox(headline)
    if headline_bounds is None:
        return
    # Compute the copy gap from the rendered headline, so font metrics and panel
    # resizing cannot push the description up into the two headline lines.
    description_gap = max(18, round(height * .035)) if not compact else max(16, round(height * .03))
    description_y = headline_bounds[3] + description_gap
    description_x = width * (.105 if compact else .125)
    description_width = width * (.76 if compact else .75)
    description_font = 10 if compact else 11
    canvas.create_text(description_x, description_y,
                       text="Kelola pesanan, pelanggan, dan operasional\ndalam satu aplikasi yang terintegrasi.",
                       anchor="nw", justify="left", width=description_width,
                       fill="#C9D8ED", font=(app.font_family, description_font))
