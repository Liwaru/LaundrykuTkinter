"""Template 2: Fluid Blue login UI for LaundryKu Desktop."""

import tkinter as tk
from tkinter import font as tkfont
import logging

from PIL import Image, ImageTk

from app.database.connection import PROJECT_ROOT

COMPACT_BREAKPOINT_WIDTH = 480
COMPACT_BREAKPOINT_HEIGHT = 600
logger = logging.getLogger("laundryku.ui.login")
FLUID_BACKGROUND_PATH = PROJECT_ROOT / "assets" / "login_fluid_background.png"


def build_login(app):
    """Build the alternate visual while reusing shared app authentication."""
    for child in app.root.winfo_children():
        child.destroy()
    app.root.title("LaundryKu | Masuk")
    app.root.geometry("1040x700")
    # Keep the two-column login usable when restored to a smaller desktop window.
    app.root.minsize(820, 560)

    page = tk.Frame(app.root, bg=app.BG)
    page.pack(fill="both", expand=True, padx=18, pady=18)
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

    card = tk.Canvas(form, bg=app.NAVY, highlightthickness=0, bd=0)
    content = tk.Frame(card, bg=app.WHITE)
    app.login_template2_card_content_window = card.create_window(
        12, 12, window=content, anchor="nw")
    app.login_template2_card = card
    app.login_template2_content = content

    heading = tk.Label(content, text="Masuk ke LaundryKu", bg=app.WHITE, fg=app.NAVY,
                       font=(app.font_family, 25, "bold"), bd=0)
    form_description = tk.Label(content, text="Masuk untuk melanjutkan aktivitasmu.", bg=app.WHITE,
                                fg="#64748B", font=(app.font_family, 10), wraplength=400, bd=0)
    username_label = tk.Label(content, text="Username", bg=app.WHITE, fg=app.NAVY,
                              font=(app.font_family, 10, "bold"), bd=0)
    username_row = _input_row(content, app)
    username_icon = tk.Canvas(username_row, width=38, height=42, bg=app.BG,
                              highlightthickness=0, bd=0)
    username_icon.pack(side="left", padx=(5, 0))
    app.draw_input_icon(username_icon, "user")
    app.username_entry = tk.Entry(username_row, font=(app.font_family, 11), relief="flat", bd=0,
                                  bg=app.BG, fg=app.NAVY, insertbackground=app.NAVY)
    app.username_entry.pack(side="left", fill="x", expand=True, ipady=12, padx=(0, 12))
    app.username_entry.bind("<FocusIn>", lambda _event: username_row.configure(highlightbackground="#A9C5F5"))
    app.username_entry.bind("<FocusOut>", lambda _event: username_row.configure(highlightbackground="#DCE4EF"))
    app.username_entry.bind("<Return>", lambda _event: app.password_entry.focus_set())

    password_label = tk.Label(content, text="Password", bg=app.WHITE, fg=app.NAVY,
                              font=(app.font_family, 10, "bold"), bd=0)
    password_row = _input_row(content, app)
    password_icon = tk.Canvas(password_row, width=38, height=42, bg=app.BG,
                              highlightthickness=0, bd=0)
    password_icon.pack(side="left", padx=(5, 0))
    app.draw_input_icon(password_icon, "lock")
    app.password_entry = tk.Entry(password_row, font=(app.font_family, 11), relief="flat", bd=0,
                                  bg=app.BG, fg=app.NAVY, insertbackground=app.NAVY, show="*")
    app.password_entry.pack(side="left", fill="x", expand=True, ipady=12, padx=(0, 2))
    app.password_entry.bind("<FocusIn>", lambda _event: password_row.configure(highlightbackground="#A9C5F5"))
    app.password_entry.bind("<FocusOut>", lambda _event: password_row.configure(highlightbackground="#DCE4EF"))
    app.password_entry.bind("<Return>", lambda _event: app.submit_login())
    app.password_visible = False
    app.eye_canvas = tk.Canvas(password_row, width=42, height=42, bg=app.BG,
                               highlightthickness=0, bd=0, cursor="hand2")
    app.eye_canvas.pack(side="right", padx=(0, 4))
    app._draw_eye_icon()
    app.eye_canvas.bind("<Button-1>", lambda _event: app.toggle_password())

    app.login_message = tk.Label(content, text="", bg=app.WHITE, fg="#C24141",
                                 font=(app.font_family, 9), anchor="w", wraplength=420, bd=0)
    app.login_button = tk.Button(content, text="Masuk ke LaundryKu", command=app.submit_login,
                                 bg=app.BLUE, fg=app.WHITE, activebackground="#1D4ED8",
                                 activeforeground=app.WHITE, relief="flat", bd=0,
                                 cursor="hand2", font=(app.font_family, 10, "bold"), pady=13)
    app.login_button.bind("<Enter>", lambda _event: app._set_login_button_color("#1D4ED8"))
    app.login_button.bind("<Leave>", lambda _event: app._set_login_button_color(app.BLUE))
    app.login_button.bind("<ButtonPress-1>", lambda _event: app._set_login_button_color("#1E40AF"))
    app.login_button.bind("<ButtonRelease-1>", lambda _event: app._set_login_button_color("#1D4ED8"))

    app.login_template2_form_flow = [
        (heading, 0, 8), (form_description, 0, 24),
        (username_label, 0, 8), (username_row, 0, 16),
        (password_label, 0, 8), (password_row, 0, 4),
        (app.login_message, 0, 6), (app.login_button, 0, 0),
    ]
    for widget, _before, after in app.login_template2_form_flow:
        widget.pack(fill="x", pady=(0, after))
    app.login_template2_card_window = form.create_window(
        0, 0, window=card, anchor="center")
    card.bind("<Configure>", lambda event: draw_login_card(app, event))
    form.bind("<Configure>", lambda event: draw_login_panel(app, event))
    app.login_message.bind("<Configure>", lambda _event: form.after_idle(
        lambda: layout_login_form(app, form.winfo_width(), form.winfo_height())))
    app.username_entry.focus_set()


def _input_row(parent, app):
    return tk.Frame(parent, bg=app.BG, highlightbackground="#DCE4EF",
                    highlightcolor="#A9C5F5", highlightthickness=1, bd=0)


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
    compact = width < 480 or height < 600
    card, content = app.login_template2_card, app.login_template2_content
    horizontal_margin = min(40, max(22, round(width * .07)))
    card_width = min(560, width - horizontal_margin * 2)
    card_inset = 24 if compact else 28
    content_width = max(220, card_width - card_inset * 2)
    flow = app.login_template2_form_flow
    for widget, _before, _after in flow:
        if widget in (flow[1][0], app.login_message):
            if widget.cget("wraplength") != content_width:
                widget.configure(wraplength=content_width)

    content.update_idletasks()
    card_height = min(max(360, content.winfo_reqheight() + card_inset * 2),
                      max(360, height - 40))
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
