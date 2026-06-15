import tkinter as tk
from modules.password_analyzer import launch as password_analyzer
from modules.password_generator import launch as password_generator
from modules.hash_checker import launch as hash_checker
from modules.phishing_detector import launch as phishing_detector

# ─────────────────────────────────────────────
#  THEME
# ─────────────────────────────────────────────
BG_ROOT      = "#000000"
BG_SIDEBAR   = "#000000"
BG_CONTENT   = "#0A0E1A"
BG_BTN       = "#FFFFFF"
BG_BTN_ACT   = "#000000"  
ACCENT_CYAN  = "#00D4FF"
ACCENT_GREEN = "#00FF88"
BORDER_COL   = "#1A2D4A"
TEXT_BTN     = "#000000"   
TEXT_BTN_ACT = "#000000"   
TEXT_MUTED   = "#FFFFFF"
TEXT_LOGO    = "#FFFFFF"

# ─────────────────────────────────────────────
#  WINDOW
# ─────────────────────────────────────────────
root = tk.Tk()
root.title("CyberShield Toolkit")
root.geometry("1280x760")
root.minsize(1000, 600)
root.configure(bg=BG_ROOT)

# ─────────────────────────────────────────────
#  LAYOUT
# ─────────────────────────────────────────────
sidebar = tk.Frame(root, bg=BG_SIDEBAR, width=240)
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

tk.Frame(root, bg=ACCENT_CYAN, width=2).pack(side="left", fill="y")

content_frame = tk.Frame(root, bg=BG_CONTENT)
content_frame.pack(side="right", fill="both", expand=True)

# ─────────────────────────────────────────────
#  SIDEBAR — LOGO
# ─────────────────────────────────────────────
tk.Label(
    sidebar,
    text="CyberShield\nToolkit",
    font=("Consolas", 17, "bold"),
    bg=BG_SIDEBAR,
    fg=TEXT_LOGO,
    justify="left"
).pack(anchor="w", padx=22, pady=(30, 4))

tk.Label(
    sidebar,
    text="OSSD Semester Project",
    font=("Consolas", 8),
    bg=BG_SIDEBAR,
    fg=TEXT_MUTED,
    justify="left"
).pack(anchor="w", padx=22, pady=(0, 6))

tk.Frame(sidebar, bg=BORDER_COL, height=1).pack(fill="x", padx=18, pady=(10, 16))

tk.Label(
    sidebar,
    text="MODULES",
    font=("Consolas", 8, "bold"),
    bg=BG_SIDEBAR,
    fg=TEXT_MUTED,
    anchor="w"
).pack(fill="x", padx=22, pady=(0, 6))

# ─────────────────────────────────────────────
#  MODULE DEFINITIONS
# ─────────────────────────────────────────────
MODULES = [
    {"label": "Password Analyzer",  "fn": password_analyzer},
    {"label": "Password Generator", "fn": password_generator},
    {"label": "Hash Checker",       "fn": hash_checker},
    {"label": "Phishing Detector",  "fn": phishing_detector},
]

# ─────────────────────────────────────────────
#  MODULE LOADER
# ─────────────────────────────────────────────
_active_btn = None

def load_module(module_fn, btn):
    global _active_btn

    if _active_btn and _active_btn.winfo_exists():
        _active_btn.configure(bg=BG_BTN, fg=TEXT_BTN)

    btn.configure(bg=BG_BTN_ACT, fg=TEXT_BTN_ACT)
    _active_btn = btn

    for widget in content_frame.winfo_children():
        widget.destroy()
    module_fn(content_frame)

# ─────────────────────────────────────────────
#  SIDEBAR BUTTONS
# ─────────────────────────────────────────────
_btn_refs = []

for mod in MODULES:
    btn = tk.Button(
        sidebar,
        text=mod["label"],
        font=("Segoe UI", 11, "bold"),
        fg=TEXT_BTN,
        bg=BG_BTN,
        activebackground=BG_BTN_ACT,
        activeforeground=TEXT_BTN_ACT,
        relief="flat",
        bd=0,
        anchor="w",
        cursor="hand2",
        pady=11,
        padx=16,
        highlightthickness=0,
    )
    btn.pack(fill="x", padx=14, pady=3)

    def _make_cmd(fn=mod["fn"], b=btn):
        return lambda: load_module(fn, b)

    btn.configure(command=_make_cmd())

    def _on_enter(e, b=btn):
        if b is not _active_btn:
            b.configure(bg="#1A1A1A", fg="#FFD60A")

    def _on_leave(e, b=btn):
        if b is not _active_btn:
            b.configure(bg=BG_BTN, fg=TEXT_BTN)

    btn.bind("<Enter>", _on_enter)
    btn.bind("<Leave>", _on_leave)

    _btn_refs.append((btn, mod["fn"]))

# ─────────────────────────────────────────────
#  SIDEBAR — FOOTER
# ─────────────────────────────────────────────
tk.Frame(sidebar, bg=BORDER_COL, height=1).pack(fill="x", padx=18, pady=(20, 12))

tk.Label(
    sidebar,
    text="SYSTEM ONLINE",
    font=("Consolas", 8, "bold"),
    bg=BG_SIDEBAR,
    fg=ACCENT_GREEN,
    anchor="w"
).pack(side="bottom", anchor="w", padx=22, pady=(0, 18))

# ─────────────────────────────────────────────
#  KEYBOARD SHORTCUTS  Ctrl+1 to Ctrl+4
# ─────────────────────────────────────────────
for i, (btn, fn) in enumerate(_btn_refs):
    def _make_shortcut(b=btn, f=fn):
        return lambda e: load_module(f, b)
    root.bind(f"<Control-Key-{i + 1}>", _make_shortcut())

# ─────────────────────────────────────────────
#  BOOT — default module
# ─────────────────────────────────────────────
first_btn, first_fn = _btn_refs[0]
load_module(first_fn, first_btn)

# ─────────────────────────────────────────────
#  RUN
# ─────────────────────────────────────────────
root.mainloop()
