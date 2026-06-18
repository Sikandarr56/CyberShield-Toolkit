import tkinter as tk
from modules.password_analyzer import launch as password_analyzer
from modules.password_generator import launch as password_generator
from modules.hash_checker import launch as hash_checker
from modules.phishing_detector import launch as phishing_detector

# ─────────────────────────────────────────────
# THEME (clean + high contrast cyber UI)
# ─────────────────────────────────────────────
BG_ROOT      = "#060A12"
BG_SIDEBAR   = "#0B1120"
BG_CONTENT   = "#0A0E1A"

BG_BTN       = "#0F1829"
BG_BTN_HOVER = "#162035"
BG_BTN_ACTIVE = "#FFD60A"

TEXT_NORMAL  = "#FFFFFF"
TEXT_ACTIVE  = "#000000"
TEXT_MUTED   = "#7A8AA6"

ACCENT_GREEN = "#00FF88"

# ─────────────────────────────────────────────
# WINDOW
# ─────────────────────────────────────────────
root = tk.Tk()
root.title("CyberShield Toolkit")
root.geometry("1280x760")
root.minsize(1000, 600)
root.configure(bg=BG_ROOT)

# ─────────────────────────────────────────────
# LAYOUT
# ─────────────────────────────────────────────
sidebar = tk.Frame(root, bg=BG_SIDEBAR, width=240)
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

tk.Frame(root, bg="#00D4FF", width=2).pack(side="left", fill="y")

content_frame = tk.Frame(root, bg=BG_CONTENT)
content_frame.pack(side="right", fill="both", expand=True)

# ─────────────────────────────────────────────
# LOGO
# ─────────────────────────────────────────────
tk.Label(
    sidebar,
    text="CyberShield\nToolkit",
    font=("Consolas", 17, "bold"),
    bg=BG_SIDEBAR,
    fg="#00FF88",
    justify="left"
).pack(anchor="w", padx=20, pady=(25, 5))

tk.Label(
    sidebar,
    text="OSSD Project",
    font=("Consolas", 8),
    bg=BG_SIDEBAR,
    fg=TEXT_MUTED
).pack(anchor="w", padx=20)

tk.Frame(sidebar, bg="#1A2D4A", height=1).pack(fill="x", padx=15, pady=15)

tk.Label(
    sidebar,
    text="MODULES",
    font=("Consolas", 8, "bold"),
    bg=BG_SIDEBAR,
    fg=TEXT_MUTED
).pack(anchor="w", padx=20, pady=(0, 10))

# ─────────────────────────────────────────────
# MODULES
# ─────────────────────────────────────────────
MODULES = [
    ("Password Analyzer", password_analyzer),
    ("Password Generator", password_generator),
    ("Hash Checker", hash_checker),
    ("Phishing Detector", phishing_detector),
]

_active_btn = None
_active_indicator = None


# ─────────────────────────────────────────────
# MODULE LOADER
# ─────────────────────────────────────────────
def load_module(fn, btn, indicator):
    global _active_btn, _active_indicator

    # reset previous
    if _active_btn:
        _active_btn.configure(bg=BG_BTN, fg=TEXT_NORMAL)
    if _active_indicator:
        _active_indicator.configure(bg=BG_SIDEBAR)

    # activate current
    btn.configure(bg=BG_BTN_ACTIVE, fg=TEXT_ACTIVE)
    indicator.configure(bg="#FFD60A")

    _active_btn = btn
    _active_indicator = indicator

    # load module
    for w in content_frame.winfo_children():
        w.destroy()

    fn(content_frame)


# ─────────────────────────────────────────────
# SIDEBAR BUTTONS
# ─────────────────────────────────────────────
for name, fn in MODULES:

    row = tk.Frame(sidebar, bg=BG_SIDEBAR)
    row.pack(fill="x", pady=4)

    indicator = tk.Frame(row, bg=BG_SIDEBAR, width=4, height=42)
    indicator.pack(side="left", fill="y")

    btn = tk.Button(
        row,
        text=name,
        font=("Segoe UI", 11, "bold"),
        fg=TEXT_NORMAL,
        bg=BG_BTN,
        relief="flat",
        bd=0,
        anchor="w",
        padx=12,
        pady=10,
        cursor="hand2"
    )
    btn.pack(side="left", fill="x", expand=True)

    def on_click(f=fn, b=btn, i=indicator):
        return lambda: load_module(f, b, i)

    btn.configure(command=on_click())

    def on_enter(e, b=btn):
        if b != _active_btn:
            b.configure(bg=BG_BTN_HOVER, fg="#FFD60A")

    def on_leave(e, b=btn):
        if b != _active_btn:
            b.configure(bg=BG_BTN, fg=TEXT_NORMAL)

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)


# ─────────────────────────────────────────────
# DEFAULT LOAD
# ─────────────────────────────────────────────
first_btn = sidebar.winfo_children()[4].winfo_children()[1]
first_indicator = sidebar.winfo_children()[4].winfo_children()[0]

load_module(MODULES[0][1], first_btn, first_indicator)

# ─────────────────────────────────────────────
# RUN
# ─────────────────────────────────────────────
root.mainloop()