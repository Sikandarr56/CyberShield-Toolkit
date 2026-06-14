"""
CyberShield Toolkit - Phishing Email Detector Module
=====================================================
Collaborator Module: phishing_detector.py
Author: [Tumhara Naam]
Description: Dark-themed Tkinter module to detect phishing emails
             using keyword analysis and URL pattern matching.

Usage:
    from modules.phishing_detector import launch
    launch(parent_frame)
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import re


# ─────────────────────────────────────────────
#  PHISHING DETECTION ENGINE
# ─────────────────────────────────────────────

# Common phishing keywords found in suspicious emails
PHISHING_KEYWORDS = [
    "verify your account", "confirm your password", "click here immediately",
    "your account will be suspended", "update your payment", "urgent action required",
    "you have won", "claim your prize", "limited time offer", "act now",
    "dear customer", "dear user", "validate your information",
    "unusual activity", "suspicious login", "reset your password immediately",
    "enter your credentials", "bank account", "social security", "wire transfer",
    "nigerian prince", "lottery winner", "free money", "inheritance",
    "verify immediately", "account locked", "security alert"
]

# Suspicious URL patterns commonly used in phishing
SUSPICIOUS_URL_PATTERNS = [
    r"https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",   # IP address URLs
    r"https?://[^\s]*@[^\s]*",                            # URLs with @ symbol
    r"bit\.ly|tinyurl|goo\.gl|t\.co|ow\.ly",             # URL shorteners
    r"https?://[^\s]*(login|signin|verify|secure|update|confirm)[^\s]*",  # Fake login pages
    r"\.tk|\.ml|\.ga|\.cf|\.gq",                          # Free suspicious TLDs
]

# Suspicious sender patterns
SENDER_PATTERNS = [
    r"no.?reply@(?!.*\.(com|org|gov|edu))",
    r"support@.*\d{4,}",
    r"[a-z]{2,5}\d{6,}@",
    r"@.*-.*-.*\.",                                        # Many hyphens in domain
]


def analyze_email(sender: str, subject: str, body: str) -> dict:
    """
    Core phishing analysis function.
    Returns a dict with score, risk level, and list of detected threats.
    """
    threats = []
    score = 0

    combined_text = (sender + " " + subject + " " + body).lower()

    # Check for phishing keywords
    for keyword in PHISHING_KEYWORDS:
        if keyword.lower() in combined_text:
            threats.append(f"⚠ Suspicious keyword: '{keyword}'")
            score += 15

    # Check for suspicious URLs in body
    for pattern in SUSPICIOUS_URL_PATTERNS:
        matches = re.findall(pattern, body, re.IGNORECASE)
        for match in matches:
            threats.append(f"🔗 Suspicious URL pattern: '{match[:60]}'")
            score += 20

    # Check sender patterns
    for pattern in SENDER_PATTERNS:
        if re.search(pattern, sender, re.IGNORECASE):
            threats.append(f"📧 Suspicious sender format: '{sender}'")
            score += 25

    # Check for urgency indicators in subject
    urgency_words = ["urgent", "immediate", "asap", "action required", "final notice", "last chance"]
    for word in urgency_words:
        if word in subject.lower():
            threats.append(f"🚨 Urgency trigger in subject: '{word}'")
            score += 10

    # Check for ALL CAPS words (common in phishing)
    caps_words = re.findall(r'\b[A-Z]{4,}\b', subject + " " + body)
    if len(caps_words) > 3:
        threats.append(f"🔠 Excessive CAPS usage: {caps_words[:5]}")
        score += 10

    # Check for excessive exclamation marks
    exclamations = body.count("!") + subject.count("!")
    if exclamations > 3:
        threats.append(f"❗ Excessive exclamation marks: {exclamations} found")
        score += 5

    # Cap score at 100
    score = min(score, 100)

    # Determine risk level
    if score == 0:
        risk = "SAFE"
    elif score < 30:
        risk = "LOW RISK"
    elif score < 60:
        risk = "MEDIUM RISK"
    elif score < 85:
        risk = "HIGH RISK"
    else:
        risk = "PHISHING DETECTED"

    return {
        "score": score,
        "risk": risk,
        "threats": threats
    }


# ─────────────────────────────────────────────
#  COLOR THEME — Dark Cybersecurity
# ─────────────────────────────────────────────

THEME = {
    "bg_dark":      "#0A0E1A",   # Main background — deep navy black
    "bg_panel":     "#0F1526",   # Panel/card background
    "bg_input":     "#141C2E",   # Input field background
    "bg_header":    "#0D1220",   # Header bar background
    "accent_cyan":  "#00D4FF",   # Primary accent — cyber cyan
    "accent_green": "#00FF88",   # Safe/success green
    "accent_red":   "#FF3355",   # Danger/phishing red
    "accent_amber": "#FFB800",   # Warning amber
    "accent_purple":"#7B5EA7",   # Secondary accent
    "text_primary": "#E8EAF0",   # Main text
    "text_secondary":"#6B7A99",  # Muted text
    "border":       "#1E2A45",   # Border color
    "border_glow":  "#00D4FF33", # Cyan glow border
}

# Risk level colors
RISK_COLORS = {
    "SAFE":             THEME["accent_green"],
    "LOW RISK":         "#88FF44",
    "MEDIUM RISK":      THEME["accent_amber"],
    "HIGH RISK":        "#FF6B35",
    "PHISHING DETECTED":THEME["accent_red"],
}


# ─────────────────────────────────────────────
#  MAIN LAUNCH FUNCTION
# ─────────────────────────────────────────────

def launch(parent_frame: tk.Frame):
    """
    Public entry point for CyberShield Toolkit.
    Renders complete Phishing Email Detector UI inside parent_frame.

    Args:
        parent_frame (tk.Frame): The host frame provided by the main dashboard.
    """

    # Clear any existing widgets in parent frame
    for widget in parent_frame.winfo_children():
        widget.destroy()

    # Configure parent frame background
    parent_frame.configure(bg=THEME["bg_dark"])

    # ── MAIN CONTAINER ──────────────────────────────
    main_container = tk.Frame(parent_frame, bg=THEME["bg_dark"])
    main_container.pack(fill="both", expand=True, padx=16, pady=12)

    # ── HEADER ──────────────────────────────────────
    _build_header(main_container)

    # ── CONTENT AREA (Left Input | Right Results) ────
    content_frame = tk.Frame(main_container, bg=THEME["bg_dark"])
    content_frame.pack(fill="both", expand=True, pady=(12, 0))

    content_frame.columnconfigure(0, weight=3)
    content_frame.columnconfigure(1, weight=2)
    content_frame.rowconfigure(0, weight=1)

    # Left: Email Input Panel
    left_panel = _build_input_panel(content_frame)
    left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

    # Right: Results Panel
    right_panel, result_widgets = _build_results_panel(content_frame)
    right_panel.grid(row=0, column=1, sticky="nsew")

    # Wire input fields → result_widgets (cross-panel linking)
    result_widgets["sender_var"]  = left_panel._sender_var
    result_widgets["subject_var"] = left_panel._subject_var
    result_widgets["body_text"]   = left_panel._body_text

    # ── STATUS BAR ──────────────────────────────────
    status_var = tk.StringVar(value="Ready — Paste email content and click Analyze")
    _build_status_bar(main_container, status_var)

    # ── WIRE UP ANALYZE BUTTON ──────────────────────
    def on_analyze():
        sender  = result_widgets["sender_var"].get().strip()
        subject = result_widgets["subject_var"].get().strip()
        body    = result_widgets["body_text"].get("1.0", "end").strip()

        if not sender and not subject and not body:
            status_var.set("⚠  Please fill in at least one field before analyzing.")
            return

        status_var.set("🔍  Analyzing email...")
        parent_frame.update()

        result = analyze_email(sender, subject, body)
        _display_results(result_widgets, result)
        status_var.set(f"✓  Analysis complete — Risk: {result['risk']}  |  Score: {result['score']}/100")

    def on_clear():
        result_widgets["sender_var"].set("")
        result_widgets["subject_var"].set("")
        result_widgets["body_text"].delete("1.0", "end")
        _reset_results(result_widgets)
        status_var.set("Cleared — Ready for new analysis")

    # Bind buttons
    result_widgets["analyze_btn"].configure(command=on_analyze)
    result_widgets["clear_btn"].configure(command=on_clear)

    # Bind Ctrl+Enter shortcut
    parent_frame.bind_all("<Control-Return>", lambda e: on_analyze())


# ─────────────────────────────────────────────
#  UI BUILDER HELPERS
# ─────────────────────────────────────────────

def _build_header(parent):
    """Build the top header bar with title and description."""
    header = tk.Frame(parent, bg=THEME["bg_header"], pady=14)
    header.pack(fill="x")

    # Left: Icon + Title
    title_frame = tk.Frame(header, bg=THEME["bg_header"])
    title_frame.pack(side="left", padx=16)

    icon_lbl = tk.Label(
        title_frame, text="🛡",
        font=("Consolas", 22),
        bg=THEME["bg_header"], fg=THEME["accent_cyan"]
    )
    icon_lbl.pack(side="left", padx=(0, 10))

    text_frame = tk.Frame(title_frame, bg=THEME["bg_header"])
    text_frame.pack(side="left")

    tk.Label(
        text_frame,
        text="PHISHING EMAIL DETECTOR",
        font=("Consolas", 15, "bold"),
        bg=THEME["bg_header"], fg=THEME["accent_cyan"]
    ).pack(anchor="w")

    tk.Label(
        text_frame,
        text="CyberShield Toolkit  ·  Threat Analysis Module",
        font=("Consolas", 8),
        bg=THEME["bg_header"], fg=THEME["text_secondary"]
    ).pack(anchor="w")

    # Right: Live indicator
    indicator_frame = tk.Frame(header, bg=THEME["bg_header"])
    indicator_frame.pack(side="right", padx=16)

    tk.Label(
        indicator_frame, text="● ACTIVE",
        font=("Consolas", 9, "bold"),
        bg=THEME["bg_header"], fg=THEME["accent_green"]
    ).pack()

    # Separator line
    tk.Frame(parent, bg=THEME["accent_cyan"], height=1).pack(fill="x")


def _build_input_panel(parent):
    """Build the left panel with email input fields."""
    panel = tk.Frame(parent, bg=THEME["bg_panel"], bd=0)
    panel.configure(highlightbackground=THEME["border"], highlightthickness=1)

    # Panel header
    tk.Label(
        panel,
        text="  📨  EMAIL INPUT",
        font=("Consolas", 10, "bold"),
        bg=THEME["bg_panel"], fg=THEME["accent_cyan"],
        anchor="w", pady=10
    ).pack(fill="x", padx=12)

    tk.Frame(panel, bg=THEME["border"], height=1).pack(fill="x")

    # ── Sender Field ────────────────────────────────
    _field_label(panel, "SENDER ADDRESS")
    sender_var = tk.StringVar()
    sender_entry = _styled_entry(panel, sender_var, "e.g. support@bank-secure.tk")
    sender_entry.pack(fill="x", padx=12, pady=(0, 10))

    # ── Subject Field ───────────────────────────────
    _field_label(panel, "EMAIL SUBJECT")
    subject_var = tk.StringVar()
    subject_entry = _styled_entry(panel, subject_var, "e.g. URGENT: Verify your account NOW!")
    subject_entry.pack(fill="x", padx=12, pady=(0, 10))

    # ── Body Field ──────────────────────────────────
    _field_label(panel, "EMAIL BODY")

    body_frame = tk.Frame(panel, bg=THEME["border"], padx=1, pady=1)
    body_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    body_text = scrolledtext.ScrolledText(
        body_frame,
        height=12,
        font=("Consolas", 10),
        bg=THEME["bg_input"],
        fg=THEME["text_primary"],
        insertbackground=THEME["accent_cyan"],
        selectbackground=THEME["accent_purple"],
        relief="flat",
        wrap="word",
        padx=10, pady=8
    )
    body_text.pack(fill="both", expand=True)
    body_text.insert("1.0", "Paste email body content here...")
    body_text.bind("<FocusIn>", lambda e: _clear_placeholder(body_text, "Paste email body content here..."))

    # Store references on panel so we can retrieve them
    panel._sender_var = sender_var
    panel._subject_var = subject_var
    panel._body_text = body_text

    return panel


def _build_results_panel(content_frame):
    """Build the right panel for analysis results."""
    panel = tk.Frame(content_frame, bg=THEME["bg_panel"])
    panel.configure(highlightbackground=THEME["border"], highlightthickness=1)

    # Panel header
    tk.Label(
        panel,
        text="  🔍  ANALYSIS RESULTS",
        font=("Consolas", 10, "bold"),
        bg=THEME["bg_panel"], fg=THEME["accent_cyan"],
        anchor="w", pady=10
    ).pack(fill="x", padx=12)

    tk.Frame(panel, bg=THEME["border"], height=1).pack(fill="x")

    # ── Risk Meter ──────────────────────────────────
    meter_frame = tk.Frame(panel, bg=THEME["bg_panel"], pady=16)
    meter_frame.pack(fill="x", padx=16)

    tk.Label(
        meter_frame, text="THREAT LEVEL",
        font=("Consolas", 8), bg=THEME["bg_panel"],
        fg=THEME["text_secondary"]
    ).pack()

    risk_label = tk.Label(
        meter_frame, text="AWAITING SCAN",
        font=("Consolas", 16, "bold"),
        bg=THEME["bg_panel"], fg=THEME["text_secondary"]
    )
    risk_label.pack(pady=(4, 0))

    # Score bar background
    score_bg = tk.Frame(meter_frame, bg=THEME["border"], height=8)
    score_bg.pack(fill="x", pady=(8, 2))

    score_bar = tk.Frame(score_bg, bg=THEME["text_secondary"], height=8, width=0)
    score_bar.place(x=0, y=0, relheight=1.0, relwidth=0.0)

    score_label = tk.Label(
        meter_frame, text="Score: —",
        font=("Consolas", 9), bg=THEME["bg_panel"],
        fg=THEME["text_secondary"]
    )
    score_label.pack()

    tk.Frame(panel, bg=THEME["border"], height=1).pack(fill="x", padx=12)

    # ── Threats List ────────────────────────────────
    tk.Label(
        panel, text="DETECTED THREATS",
        font=("Consolas", 8), bg=THEME["bg_panel"],
        fg=THEME["text_secondary"], anchor="w"
    ).pack(fill="x", padx=16, pady=(10, 4))

    threats_frame = tk.Frame(panel, bg=THEME["bg_input"])
    threats_frame.configure(highlightbackground=THEME["border"], highlightthickness=1)
    threats_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    threats_text = scrolledtext.ScrolledText(
        threats_frame,
        font=("Consolas", 9),
        bg=THEME["bg_input"],
        fg=THEME["text_primary"],
        relief="flat",
        wrap="word",
        padx=8, pady=8,
        state="disabled"
    )
    threats_text.pack(fill="both", expand=True)

    tk.Frame(panel, bg=THEME["border"], height=1).pack(fill="x", padx=12)

    # ── Buttons ─────────────────────────────────────
    btn_frame = tk.Frame(panel, bg=THEME["bg_panel"], pady=12)
    btn_frame.pack(fill="x", padx=12)

    analyze_btn = tk.Button(
        btn_frame,
        text="⚡  ANALYZE EMAIL",
        font=("Consolas", 10, "bold"),
        bg=THEME["accent_cyan"], fg=THEME["bg_dark"],
        activebackground="#00AACC", activeforeground=THEME["bg_dark"],
        relief="flat", cursor="hand2", pady=8,
        bd=0
    )
    analyze_btn.pack(fill="x", pady=(0, 6))

    clear_btn = tk.Button(
        btn_frame,
        text="✕  CLEAR",
        font=("Consolas", 9),
        bg=THEME["bg_input"], fg=THEME["text_secondary"],
        activebackground=THEME["border"], activeforeground=THEME["text_primary"],
        relief="flat", cursor="hand2", pady=6,
        bd=0
    )
    clear_btn.pack(fill="x")

    # Retrieve sender/subject/body from left panel reference
    # These will be set after both panels are built
    sender_var = tk.StringVar()
    subject_var = tk.StringVar()

    # Collect all result widgets into a dict for easy access
    result_widgets = {
        "sender_var":   sender_var,
        "subject_var":  subject_var,
        "body_text":    None,           # Set after input panel is built
        "risk_label":   risk_label,
        "score_label":  score_label,
        "score_bar":    score_bar,
        "score_bg":     score_bg,
        "threats_text": threats_text,
        "analyze_btn":  analyze_btn,
        "clear_btn":    clear_btn,
    }

    return panel, result_widgets


def _build_status_bar(parent, status_var):
    """Build bottom status bar."""
    tk.Frame(parent, bg=THEME["border"], height=1).pack(fill="x", pady=(8, 0))

    status_bar = tk.Frame(parent, bg=THEME["bg_header"], pady=5)
    status_bar.pack(fill="x")

    tk.Label(
        status_bar,
        textvariable=status_var,
        font=("Consolas", 8),
        bg=THEME["bg_header"], fg=THEME["text_secondary"],
        anchor="w"
    ).pack(side="left", padx=12)

    tk.Label(
        status_bar,
        text="Ctrl+Enter to analyze",
        font=("Consolas", 8),
        bg=THEME["bg_header"], fg=THEME["text_secondary"]
    ).pack(side="right", padx=12)


# ─────────────────────────────────────────────
#  RESULT DISPLAY HELPERS
# ─────────────────────────────────────────────

def _display_results(widgets: dict, result: dict):
    """Update result widgets with analysis output."""
    risk    = result["risk"]
    score   = result["score"]
    threats = result["threats"]
    color   = RISK_COLORS.get(risk, THEME["text_primary"])

    # Update risk label
    widgets["risk_label"].configure(text=risk, fg=color)
    widgets["score_label"].configure(
        text=f"Score: {score}/100",
        fg=color
    )

    # Update score bar (proportional fill)
    widgets["score_bg"].update_idletasks()
    bar_width = widgets["score_bg"].winfo_width()
    fill_width = int(bar_width * score / 100)
    widgets["score_bar"].place(x=0, y=0, width=fill_width, relheight=1.0)
    widgets["score_bar"].configure(bg=color)

    # Update threats list
    widgets["threats_text"].configure(state="normal")
    widgets["threats_text"].delete("1.0", "end")

    if threats:
        for threat in threats:
            widgets["threats_text"].insert("end", threat + "\n\n")
    else:
        widgets["threats_text"].insert(
            "end",
            "✅  No threats detected.\n\nThis email appears to be safe based on pattern analysis.",
            "safe"
        )
        widgets["threats_text"].tag_configure("safe", foreground=THEME["accent_green"])

    widgets["threats_text"].configure(state="disabled")


def _reset_results(widgets: dict):
    """Reset results panel to default state."""
    widgets["risk_label"].configure(text="AWAITING SCAN", fg=THEME["text_secondary"])
    widgets["score_label"].configure(text="Score: —", fg=THEME["text_secondary"])
    widgets["score_bar"].place(x=0, y=0, width=0, relheight=1.0)
    widgets["score_bar"].configure(bg=THEME["text_secondary"])

    widgets["threats_text"].configure(state="normal")
    widgets["threats_text"].delete("1.0", "end")
    widgets["threats_text"].configure(state="disabled")


# ─────────────────────────────────────────────
#  WIDGET FACTORY HELPERS
# ─────────────────────────────────────────────

def _field_label(parent, text: str):
    """Render a small uppercase field label."""
    tk.Label(
        parent,
        text=text,
        font=("Consolas", 8),
        bg=THEME["bg_panel"], fg=THEME["text_secondary"],
        anchor="w"
    ).pack(fill="x", padx=12, pady=(10, 3))


def _styled_entry(parent, textvariable: tk.StringVar, placeholder: str = "") -> tk.Entry:
    """Return a styled Entry widget with dark theme."""
    entry = tk.Entry(
        parent,
        textvariable=textvariable,
        font=("Consolas", 10),
        bg=THEME["bg_input"],
        fg=THEME["text_primary"],
        insertbackground=THEME["accent_cyan"],
        selectbackground=THEME["accent_purple"],
        relief="flat",
        bd=0,
        highlightthickness=1,
        highlightbackground=THEME["border"],
        highlightcolor=THEME["accent_cyan"]
    )
    entry.configure({"disabledforeground": THEME["text_secondary"]})

    # Placeholder logic
    if placeholder:
        entry.insert(0, placeholder)
        entry.configure(fg=THEME["text_secondary"])
        entry.bind("<FocusIn>",  lambda e: _clear_placeholder(entry, placeholder))
        entry.bind("<FocusOut>", lambda e: _restore_placeholder(entry, placeholder))

    return entry


def _clear_placeholder(widget, placeholder: str):
    """Clear placeholder text on focus."""
    if isinstance(widget, scrolledtext.ScrolledText):
        if widget.get("1.0", "end").strip() == placeholder:
            widget.delete("1.0", "end")
            widget.configure(fg=THEME["text_primary"])
    else:
        if widget.get() == placeholder:
            widget.delete(0, "end")
            widget.configure(fg=THEME["text_primary"])


def _restore_placeholder(widget, placeholder: str):
    """Restore placeholder if field is empty."""
    if widget.get() == "":
        widget.insert(0, placeholder)
        widget.configure(fg=THEME["text_secondary"])


# ─────────────────────────────────────────────
#  WIRE INPUT ↔ RESULTS (post-build link)
# ─────────────────────────────────────────────
# NOTE: In launch(), after both panels are created,
# result_widgets["sender_var"] and ["subject_var"] are
# linked to the input panel's StringVars, and
# result_widgets["body_text"] is set to the body ScrolledText.
# This is handled inside the launch() function above.


# ─────────────────────────────────────────────
#  STANDALONE TEST (for development only)
# ─────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    root.title("CyberShield - Phishing Detector [DEV TEST]")
    root.geometry("1100x680")
    root.configure(bg="#0A0E1A")

    test_frame = tk.Frame(root, bg="#0A0E1A")
    test_frame.pack(fill="both", expand=True)

    launch(test_frame)
    root.mainloop()
