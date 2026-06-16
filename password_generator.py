"""
CyberShield Toolkit - Password Generator Module
================================================
A self-contained password generator module for integration into the
CyberShield Toolkit dashboard. Renders entirely within a provided parent_frame.

Public API:
    launch(parent_frame) -> None
"""

import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import secrets


# ─────────────────────────────────────────────
#  THEME TOKENS  (dark cybersecurity palette)
# ─────────────────────────────────────────────
COLORS = {
    "bg_deep":      "#0A0E17",   # near-black navy — primary background
    "bg_panel":     "#111827",   # raised panel surface
    "bg_card":      "#1A2235",   # card / section background
    "accent_cyan":  "#00D4FF",   # primary interactive accent
    "accent_green": "#00FF88",   # success / strength indicator
    "accent_amber": "#FFB800",   # warning strength level
    "accent_red":   "#FF3B5C",   # danger / weak strength
    "border":       "#1E3050",   # subtle divider / border
    "text_primary": "#E2E8F0",   # body text
    "text_muted":   "#4A6080",   # labels, secondary text
    "text_accent":  "#00D4FF",   # highlighted labels
    "btn_bg":       "#0D2137",   # button resting state
    "btn_hover":    "#0A3560",   # button hover state
    "entry_bg":     "#0D1829",   # input field background
    "entry_border": "#1E3A5F",   # input field border
}

FONT_MONO  = ("Courier New", 10)
FONT_MONO_LG = ("Courier New", 13, "bold")
FONT_UI    = ("Segoe UI", 9)
FONT_UI_SM = ("Segoe UI", 8)
FONT_HEAD  = ("Segoe UI", 11, "bold")
FONT_LABEL = ("Segoe UI", 8)


# ─────────────────────────────────────────────
#  PASSWORD GENERATION LOGIC
# ─────────────────────────────────────────────

CHAR_SETS = {
    "uppercase":  string.ascii_uppercase,
    "lowercase":  string.ascii_lowercase,
    "digits":     string.digits,
    "symbols":    "!@#$%^&*()-_=+[]{}|;:,.<>?",
    "ambiguous":  "0O1lI",          # characters to optionally exclude
}

def generate_password(length: int,
                      use_upper: bool,
                      use_lower: bool,
                      use_digits: bool,
                      use_symbols: bool,
                      exclude_ambiguous: bool) -> str:
    """Build a cryptographically strong password from the selected character pools."""
    pool = ""
    required = []   # guarantee at least one char from every chosen set

    if use_upper:
        chars = CHAR_SETS["uppercase"]
        if exclude_ambiguous:
            chars = "".join(c for c in chars if c not in CHAR_SETS["ambiguous"])
        pool += chars
        required.append(secrets.choice(chars))

    if use_lower:
        chars = CHAR_SETS["lowercase"]
        if exclude_ambiguous:
            chars = "".join(c for c in chars if c not in CHAR_SETS["ambiguous"])
        pool += chars
        required.append(secrets.choice(chars))

    if use_digits:
        chars = CHAR_SETS["digits"]
        if exclude_ambiguous:
            chars = "".join(c for c in chars if c not in CHAR_SETS["ambiguous"])
        pool += chars
        required.append(secrets.choice(chars))

    if use_symbols:
        chars = CHAR_SETS["symbols"]
        pool += chars
        required.append(secrets.choice(chars))

    if not pool:
        return ""

    # Fill remaining slots from the full pool, then shuffle
    remaining = length - len(required)
    password_chars = required + [secrets.choice(pool) for _ in range(max(0, remaining))]
    secrets.SystemRandom().shuffle(password_chars)
    return "".join(password_chars[:length])


def score_password(password: str) -> tuple[int, str, str]:
    """
    Returns (score 0-4, label, hex_color).
    Scoring factors: length, character variety, entropy estimate.
    """
    if not password:
        return 0, "—", COLORS["text_muted"]

    score = 0
    has_upper   = any(c.isupper()  for c in password)
    has_lower   = any(c.islower()  for c in password)
    has_digit   = any(c.isdigit()  for c in password)
    has_symbol  = any(c in CHAR_SETS["symbols"] for c in password)
    variety     = sum([has_upper, has_lower, has_digit, has_symbol])
    length      = len(password)

    if length >= 8:  score += 1
    if length >= 16: score += 1
    if variety >= 3: score += 1
    if variety == 4: score += 1

    labels = {0: "Weak", 1: "Fair", 2: "Good", 3: "Strong", 4: "Excellent"}
    colors = {
        0: COLORS["accent_red"],
        1: COLORS["accent_red"],
        2: COLORS["accent_amber"],
        3: COLORS["accent_green"],
        4: COLORS["accent_cyan"],
    }
    return score, labels[score], colors[score]


# ─────────────────────────────────────────────
#  REUSABLE WIDGET HELPERS
# ─────────────────────────────────────────────

def _styled_frame(parent, **kw) -> tk.Frame:
    kw.setdefault("bg", COLORS["bg_card"])
    kw.setdefault("bd", 0)
    kw.setdefault("highlightthickness", 1)
    kw.setdefault("highlightbackground", COLORS["border"])
    return tk.Frame(parent, **kw)


def _label(parent, text, font=FONT_UI, fg=None, **kw) -> tk.Label:
    fg = fg or COLORS["text_primary"]
    return tk.Label(parent, text=text, font=font,
                    fg=fg, bg=kw.pop("bg", COLORS["bg_card"]),
                    anchor=kw.pop("anchor", "w"), **kw)


def _checkbutton(parent, text, variable, command=None) -> tk.Checkbutton:
    return tk.Checkbutton(
        parent, text=text, variable=variable,
        font=FONT_UI, fg=COLORS["text_primary"],
        bg=COLORS["bg_card"],
        activebackground=COLORS["bg_card"],
        activeforeground=COLORS["accent_cyan"],
        selectcolor=COLORS["bg_deep"],
        command=command,
        cursor="hand2",
    )


def _cyber_button(parent, text, command, accent=False) -> tk.Button:
    """A flat button with hover effects wired in."""
    bg  = COLORS["accent_cyan"] if accent else COLORS["btn_bg"]
    fg  = COLORS["bg_deep"]     if accent else COLORS["accent_cyan"]
    abg = COLORS["accent_green"] if accent else COLORS["btn_hover"]
    afg = COLORS["bg_deep"]

    btn = tk.Button(
        parent, text=text, command=command,
        font=("Segoe UI", 9, "bold") if accent else FONT_UI,
        fg=fg, bg=bg,
        activeforeground=afg, activebackground=abg,
        relief="flat", bd=0, padx=14, pady=6,
        cursor="hand2",
        highlightthickness=0,
    )
    btn.bind("<Enter>", lambda e: btn.config(bg=abg, fg=afg))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg,  fg=fg))
    return btn


# ─────────────────────────────────────────────
#  MAIN MODULE ENTRY POINT
# ─────────────────────────────────────────────

def launch(parent_frame: tk.Frame) -> None:
    """
    Render the Password Generator UI inside parent_frame.
    Called by the CyberShield Toolkit dashboard.
    """

    # ── Clear any previously loaded module content ────────────────────────
    for widget in parent_frame.winfo_children():
        widget.destroy()

    # ── Root container fills the given frame ──────────────────────────────
    root = tk.Frame(parent_frame, bg=COLORS["bg_deep"])
    root.pack(fill="both", expand=True)

    # ── State variables ───────────────────────────────────────────────────
    length_var          = tk.IntVar(value=16)
    use_upper_var       = tk.BooleanVar(value=True)
    use_lower_var       = tk.BooleanVar(value=True)
    use_digits_var      = tk.BooleanVar(value=True)
    use_symbols_var     = tk.BooleanVar(value=True)
    excl_ambiguous_var  = tk.BooleanVar(value=False)
    password_var        = tk.StringVar(value="")
    quantity_var        = tk.IntVar(value=1)

    # ── Header bar ────────────────────────────────────────────────────────
    header = tk.Frame(root, bg=COLORS["bg_panel"],
                      highlightthickness=1,
                      highlightbackground=COLORS["border"])
    header.pack(fill="x", padx=0, pady=0)

    # Left: icon + title
    tk.Label(header, text="🔐", font=("Segoe UI", 16),
             bg=COLORS["bg_panel"], fg=COLORS["accent_cyan"]
             ).pack(side="left", padx=(16, 6), pady=10)
    tk.Label(header, text="Password Generator",
             font=("Segoe UI", 13, "bold"),
             bg=COLORS["bg_panel"], fg=COLORS["text_primary"]
             ).pack(side="left", pady=10)

    # Right: status chip
    status_lbl = tk.Label(header, text="● READY",
                          font=FONT_UI_SM,
                          bg=COLORS["bg_panel"], fg=COLORS["accent_green"])
    status_lbl.pack(side="right", padx=16, pady=10)

    # ── Two-column content area ───────────────────────────────────────────
    content = tk.Frame(root, bg=COLORS["bg_deep"])
    content.pack(fill="both", expand=True, padx=16, pady=12)
    content.columnconfigure(0, weight=1)
    content.columnconfigure(1, weight=1)
    content.rowconfigure(0, weight=1)

    # ── LEFT COLUMN ──────────────────────────────────────────────────────
    left_col = tk.Frame(content, bg=COLORS["bg_deep"])
    left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

    # — Section: Length ——————————————————————————————————————————————
    length_card = _styled_frame(left_col)
    length_card.pack(fill="x", pady=(0, 10))

    _label(length_card, "PASSWORD LENGTH",
           font=("Courier New", 8, "bold"),
           fg=COLORS["text_muted"]
           ).pack(anchor="w", padx=14, pady=(12, 4))

    len_row = tk.Frame(length_card, bg=COLORS["bg_card"])
    len_row.pack(fill="x", padx=14, pady=(0, 4))

    length_display = tk.Label(len_row, textvariable=length_var,
                              font=("Courier New", 22, "bold"),
                              fg=COLORS["accent_cyan"],
                              bg=COLORS["bg_card"], width=4, anchor="w")
    length_display.pack(side="left")

    tk.Label(len_row, text="chars",
             font=FONT_UI_SM, fg=COLORS["text_muted"],
             bg=COLORS["bg_card"]
             ).pack(side="left", padx=(4, 0), anchor="s", pady=4)

    # Slider (custom styled via ttk.Scale or tk.Scale)
    length_slider = tk.Scale(
        length_card, from_=4, to=128,
        orient="horizontal", variable=length_var,
        bg=COLORS["bg_card"], fg=COLORS["text_muted"],
        troughcolor=COLORS["bg_deep"],
        activebackground=COLORS["accent_cyan"],
        highlightthickness=0, bd=0,
        showvalue=False, sliderlength=18,
        sliderrelief="flat",
    )
    length_slider.pack(fill="x", padx=14, pady=(0, 12))

    # Quick preset buttons
    preset_row = tk.Frame(length_card, bg=COLORS["bg_card"])
    preset_row.pack(fill="x", padx=14, pady=(0, 12))

    _label(preset_row, "Presets:", font=FONT_UI_SM,
           fg=COLORS["text_muted"], bg=COLORS["bg_card"]
           ).pack(side="left")

    for preset_len in (8, 12, 16, 24, 32):
        btn = tk.Button(
            preset_row, text=str(preset_len),
            font=("Courier New", 8),
            fg=COLORS["text_muted"], bg=COLORS["bg_deep"],
            activeforeground=COLORS["accent_cyan"],
            activebackground=COLORS["bg_deep"],
            relief="flat", bd=0, padx=6, pady=2,
            cursor="hand2",
        )
        btn.config(command=lambda v=preset_len, b=btn: [
            length_var.set(v),
            _flash_btn(b)
        ])
        btn.pack(side="left", padx=2)

    # — Section: Character Sets ——————————————————————————————————————
    charset_card = _styled_frame(left_col)
    charset_card.pack(fill="x", pady=(0, 10))

    _label(charset_card, "CHARACTER SETS",
           font=("Courier New", 8, "bold"),
           fg=COLORS["text_muted"]
           ).pack(anchor="w", padx=14, pady=(12, 6))

    options = [
        ("ABC  Uppercase  (A–Z)", use_upper_var),
        ("abc  Lowercase  (a–z)", use_lower_var),
        ("123  Digits     (0–9)", use_digits_var),
        ("!@#  Symbols",          use_symbols_var),
    ]
    for label_text, var in options:
        _checkbutton(charset_card, label_text, var
                     ).pack(anchor="w", padx=14, pady=2)

    tk.Frame(charset_card, bg=COLORS["border"], height=1
             ).pack(fill="x", padx=14, pady=8)

    _checkbutton(charset_card,
                 "⊘  Exclude ambiguous characters (0, O, l, 1, I)",
                 excl_ambiguous_var
                 ).pack(anchor="w", padx=14, pady=(0, 12))

    # — Section: Batch Generation ————————————————————————————————————
    batch_card = _styled_frame(left_col)
    batch_card.pack(fill="x", pady=(0, 10))

    _label(batch_card, "BATCH GENERATION",
           font=("Courier New", 8, "bold"),
           fg=COLORS["text_muted"]
           ).pack(anchor="w", padx=14, pady=(12, 6))

    qty_row = tk.Frame(batch_card, bg=COLORS["bg_card"])
    qty_row.pack(fill="x", padx=14, pady=(0, 12))

    _label(qty_row, "Generate", font=FONT_UI,
           fg=COLORS["text_primary"], bg=COLORS["bg_card"]
           ).pack(side="left")

    qty_spin = tk.Spinbox(
        qty_row, from_=1, to=50,
        textvariable=quantity_var, width=4,
        font=FONT_MONO,
        fg=COLORS["accent_cyan"], bg=COLORS["entry_bg"],
        insertbackground=COLORS["accent_cyan"],
        relief="flat", bd=1,
        highlightthickness=1,
        highlightbackground=COLORS["entry_border"],
        buttonbackground=COLORS["bg_deep"],
    )
    qty_spin.pack(side="left", padx=8)

    _label(qty_row, "passwords", font=FONT_UI,
           fg=COLORS["text_primary"], bg=COLORS["bg_card"]
           ).pack(side="left")

    # ── RIGHT COLUMN ─────────────────────────────────────────────────────
    right_col = tk.Frame(content, bg=COLORS["bg_deep"])
    right_col.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

    # — Generated Password Display ———————————————————————————————————
    output_card = _styled_frame(right_col)
    output_card.pack(fill="x", pady=(0, 10))

    _label(output_card, "GENERATED PASSWORD",
           font=("Courier New", 8, "bold"),
           fg=COLORS["text_muted"]
           ).pack(anchor="w", padx=14, pady=(12, 4))

    pw_entry = tk.Entry(
        output_card, textvariable=password_var,
        font=FONT_MONO_LG,
        fg=COLORS["accent_cyan"], bg=COLORS["entry_bg"],
        insertbackground=COLORS["accent_cyan"],
        relief="flat", bd=0,
        highlightthickness=1,
        highlightbackground=COLORS["entry_border"],
        readonlybackground=COLORS["entry_bg"],
        state="readonly",
    )
    pw_entry.pack(fill="x", padx=14, pady=(0, 8), ipady=8)

    # Copy button inline
    copy_row = tk.Frame(output_card, bg=COLORS["bg_card"])
    copy_row.pack(fill="x", padx=14, pady=(0, 12))

    copy_status_lbl = tk.Label(copy_row, text="",
                               font=FONT_UI_SM,
                               fg=COLORS["accent_green"],
                               bg=COLORS["bg_card"])
    copy_status_lbl.pack(side="right")

    def _copy_to_clipboard(pw=None):
        text = pw or password_var.get()
        if not text:
            return
        root.clipboard_clear()
        root.clipboard_append(text)
        copy_status_lbl.config(text="✔ Copied!")
        root.after(2000, lambda: copy_status_lbl.config(text=""))

    _cyber_button(copy_row, "⧉  Copy to Clipboard",
                  _copy_to_clipboard
                  ).pack(side="left")

    # — Strength Meter ——————————————————————————————————————————————
    strength_card = _styled_frame(right_col)
    strength_card.pack(fill="x", pady=(0, 10))

    _label(strength_card, "STRENGTH ANALYSIS",
           font=("Courier New", 8, "bold"),
           fg=COLORS["text_muted"]
           ).pack(anchor="w", padx=14, pady=(12, 6))

    # Strength label row
    str_label_row = tk.Frame(strength_card, bg=COLORS["bg_card"])
    str_label_row.pack(fill="x", padx=14, pady=(0, 4))

    strength_label = tk.Label(str_label_row, text="—",
                              font=("Segoe UI", 11, "bold"),
                              fg=COLORS["text_muted"],
                              bg=COLORS["bg_card"])
    strength_label.pack(side="left")

    entropy_label = tk.Label(str_label_row, text="",
                             font=FONT_MONO, fg=COLORS["text_muted"],
                             bg=COLORS["bg_card"])
    entropy_label.pack(side="right")

    # Segmented bar (5 blocks)
    bar_frame = tk.Frame(strength_card, bg=COLORS["bg_card"])
    bar_frame.pack(fill="x", padx=14, pady=(0, 12))

    strength_segments = []
    for _ in range(5):
        seg = tk.Frame(bar_frame, bg=COLORS["bg_deep"],
                       height=6, width=1,
                       highlightthickness=0)
        seg.pack(side="left", expand=True, fill="x", padx=2)
        strength_segments.append(seg)

    # Stat pills row
    stats_row = tk.Frame(strength_card, bg=COLORS["bg_card"])
    stats_row.pack(fill="x", padx=14, pady=(0, 12))

    def _stat_pill(parent, label, value_var):
        frame = tk.Frame(parent, bg=COLORS["bg_deep"],
                         highlightthickness=1,
                         highlightbackground=COLORS["border"])
        frame.pack(side="left", padx=(0, 6))
        tk.Label(frame, text=label, font=FONT_LABEL,
                 fg=COLORS["text_muted"], bg=COLORS["bg_deep"]
                 ).pack(padx=8, pady=(4, 0))
        lbl = tk.Label(frame, textvariable=value_var,
                       font=("Courier New", 11, "bold"),
                       fg=COLORS["accent_cyan"], bg=COLORS["bg_deep"])
        lbl.pack(padx=8, pady=(0, 4))
        return lbl

    stat_length = tk.StringVar(value="—")
    stat_sets   = tk.StringVar(value="—")
    stat_entropy = tk.StringVar(value="—")

    _stat_pill(stats_row, "Length",   stat_length)
    _stat_pill(stats_row, "Char Sets", stat_sets)
    _stat_pill(stats_row, "Entropy",  stat_entropy)

    # — Batch Output Area ——————————————————————————————————————————
    batch_out_card = _styled_frame(right_col)
    batch_out_card.pack(fill="both", expand=True, pady=(0, 10))

    _label(batch_out_card, "BATCH OUTPUT",
           font=("Courier New", 8, "bold"),
           fg=COLORS["text_muted"]
           ).pack(anchor="w", padx=14, pady=(12, 4))

    batch_text = tk.Text(
        batch_out_card,
        font=("Courier New", 9),
        fg=COLORS["text_primary"],
        bg=COLORS["entry_bg"],
        insertbackground=COLORS["accent_cyan"],
        relief="flat", bd=0,
        highlightthickness=1,
        highlightbackground=COLORS["entry_border"],
        state="disabled",
        wrap="none",
        selectbackground=COLORS["btn_hover"],
        selectforeground=COLORS["accent_cyan"],
    )
    batch_text.pack(fill="both", expand=True, padx=14, pady=(0, 8))

    # Scrollbar for batch output
    batch_scroll = tk.Scrollbar(batch_out_card, orient="vertical",
                                command=batch_text.yview,
                                bg=COLORS["bg_deep"],
                                troughcolor=COLORS["bg_deep"],
                                activebackground=COLORS["accent_cyan"])
    batch_text.config(yscrollcommand=batch_scroll.set)

    batch_copy_row = tk.Frame(batch_out_card, bg=COLORS["bg_card"])
    batch_copy_row.pack(fill="x", padx=14, pady=(0, 12))

    batch_copy_status = tk.Label(batch_copy_row, text="",
                                 font=FONT_UI_SM,
                                 fg=COLORS["accent_green"],
                                 bg=COLORS["bg_card"])
    batch_copy_status.pack(side="right")

    def _copy_batch():
        text = batch_text.get("1.0", "end").strip()
        if not text:
            return
        root.clipboard_clear()
        root.clipboard_append(text)
        batch_copy_status.config(text="✔ All copied!")
        root.after(2000, lambda: batch_copy_status.config(text=""))

    _cyber_button(batch_copy_row, "⧉  Copy All",
                  _copy_batch).pack(side="left")

    # ── Action Buttons (bottom of left col) ───────────────────────────────
    action_frame = tk.Frame(left_col, bg=COLORS["bg_deep"])
    action_frame.pack(fill="x", pady=(4, 0))

    # ── Core update / generate logic ─────────────────────────────────────

    def _validate_options() -> bool:
        if not any([use_upper_var.get(), use_lower_var.get(),
                    use_digits_var.get(), use_symbols_var.get()]):
            messagebox.showwarning(
                "CyberShield",
                "Select at least one character set.",
                parent=root
            )
            return False
        return True

    def _compute_entropy(length: int, pool_size: int) -> float:
        import math
        return round(length * math.log2(pool_size), 1) if pool_size > 0 else 0.0

    def _pool_size() -> int:
        pool = ""
        if use_upper_var.get():   pool += CHAR_SETS["uppercase"]
        if use_lower_var.get():   pool += CHAR_SETS["lowercase"]
        if use_digits_var.get():  pool += CHAR_SETS["digits"]
        if use_symbols_var.get(): pool += CHAR_SETS["symbols"]
        if excl_ambiguous_var.get():
            pool = "".join(c for c in pool if c not in CHAR_SETS["ambiguous"])
        return len(set(pool))

    def _refresh_strength(pw: str):
        """Update all strength meter widgets for a given password."""
        score, label_text, color = score_password(pw)
        strength_label.config(text=label_text, fg=color)

        # Fill segments
        filled = score + 1 if pw else 0
        for i, seg in enumerate(strength_segments):
            seg.config(bg=color if i < filled else COLORS["bg_deep"])

        # Update stat pills
        length = len(pw)
        sets_used = sum([
            any(c.isupper()  for c in pw),
            any(c.islower()  for c in pw),
            any(c.isdigit()  for c in pw),
            any(c in CHAR_SETS["symbols"] for c in pw),
        ]) if pw else 0

        pool = _pool_size()
        entropy = _compute_entropy(length, pool)

        stat_length.set(str(length))
        stat_sets.set(f"{sets_used}/4")
        stat_entropy.set(f"{entropy} b")
        entropy_label.config(
            text=f"Pool: {pool} chars",
            fg=COLORS["text_muted"]
        )

    def _generate():
        if not _validate_options():
            return

        qty = quantity_var.get()
        passwords = [
            generate_password(
                length=length_var.get(),
                use_upper=use_upper_var.get(),
                use_lower=use_lower_var.get(),
                use_digits=use_digits_var.get(),
                use_symbols=use_symbols_var.get(),
                exclude_ambiguous=excl_ambiguous_var.get(),
            )
            for _ in range(qty)
        ]

        # Update primary display with the first password
        first = passwords[0]
        password_var.set(first)
        _refresh_strength(first)

        # Update batch output area
        batch_text.config(state="normal")
        batch_text.delete("1.0", "end")
        for i, pw in enumerate(passwords, 1):
            prefix = f"{i:02d}. " if qty > 1 else ""
            batch_text.insert("end", f"{prefix}{pw}\n")
        batch_text.config(state="disabled")

        status_lbl.config(
            text=f"● {qty} password{'s' if qty > 1 else ''} generated",
            fg=COLORS["accent_green"]
        )
        root.after(3000, lambda: status_lbl.config(text="● READY",
                                                   fg=COLORS["accent_green"]))

    def _flash_btn(btn):
        """Brief colour flash on preset buttons to confirm tap."""
        original_fg = btn.cget("fg")
        btn.config(fg=COLORS["accent_cyan"])
        root.after(300, lambda: btn.config(fg=original_fg))

    # ── Generate button (primary CTA) ─────────────────────────────────────
    gen_btn = _cyber_button(action_frame, "⚡  GENERATE PASSWORD",
                            _generate, accent=True)
    gen_btn.pack(fill="x", pady=(0, 6), ipady=4)

    # Clear button
    def _clear():
        password_var.set("")
        batch_text.config(state="normal")
        batch_text.delete("1.0", "end")
        batch_text.config(state="disabled")
        _refresh_strength("")
        status_lbl.config(text="● READY", fg=COLORS["accent_green"])

    _cyber_button(action_frame, "✕  Clear", _clear
                  ).pack(fill="x", ipady=2)

    # ── Keyboard shortcut: Enter = Generate ──────────────────────────────
    root.bind_all("<Return>", lambda e: _generate())

    # ── Initial generation on load ────────────────────────────────────────
    _generate()
