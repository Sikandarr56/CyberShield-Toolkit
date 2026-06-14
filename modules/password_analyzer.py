import tkinter as tk
from typing import Optional
import math
import re

BG         = "#0A0E14"
BG_PANEL   = "#0D1117"
BG_CARD    = "#111820"
BG_INPUT   = "#0D1117"
BG_ROW     = "#141C26"
BORDER     = "#1E2D3D"
BORDER_LIT = "#00FF41"
TEXT_HI    = "#E8F0FE"
TEXT_MID   = "#8892A4"
TEXT_LO    = "#3D4B5C"
GREEN      = "#00FF41"
GREEN_DIM  = "#00662A"
BLUE       = "#3B82F6"
AMBER      = "#F59E0B"
RED        = "#EF4444"
TEAL       = "#06B6D4"

COMMON_PASSWORDS = {
    "123456","12345678","password","password123",
    "admin","qwerty","welcome","letmein","abc123"
}

def _entropy(pw: str) -> float:
    if not pw:
        return 0.0
    pool = 0
    if re.search(r"[a-z]", pw): pool += 26
    if re.search(r"[A-Z]", pw): pool += 26
    if re.search(r"[0-9]", pw): pool += 10
    if re.search(r"[^a-zA-Z0-9]", pw): pool += 32
    return len(pw) * math.log2(max(pool, 1))

def _analyze(pw: str) -> dict:
    has_up  = bool(re.search(r"[A-Z]", pw))
    has_lo  = bool(re.search(r"[a-z]", pw))
    has_di  = bool(re.search(r"[0-9]", pw))
    has_sp  = bool(re.search(r"[^a-zA-Z0-9]", pw))
    length  = len(pw)
    ent     = _entropy(pw)
    breached = pw.lower() in COMMON_PASSWORDS or pw in COMMON_PASSWORDS

    score = 0
    if length >= 8:  score += 10
    if length >= 12: score += 15
    if length >= 16: score += 10
    if has_up:       score += 15
    if has_lo:       score += 10
    if has_di:       score += 15
    if has_sp:       score += 20
    if ent >= 28:    score += 2
    if ent >= 40:    score += 3
    if ent >= 60:    score += 5
    score = min(score, 100)
    if breached:     score = min(score, 12)

    if   score < 30: tier, color = "WEAK",      RED
    elif score < 55: tier, color = "MEDIUM",     AMBER
    elif score < 80: tier, color = "STRONG",     TEAL
    else:            tier, color = "EXCELLENT",  GREEN

    recs = []
    if breached:    recs.append(("critical", "Known breached password — change it immediately"))
    if length < 8:  recs.append(("warn",     "Use at least 8 characters"))
    if length < 12: recs.append(("warn",     "12+ characters significantly raises security"))
    if not has_up:  recs.append(("warn",     "Add uppercase letters  A–Z"))
    if not has_lo:  recs.append(("warn",     "Add lowercase letters  a–z"))
    if not has_di:  recs.append(("warn",     "Include at least one digit  0–9"))
    if not has_sp:  recs.append(("warn",     "Add special characters  !@#$%…"))
    if ent < 40:    recs.append(("warn",     "Raise entropy above 40 bits for better resilience"))
    if not recs:    recs.append(("ok",       "All criteria met — this password is solid"))

    return {
        "score": score, "tier": tier, "color": color,
        "entropy": ent, "breached": breached,
        "criteria": {
            "len8":  length >= 8,
            "len12": length >= 12,
            "upper": has_up,
            "lower": has_lo,
            "digit": has_di,
            "spec":  has_sp,
        },
        "recs": recs,
        "length": length,
        "has_up": has_up, "has_lo": has_lo,
        "has_di": has_di, "has_sp": has_sp,
    }


class _GlowBar:
    H = 8

    def __init__(self, parent: tk.Widget):
        self.cv = tk.Canvas(parent, height=self.H, bg=BG_CARD,
                            highlightthickness=0, bd=0)
        self.cv.pack(fill="x", padx=20, pady=(0, 18))
        self._val   = 0.0
        self._tgt   = 0.0
        self._color = GREEN
        self._job   = None
        self.cv.bind("<Configure>", lambda e: self._draw())

    def _draw(self):
        w = self.cv.winfo_width()
        if w < 4:
            return
        self.cv.delete("all")
        self.cv.create_rectangle(0, 0, w, self.H, fill=BG_ROW, outline="")
        px = int(w * self._val / 100)
        if px > 2:
            self.cv.create_rectangle(0, 0, px, self.H,
                                     fill=self._color, outline="")
            self.cv.create_rectangle(0, 0, px, 2,
                                     fill="#FFFFFF", outline="",
                                     stipple="gray12")

    def animate(self, target: float, color: str):
        self._tgt   = max(0.0, min(100.0, target))
        self._color = color
        if self._job:
            try: self.cv.after_cancel(self._job)
            except Exception: pass
        self._tick()

    def _tick(self):
        diff = self._tgt - self._val
        if abs(diff) < 0.4:
            self._val = self._tgt
            self._draw()
            return
        self._val += diff * 0.15
        self._draw()
        self._job = self.cv.after(14, self._tick)


def launch(parent_frame: tk.Frame):
    parent_frame.configure(bg=BG)

    outer = tk.Canvas(parent_frame, bg=BG, highlightthickness=0)
    vsb   = tk.Scrollbar(parent_frame, orient="vertical",
                         command=outer.yview, bg=BG,
                         troughcolor=BG_PANEL, bd=0)
    outer.configure(yscrollcommand=vsb.set)
    vsb.pack(side="right", fill="y")
    outer.pack(side="left", fill="both", expand=True)

    root = tk.Frame(outer, bg=BG)
    win_id = outer.create_window((0, 0), window=root, anchor="nw")

    root.bind("<Configure>",
              lambda e: outer.configure(scrollregion=outer.bbox("all")))
    outer.bind("<Configure>",
               lambda e: outer.itemconfig(win_id, width=e.width))
    outer.bind_all("<MouseWheel>",
                   lambda e: outer.yview_scroll(int(-1*(e.delta/120)), "units"))

    def _section(label: str) -> tk.Frame:
        wrap = tk.Frame(root, bg=BG_CARD, bd=0)
        wrap.pack(fill="x", padx=18, pady=6)
        tk.Frame(wrap, bg=BORDER, height=1).pack(fill="x")
        inner = tk.Frame(wrap, bg=BG_CARD, padx=18, pady=14)
        inner.pack(fill="both", expand=True)
        tk.Label(inner, text=label.upper(),
                 font=("Courier New", 8, "bold"),
                 fg=TEXT_LO, bg=BG_CARD, anchor="w").pack(fill="x")
        tk.Frame(inner, bg=BORDER, height=1).pack(fill="x", pady=(6, 10))
        return inner

    tk.Frame(root, bg=BG, height=10).pack()

    hdr = tk.Frame(root, bg=BG)
    hdr.pack(fill="x", padx=18, pady=(4, 2))
    tk.Label(hdr, text="PASSWORD", font=("Courier New", 22, "bold"),
             fg=GREEN, bg=BG).pack(side="left")
    tk.Label(hdr, text="  ANALYZER", font=("Courier New", 22, "bold"),
             fg=TEXT_HI, bg=BG).pack(side="left")
    tk.Label(hdr, text="CyberShield Toolkit",
             font=("Courier New", 9), fg=TEXT_LO, bg=BG).pack(side="right", pady=(8,0))
    tk.Frame(root, bg=GREEN, height=1).pack(fill="x", padx=18, pady=(4, 8))

    inp_sec = _section("target password")

    entry_wrap = tk.Frame(inp_sec, bg=BG_INPUT, bd=0,
                          highlightthickness=1,
                          highlightbackground=BORDER,
                          highlightcolor=GREEN)
    entry_wrap.pack(fill="x")

    pw_var  = tk.StringVar()
    show_var = tk.BooleanVar(value=False)

    entry = tk.Entry(entry_wrap, textvariable=pw_var, show="●",
                     font=("Courier New", 14),
                     bg=BG_INPUT, fg=GREEN,
                     insertbackground=GREEN,
                     relief="flat", bd=0,
                     highlightthickness=0)
    entry.pack(side="left", fill="x", expand=True, ipady=11, ipadx=10)
    entry.focus_set()

    def _toggle_vis():
        if show_var.get():
            entry.config(show="●")
            show_var.set(False)
            vis_btn.config(text="SHOW", fg=BLUE)
        else:
            entry.config(show="")
            show_var.set(True)
            vis_btn.config(text="HIDE", fg=AMBER)

    vis_btn = tk.Label(entry_wrap, text="SHOW",
                       font=("Courier New", 9, "bold"),
                       fg=BLUE, bg=BG_INPUT,
                       cursor="hand2", padx=12)
    vis_btn.pack(side="right")
    vis_btn.bind("<Button-1>", lambda e: _toggle_vis())

    clr_btn = tk.Label(entry_wrap, text="CLR",
                       font=("Courier New", 9, "bold"),
                       fg=TEXT_MID, bg=BG_INPUT,
                       cursor="hand2", padx=8)
    clr_btn.pack(side="right")
    clr_btn.bind("<Button-1>", lambda e: (pw_var.set(""), entry.focus_set()))

    score_sec = _section("security score")

    top_row = tk.Frame(score_sec, bg=BG_CARD)
    top_row.pack(fill="x")

    score_num = tk.Label(top_row, text="--",
                         font=("Courier New", 48, "bold"),
                         fg=TEXT_LO, bg=BG_CARD, width=3, anchor="e")
    score_num.pack(side="left")

    tk.Label(top_row, text="/100",
             font=("Courier New", 16),
             fg=TEXT_LO, bg=BG_CARD).pack(side="left", pady=(18, 0), padx=(2, 18))

    right_col = tk.Frame(top_row, bg=BG_CARD)
    right_col.pack(side="left", fill="both", expand=True)

    tier_lbl = tk.Label(right_col, text="AWAITING INPUT",
                        font=("Courier New", 16, "bold"),
                        fg=TEXT_LO, bg=BG_CARD, anchor="w")
    tier_lbl.pack(fill="x")

    ent_lbl = tk.Label(right_col, text="entropy  ·  -- bits",
                       font=("Courier New", 10),
                       fg=TEXT_MID, bg=BG_CARD, anchor="w")
    ent_lbl.pack(fill="x", pady=(4, 0))

    len_lbl = tk.Label(right_col, text="length   ·  -- chars",
                       font=("Courier New", 10),
                       fg=TEXT_MID, bg=BG_CARD, anchor="w")
    len_lbl.pack(fill="x")

    tk.Frame(score_sec, bg=BG_CARD, height=10).pack()
    bar = _GlowBar(score_sec)

    crit_sec = _section("criteria matrix")

    crit_grid = tk.Frame(crit_sec, bg=BG_CARD)
    crit_grid.pack(fill="x")
    crit_grid.columnconfigure(0, weight=1)
    crit_grid.columnconfigure(1, weight=1)

    CRITERIA = [
        ("len8",  "Length ≥ 8"),
        ("len12", "Length ≥ 12"),
        ("upper", "Uppercase  A–Z"),
        ("lower", "Lowercase  a–z"),
        ("digit", "Digits  0–9"),
        ("spec",  "Specials  !@#…"),
    ]

    crit_icons = {}
    for i, (key, label) in enumerate(CRITERIA):
        r, c = divmod(i, 2)
        cell = tk.Frame(crit_grid, bg=BG_ROW, padx=12, pady=8)
        cell.grid(row=r, column=c, padx=3, pady=3, sticky="ew")
        dot = tk.Label(cell, text="◌", font=("Courier New", 13, "bold"),
                       fg=TEXT_LO, bg=BG_ROW, width=2)
        dot.pack(side="left")
        tk.Label(cell, text=label, font=("Courier New", 10),
                 fg=TEXT_MID, bg=BG_ROW).pack(side="left", padx=6)
        crit_icons[key] = dot

    breach_sec = _section("breach intel")

    breach_row = tk.Frame(breach_sec, bg=BG_CARD)
    breach_row.pack(fill="x")

    breach_dot = tk.Label(breach_row, text="◌",
                          font=("Courier New", 20, "bold"),
                          fg=TEXT_LO, bg=BG_CARD)
    breach_dot.pack(side="left", padx=(0, 12))

    breach_lbl = tk.Label(breach_row,
                          text="Enter a password to run breach check",
                          font=("Courier New", 11),
                          fg=TEXT_MID, bg=BG_CARD, anchor="w")
    breach_lbl.pack(side="left", fill="x", expand=True)

    rec_sec = _section("recommendations")

    rec_frame = tk.Frame(rec_sec, bg=BG_CARD)
    rec_frame.pack(fill="x")

    rec_labels = []
    for _ in range(8):
        row = tk.Frame(rec_frame, bg=BG_CARD)
        row.pack(fill="x", pady=2)
        bullet = tk.Label(row, text="", font=("Courier New", 10, "bold"),
                          bg=BG_CARD, width=2, anchor="w")
        bullet.pack(side="left")
        txt = tk.Label(row, text="", font=("Courier New", 10),
                       bg=BG_CARD, anchor="w")
        txt.pack(side="left", fill="x", expand=True)
        rec_labels.append((bullet, txt))
        row.pack_forget()

    tk.Frame(root, bg=BORDER, height=1).pack(fill="x", padx=18, pady=(8, 0))
    tk.Label(root, text="analysis runs locally  ·  no data leaves your machine",
             font=("Courier New", 8), fg=TEXT_LO, bg=BG).pack(pady=8)

    def _refresh(*_):
        pw = pw_var.get()

        if not pw:
            score_num.config(text="--", fg=TEXT_LO)
            tier_lbl.config(text="AWAITING INPUT", fg=TEXT_LO)
            ent_lbl.config(text="entropy  ·  -- bits", fg=TEXT_MID)
            len_lbl.config(text="length   ·  -- chars", fg=TEXT_MID)
            bar.animate(0, GREEN)
            for dot in crit_icons.values():
                dot.config(text="◌", fg=TEXT_LO)
            breach_dot.config(text="◌", fg=TEXT_LO)
            breach_lbl.config(text="Enter a password to run breach check", fg=TEXT_MID)
            for bullet, txt in rec_labels:
                bullet.master.pack_forget()
            return

        d = _analyze(pw)

        score_num.config(text=str(d["score"]), fg=d["color"])
        tier_lbl.config(text=d["tier"], fg=d["color"])
        ent_lbl.config(
            text=f"entropy  ·  {d['entropy']:.1f} bits",
            fg=TEXT_MID)
        len_lbl.config(
            text=f"length   ·  {d['length']} chars",
            fg=TEXT_MID)
        bar.animate(d["score"], d["color"])

        for key, dot in crit_icons.items():
            met = d["criteria"][key]
            dot.config(text="◆" if met else "◌",
                       fg=GREEN if met else TEXT_LO)

        if d["breached"]:
            breach_dot.config(text="!", fg=RED)
            breach_lbl.config(
                text="BREACH DETECTED — found in common password list",
                fg=RED)
        else:
            breach_dot.config(text="✓", fg=GREEN)
            breach_lbl.config(
                text="Clean — not found in known breach list",
                fg=GREEN)

        TYPE_COLOR = {"critical": RED, "warn": AMBER, "ok": GREEN}
        TYPE_BULLET = {"critical": "!", "warn": "›", "ok": "✓"}

        for i, (bullet, txt) in enumerate(rec_labels):
            if i < len(d["recs"]):
                kind, msg = d["recs"][i]
                c = TYPE_COLOR[kind]
                b = TYPE_BULLET[kind]
                bullet.config(text=b, fg=c)
                txt.config(text=msg, fg=TEXT_HI if kind == "critical" else TEXT_MID)
                bullet.master.pack(fill="x", pady=2)
            else:
                bullet.master.pack_forget()

    entry.bind("<KeyRelease>", _refresh)
    pw_var.trace_add("write", _refresh)
    _refresh()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("CyberShield — Password Analyzer")
    root.geometry("780x660")
    root.configure(bg="#0A0E14")
    root.minsize(560, 480)
    f = tk.Frame(root, bg="#0A0E14")
    f.pack(fill="both", expand=True)
    launch(f)
    root.mainloop()
