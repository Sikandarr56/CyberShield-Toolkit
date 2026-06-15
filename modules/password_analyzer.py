import tkinter as tk
from typing import Optional
import math
import re

BG        = "#080B10"
BG_CARD   = "#0D1825"
BG_INPUT  = "#0A1520"
BG_ROW    = "#112235"
BORDER    = "#1E3448"
TEXT_HI   = "#FFFFFF"
TEXT_MID  = "#B0BEC5"
TEXT_LO   = "#546E7A"
GREEN     = "#00FF41"
BLUE      = "#58A6FF"
AMBER     = "#FFA726"
RED       = "#FF5252"
TEAL      = "#26C6DA"

COMMON = {
    "123456","12345678","password","password123",
    "admin","qwerty","welcome","letmein","abc123"
}

def _entropy(pw):
    if not pw:
        return 0.0
    pool = 0
    if re.search(r"[a-z]", pw): pool += 26
    if re.search(r"[A-Z]", pw): pool += 26
    if re.search(r"[0-9]", pw): pool += 10
    if re.search(r"[^a-zA-Z0-9]", pw): pool += 32
    return len(pw) * math.log2(max(pool, 1))

def _analyze(pw):
    has_up = bool(re.search(r"[A-Z]", pw))
    has_lo = bool(re.search(r"[a-z]", pw))
    has_di = bool(re.search(r"[0-9]", pw))
    has_sp = bool(re.search(r"[^a-zA-Z0-9]", pw))
    n      = len(pw)
    ent    = _entropy(pw)
    hit    = pw.lower() in COMMON or pw in COMMON

    s = 0
    if n >= 8:   s += 10
    if n >= 12:  s += 15
    if n >= 16:  s += 10
    if has_up:   s += 15
    if has_lo:   s += 10
    if has_di:   s += 15
    if has_sp:   s += 20
    if ent >= 28: s += 2
    if ent >= 40: s += 3
    if ent >= 60: s += 5
    s = min(s, 100)
    if hit: s = min(s, 12)

    if   s < 30: tier, col = "WEAK",      RED
    elif s < 55: tier, col = "MEDIUM",    AMBER
    elif s < 80: tier, col = "STRONG",    TEAL
    else:        tier, col = "EXCELLENT", GREEN

    recs = []
    if hit:        recs.append(("crit", "Known breached password — change immediately"))
    if n < 8:      recs.append(("warn", "Use at least 8 characters"))
    if n < 12:     recs.append(("warn", "12+ characters significantly raises security"))
    if not has_up: recs.append(("warn", "Add uppercase letters  A-Z"))
    if not has_lo: recs.append(("warn", "Add lowercase letters  a-z"))
    if not has_di: recs.append(("warn", "Include at least one digit  0-9"))
    if not has_sp: recs.append(("warn", "Add special characters  !@#$%..."))
    if ent < 40:   recs.append(("warn", "Raise entropy above 40 bits"))
    if not recs:   recs.append(("ok",   "All criteria met — this password is solid"))

    return {
        "score": s, "tier": tier, "color": col,
        "entropy": ent, "breached": hit, "length": n,
        "criteria": {
            "len8":  n >= 8,  "len12": n >= 12,
            "upper": has_up,  "lower": has_lo,
            "digit": has_di,  "spec":  has_sp,
        },
        "recs": recs,
    }


class _Bar:
    def __init__(self, parent):
        self.cv  = tk.Canvas(parent, height=14, bg=BG_CARD,
                             highlightthickness=0, bd=0)
        self.cv.pack(fill="x", padx=0, pady=(6, 18))
        self._v  = 0.0
        self._t  = 0.0
        self._c  = GREEN
        self._job = None
        self.cv.bind("<Configure>", lambda e: self._draw())

    def _draw(self):
        w = self.cv.winfo_width()
        if w < 4: return
        self.cv.delete("all")
        self.cv.create_rectangle(0, 0, w, 14, fill=BG_ROW, outline="")
        px = int(w * self._v / 100)
        if px > 2:
            self.cv.create_rectangle(0, 0, px, 14, fill=self._c, outline="")
            self.cv.create_rectangle(0, 0, px, 4,
                                     fill="#FFFFFF", outline="", stipple="gray25")

    def go(self, target, color):
        self._t = max(0.0, min(100.0, target))
        self._c = color
        if self._job:
            try: self.cv.after_cancel(self._job)
            except: pass
        self._tick()

    def _tick(self):
        d = self._t - self._v
        if abs(d) < 0.4:
            self._v = self._t
            self._draw()
            return
        self._v += d * 0.15
        self._draw()
        self._job = self.cv.after(14, self._tick)


def launch(parent_frame):
    parent_frame.configure(bg=BG)

    cv   = tk.Canvas(parent_frame, bg=BG, highlightthickness=0)
    vsb  = tk.Scrollbar(parent_frame, orient="vertical", command=cv.yview,
                        bg=BG, troughcolor=BG, bd=0)
    cv.configure(yscrollcommand=vsb.set)
    vsb.pack(side="right", fill="y")
    cv.pack(side="left", fill="both", expand=True)

    root   = tk.Frame(cv, bg=BG)
    wid    = cv.create_window((0, 0), window=root, anchor="nw")

    root.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
    cv.bind("<Configure>",   lambda e: cv.itemconfig(wid, width=e.width))
    cv.bind_all("<MouseWheel>",
                lambda e: cv.yview_scroll(int(-1*(e.delta/120)), "units"))

    def card(title):
        outer = tk.Frame(root, bg=BG_CARD)
        outer.pack(fill="x", padx=18, pady=(0, 12))
        tk.Frame(outer, bg=GREEN, height=2).pack(fill="x")
        body = tk.Frame(outer, bg=BG_CARD, padx=22, pady=18)
        body.pack(fill="both", expand=True)
        tk.Label(body, text=title.upper(),
                 font=("Helvetica", 12, "bold"),
                 fg=TEXT_MID, bg=BG_CARD, anchor="w").pack(fill="x")
        tk.Frame(body, bg=BORDER, height=1).pack(fill="x", pady=(8, 14))
        return body

    tk.Frame(root, bg=BG, height=18).pack()

    hdr = tk.Frame(root, bg=BG)
    hdr.pack(fill="x", padx=18, pady=(0, 2))
    tk.Label(hdr, text="PASSWORD",
             font=("Helvetica", 28, "bold"),
             fg=GREEN, bg=BG).pack(side="left")
    tk.Label(hdr, text="  ANALYZER",
             font=("Helvetica", 28, "bold"),
             fg=TEXT_HI, bg=BG).pack(side="left")
    tk.Label(hdr, text="CyberShield Toolkit",
             font=("Helvetica", 12, "bold"),
             fg=TEXT_LO, bg=BG).pack(side="right", pady=(12, 0))
    tk.Frame(root, bg=GREEN, height=2).pack(fill="x", padx=18, pady=(8, 16))

    inp = card("Target Password")

    wrap = tk.Frame(inp, bg=BG_INPUT,
                    highlightthickness=2,
                    highlightbackground=BORDER,
                    highlightcolor=GREEN)
    wrap.pack(fill="x")

    pw_var   = tk.StringVar()
    show_var = tk.BooleanVar(value=False)

    ent = tk.Entry(wrap, textvariable=pw_var, show="*",
                   font=("Helvetica", 16, "bold"),
                   bg=BG_INPUT, fg=GREEN,
                   insertbackground=GREEN,
                   relief="flat", bd=0, highlightthickness=0)
    ent.pack(side="left", fill="x", expand=True, ipady=14, ipadx=14)
    ent.focus_set()

    def toggle():
        if show_var.get():
            ent.config(show="*")
            show_var.set(False)
            vbtn.config(text="SHOW", fg=BLUE)
        else:
            ent.config(show="")
            show_var.set(True)
            vbtn.config(text="HIDE", fg=AMBER)

    vbtn = tk.Label(wrap, text="SHOW",
                    font=("Helvetica", 12, "bold"),
                    fg=BLUE, bg=BG_INPUT, cursor="hand2", padx=14)
    vbtn.pack(side="right")
    vbtn.bind("<Button-1>", lambda e: toggle())

    cbtn = tk.Label(wrap, text="CLR",
                    font=("Helvetica", 12, "bold"),
                    fg=TEXT_LO, bg=BG_INPUT, cursor="hand2", padx=10)
    cbtn.pack(side="right")
    cbtn.bind("<Button-1>", lambda e: (pw_var.set(""), ent.focus_set()))

    scr = card("Security Score")

    top = tk.Frame(scr, bg=BG_CARD)
    top.pack(fill="x")

    num = tk.Label(top, text="--",
                   font=("Helvetica", 60, "bold"),
                   fg=TEXT_LO, bg=BG_CARD, width=3, anchor="e")
    num.pack(side="left")

    tk.Label(top, text=" /100",
             font=("Helvetica", 20, "bold"),
             fg=TEXT_LO, bg=BG_CARD).pack(side="left", pady=(26, 0))

    rc = tk.Frame(top, bg=BG_CARD)
    rc.pack(side="left", fill="both", expand=True, padx=(22, 0), pady=8)

    tier_lbl = tk.Label(rc, text="AWAITING INPUT",
                        font=("Helvetica", 22, "bold"),
                        fg=TEXT_LO, bg=BG_CARD, anchor="w")
    tier_lbl.pack(fill="x")

    ent_lbl = tk.Label(rc, text="Entropy  —  -- bits",
                       font=("Helvetica", 14),
                       fg=TEXT_MID, bg=BG_CARD, anchor="w")
    ent_lbl.pack(fill="x", pady=(10, 2))

    len_lbl = tk.Label(rc, text="Length   —  -- characters",
                       font=("Helvetica", 14),
                       fg=TEXT_MID, bg=BG_CARD, anchor="w")
    len_lbl.pack(fill="x")

    tk.Frame(scr, bg=BG_CARD, height=6).pack()
    bar = _Bar(scr)

    crt = card("Criteria Matrix")
    cg  = tk.Frame(crt, bg=BG_CARD)
    cg.pack(fill="x")
    cg.columnconfigure(0, weight=1)
    cg.columnconfigure(1, weight=1)

    CRITS = [
        ("len8",  "Length >= 8"),
        ("len12", "Length >= 12"),
        ("upper", "Uppercase  A-Z"),
        ("lower", "Lowercase  a-z"),
        ("digit", "Digits  0-9"),
        ("spec",  "Specials  !@#..."),
    ]

    icons = {}
    for i, (k, lbl) in enumerate(CRITS):
        r, c = divmod(i, 2)
        cell = tk.Frame(cg, bg=BG_ROW, padx=16, pady=14)
        cell.grid(row=r, column=c, padx=5, pady=5, sticky="ew")
        dot = tk.Label(cell, text="[ ]",
                       font=("Helvetica", 13, "bold"),
                       fg=TEXT_LO, bg=BG_ROW, width=5, anchor="w")
        dot.pack(side="left")
        tk.Label(cell, text=lbl,
                 font=("Helvetica", 14, "bold"),
                 fg=TEXT_MID, bg=BG_ROW).pack(side="left", padx=8)
        icons[k] = dot

    brc = card("Breach Intel")
    br  = tk.Frame(brc, bg=BG_CARD)
    br.pack(fill="x")

    bdot = tk.Label(br, text="[ ? ]",
                    font=("Helvetica", 15, "bold"),
                    fg=TEXT_LO, bg=BG_CARD, width=6, anchor="w")
    bdot.pack(side="left", padx=(0, 14))

    blbl = tk.Label(br, text="Enter a password to run breach check",
                    font=("Helvetica", 14),
                    fg=TEXT_MID, bg=BG_CARD, anchor="w")
    blbl.pack(side="left", fill="x", expand=True)

    rec = card("Recommendations")
    rf  = tk.Frame(rec, bg=BG_CARD)
    rf.pack(fill="x")

    rows = []
    for _ in range(8):
        rw   = tk.Frame(rf, bg=BG_ROW, padx=16, pady=12)
        bull = tk.Label(rw, text="",
                        font=("Helvetica", 13, "bold"),
                        bg=BG_ROW, width=6, anchor="w")
        bull.pack(side="left")
        msg  = tk.Label(rw, text="",
                        font=("Helvetica", 14),
                        bg=BG_ROW, fg=TEXT_MID, anchor="w")
        msg.pack(side="left", fill="x", expand=True)
        rows.append((rw, bull, msg))
        rw.pack_forget()

    tk.Frame(root, bg=BORDER, height=1).pack(fill="x", padx=18, pady=(4, 0))
    tk.Label(root, text="Analysis runs locally  —  no data leaves your machine",
             font=("Helvetica", 12), fg=TEXT_LO, bg=BG).pack(pady=12)

    def refresh(*_):
        pw = pw_var.get()

        if not pw:
            num.config(text="--", fg=TEXT_LO)
            tier_lbl.config(text="AWAITING INPUT", fg=TEXT_LO)
            ent_lbl.config(text="Entropy  —  -- bits", fg=TEXT_MID)
            len_lbl.config(text="Length   —  -- characters", fg=TEXT_MID)
            bar.go(0, GREEN)
            for dot in icons.values():
                dot.config(text="[ ]", fg=TEXT_LO)
            bdot.config(text="[ ? ]", fg=TEXT_LO)
            blbl.config(text="Enter a password to run breach check", fg=TEXT_MID)
            for rw, _, __ in rows:
                rw.pack_forget()
            return

        d = _analyze(pw)

        num.config(text=str(d["score"]), fg=d["color"])
        tier_lbl.config(text=d["tier"], fg=d["color"])
        ent_lbl.config(text=f"Entropy  —  {d['entropy']:.1f} bits", fg=TEXT_MID)
        len_lbl.config(text=f"Length   —  {d['length']} characters", fg=TEXT_MID)
        bar.go(d["score"], d["color"])

        for k, dot in icons.items():
            ok = d["criteria"][k]
            dot.config(text="[OK]" if ok else "[ ]",
                       fg=GREEN if ok else TEXT_LO)

        if d["breached"]:
            bdot.config(text="[!!]", fg=RED)
            blbl.config(text="BREACH DETECTED — found in known password list", fg=RED)
        else:
            bdot.config(text="[OK]", fg=GREEN)
            blbl.config(text="Clean — not found in known breach list", fg=GREEN)

        COLS = {"crit": RED, "warn": AMBER, "ok": GREEN}
        BULL = {"crit": "[!!]", "warn": "[ > ]", "ok": "[OK]"}

        for i, (rw, bull, msg) in enumerate(rows):
            if i < len(d["recs"]):
                kind, text = d["recs"][i]
                bull.config(text=BULL[kind], fg=COLS[kind])
                msg.config(text=text,
                           fg=TEXT_HI if kind == "crit" else TEXT_MID)
                rw.pack(fill="x", pady=4)
            else:
                rw.pack_forget()

    ent.bind("<KeyRelease>", refresh)
    pw_var.trace_add("write", refresh)
    refresh()


if __name__ == "__main__":
    r = tk.Tk()
    r.title("CyberShield Toolkit")
    r.geometry("820x700")
    r.configure(bg="#080B10")
    r.minsize(600, 500)
    f = tk.Frame(r, bg="#080B10")
    f.pack(fill="both", expand=True)
    launch(f)
    r.mainloop()
