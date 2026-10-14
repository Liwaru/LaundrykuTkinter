"""Approved Template 1: Blue Wave Premium login UI."""

import tkinter as tk
import math


def build_login(app):
    """Render the initial login screen; no database query runs before submit."""
    self = app
    for child in self.root.winfo_children():
        child.destroy()
    self.root.title("LaundryKu | Masuk")
    self.root.geometry("1040x700")
    login_page = tk.Frame(self.root, bg=self.BG)
    login_page.pack(fill="both", expand=True, padx=18, pady=18)
    card = tk.Frame(login_page, bg=self.WHITE, highlightthickness=0, bd=0)
    card.place(relx=0.5, rely=0.5, relwidth=0.95, relheight=0.94, anchor="center")
    card.grid_columnconfigure(0, weight=44, uniform="login_panel")
    card.grid_columnconfigure(1, weight=56, uniform="login_panel")
    card.grid_rowconfigure(0, weight=1)

    self.login_logo_image = self._load_logo(60)
    self.brand_canvas = tk.Canvas(card, bg=self.NAVY, highlightthickness=0, bd=0)
    self.brand_canvas.grid(row=0, column=0, sticky="nsew")
    self.brand_canvas.bind("<Configure>", self._draw_brand_accents)

    form = tk.Frame(card, bg=self.WHITE, padx=48, pady=30)
    form.grid(row=0, column=1, sticky="nsew")
    form.grid_rowconfigure(0, weight=1)
    form.grid_columnconfigure(0, weight=1)
    content = tk.Frame(form, bg=self.WHITE)
    content.grid(row=0, column=0, sticky="ew")
    tk.Label(content, text="WELCOME BACK", bg=self.WHITE, fg=self.BLUE,
             font=(self.font_family, 9, "bold")).pack(anchor="w", pady=(0, 9))
    tk.Label(content, text="Masuk ke LaundryKu", bg=self.WHITE, fg=self.NAVY,
             font=(self.font_family, 25, "bold")).pack(anchor="w", pady=(0, 7))
    tk.Label(content, text="Masuk untuk melanjutkan aktivitasmu.", bg=self.WHITE,
             fg=self.MUTED, font=(self.font_family, 10), wraplength=400).pack(anchor="w", pady=(0, 27))

    tk.Label(content, text="Username", bg=self.WHITE, fg=self.NAVY,
             font=(self.font_family, 10, "bold")).pack(anchor="w", pady=(0, 8))
    username_row = tk.Frame(content, bg=self.BG, highlightbackground="#DCE4EF",
                            highlightcolor="#A9C5F5", highlightthickness=1, bd=0)
    username_row.pack(fill="x", pady=(0, 18))
    username_icon = tk.Canvas(username_row, width=38, height=42, bg=self.BG,
                              highlightthickness=0, bd=0)
    username_icon.pack(side="left", padx=(5, 0))
    self.draw_input_icon(username_icon, "user")
    self.username_entry = tk.Entry(username_row, font=(self.font_family, 11), relief="flat", bd=0,
                                   bg=self.BG, fg=self.NAVY, insertbackground=self.NAVY)
    self.username_entry.pack(side="left", fill="x", expand=True, ipady=12, padx=(0, 12))
    self.username_entry.bind("<FocusIn>", lambda _event: username_row.configure(highlightbackground="#A9C5F5"))
    self.username_entry.bind("<FocusOut>", lambda _event: username_row.configure(highlightbackground="#DCE4EF"))
    self.username_entry.bind("<Return>", lambda _event: self.password_entry.focus_set())

    tk.Label(content, text="Password", bg=self.WHITE, fg=self.NAVY,
             font=(self.font_family, 10, "bold")).pack(anchor="w", pady=(0, 8))
    password_row = tk.Frame(content, bg=self.BG, highlightbackground="#DCE4EF",
                            highlightcolor="#A9C5F5", highlightthickness=1, bd=0)
    password_row.pack(fill="x")
    password_icon = tk.Canvas(password_row, width=38, height=42, bg=self.BG,
                              highlightthickness=0, bd=0)
    password_icon.pack(side="left", padx=(5, 0))
    self.draw_input_icon(password_icon, "lock")
    self.password_entry = tk.Entry(password_row, font=(self.font_family, 11), relief="flat", bd=0,
                                   bg=self.BG, fg=self.NAVY, insertbackground=self.NAVY,
                                   show="*")
    self.password_entry.pack(side="left", fill="x", expand=True, ipady=12, padx=(0, 2))
    self.password_entry.bind("<FocusIn>", lambda _event: password_row.configure(highlightbackground="#A9C5F5"))
    self.password_entry.bind("<FocusOut>", lambda _event: password_row.configure(highlightbackground="#DCE4EF"))
    self.password_entry.bind("<Return>", lambda _event: self.submit_login())
    self.password_visible = False
    self.eye_canvas = tk.Canvas(password_row, width=42, height=42, bg=self.BG,
                                highlightthickness=0, bd=0, cursor="hand2")
    self.eye_canvas.pack(side="right", padx=(0, 4))
    self._draw_eye_icon()
    self.eye_canvas.bind("<Button-1>", lambda _event: self.toggle_password())

    self.login_message = tk.Label(content, text="", bg=self.WHITE, fg="#C24141",
                                  font=(self.font_family, 9), anchor="w", wraplength=420)
    self.login_message.pack(fill="x", pady=(8, 2))
    self.login_button = tk.Button(content, text="Masuk ke LaundryKu", command=self.submit_login,
                                  bg=self.BLUE, fg=self.WHITE, activebackground="#1D4ED8",
                                  activeforeground=self.WHITE, relief="flat", bd=0,
                                  cursor="hand2", font=(self.font_family, 10, "bold"),
                                  pady=13)
    self.login_button.pack(fill="x", pady=(8, 0))
    self.login_button.bind("<Enter>", lambda _event: self._set_login_button_color("#1D4ED8"))
    self.login_button.bind("<Leave>", lambda _event: self._set_login_button_color(self.BLUE))
    self.login_button.bind("<ButtonPress-1>", lambda _event: self._set_login_button_color("#1E40AF"))
    self.login_button.bind("<ButtonRelease-1>", lambda _event: self._set_login_button_color("#1D4ED8"))
    security_note = tk.Frame(content, bg=self.WHITE)
    security_note.pack(anchor="center", pady=(20, 0))
    shield = tk.Canvas(security_note, width=16, height=18, bg=self.WHITE, highlightthickness=0, bd=0)
    shield.pack(side="left", padx=(0, 7))
    shield.create_polygon(8, 1, 14, 3, 13, 11, 8, 16, 3, 11, 2, 3,
                          outline="#7B91AD", fill="", width=1.3)
    shield.create_line(5, 8, 7, 10, 11, 6, fill="#7B91AD", width=1.2)
    tk.Label(security_note, text="Akses sesuai hak akun", bg=self.WHITE, fg=self.MUTED,
             font=(self.font_family, 9)).pack(side="left")
    self.username_entry.focus_set()


def draw_brand_accents(self, event):
    canvas = self.brand_canvas
    canvas.delete("all")
    width, height = max(1, event.width), max(1, event.height)
    if width <= 1 or height <= 1:
        return
    # Tk Canvas has no alpha compositing; narrow adjacent bands create a light,
    # resize-safe navy-to-blue gradient without external background images.
    top_rgb, bottom_rgb = (21, 52, 91), (31, 83, 146)
    bands = 88
    for band in range(bands):
        t = band / max(1, bands - 1)
        rgb = tuple(round(a + (b - a) * t) for a, b in zip(top_rgb, bottom_rgb))
        color = "#%02x%02x%02x" % rgb
        y0, y1 = height * band / bands, height * (band + 1) / bands + 1
        canvas.create_rectangle(0, y0, width, y1, fill=color, outline=color)

    # Subtle sweeping linework and layered waves are confined to the bottom.
    for inset, color in ((0, "#204B7A"), (15, "#215181")):
        canvas.create_line(-width * .08, height * .92 + inset,
                           width * .20, height * .73 + inset,
                           width * .55, height * .82 + inset,
                           width * .91, height * .68 + inset,
                           width * 1.08, height * .77 + inset,
                           fill=color, width=1.1, smooth=True, splinesteps=24)
    step = max(16, int(width / 42))
    for baseline, amplitude, phase, color in (
        (.91, 19, .3, "#24598A"), (.96, 17, 1.4, "#1E5487"),
    ):
        points = []
        for x in range(0, width + step, step):
            ratio = min(1.0, x / width)
            points.extend((x, height * baseline + math.sin(ratio * math.pi * 2 + phase) * amplitude))
        canvas.create_line(*points, fill=color, width=1.4, smooth=True, splinesteps=20)
    for x, y, radius, color in ((.12, .78, 3, "#22D3EE"), (.86, .84, 2.5, "#49CBE4"),
                                (.78, .95, 3.5, "#2563EB")):
        cx, cy = width * x, height * y
        canvas.create_oval(cx-radius, cy-radius, cx+radius, cy+radius, fill=color, outline="")

    # Draw the complete brand lockup directly on the canvas (no inset card).
    center_x = width * .5
    brand_y = height * .235
    if self.login_logo_image is not None:
        canvas.create_image(width * .22, brand_y, image=self.login_logo_image, anchor="center")
        text_x = width * .34
        canvas.create_text(text_x, brand_y - 10, text="LaundryKu", anchor="w",
                           fill=self.WHITE, font=(self.font_family, 23, "bold"))
        canvas.create_text(text_x + 1, brand_y + 15, text="MANAJEMEN LAUNDRY", anchor="w",
                           fill="#BDD2F1", font=(self.font_family, 8, "bold"))
    else:
        canvas.create_text(center_x, brand_y - 8, text="LaundryKu", anchor="center",
                           fill=self.WHITE, font=(self.font_family, 23, "bold"))
        canvas.create_text(center_x, brand_y + 17, text="MANAJEMEN LAUNDRY", anchor="center",
                           fill="#BDD2F1", font=(self.font_family, 8, "bold"))
    hero_size = max(24, min(32, int(width / 14)))
    canvas.create_text(center_x, height * .455,
                       text="Laundry lebih mudah.\nBisnis lebih teratur.",
                       anchor="center", justify="center", fill=self.WHITE,
                       font=(self.font_family, hero_size, "bold"))
    canvas.create_text(center_x, height * .59,
                       text="Kelola pesanan, pelanggan, dan operasional\ndalam satu aplikasi yang terintegrasi.",
                       anchor="center", justify="center", fill="#C2D2E7",
                       font=(self.font_family, 9))
