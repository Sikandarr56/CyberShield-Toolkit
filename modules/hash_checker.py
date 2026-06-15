import tkinter as tk
from tkinter import filedialog, messagebox
import hashlib


def launch(parent_frame):
    for widget in parent_frame.winfo_children():
        widget.destroy()

    parent_frame.configure(bg="#0d1117")
    selected_file = tk.StringVar()
    generated_hash = tk.StringVar()

    def calculate_hash(algorithm):
        filepath = selected_file.get()
        if not filepath:
            messagebox.showwarning("Warning", "Please select a file.")
            return
        try:
            hasher = hashlib.sha256() if algorithm == "sha256" else hashlib.md5()
            with open(filepath, "rb") as file:
                while chunk := file.read(4096):
                    hasher.update(chunk)
            generated_hash.set(hasher.hexdigest())
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def browse_file():
        filepath = filedialog.askopenfilename()
        if filepath:
            selected_file.set(filepath)

    def verify_hash():
        expected = expected_entry.get().strip().lower()
        actual = generated_hash.get().strip().lower()
        if not actual:
            messagebox.showwarning(
                "Warning",
                "Generate a hash first."
            )
            return
        if expected == actual:
            result_label.config(
                text="Integrity Verified ✓",
                fg="#00ff88"
            )
        else:
            result_label.config(
                text="Hash Mismatch ✗",
                fg="#ff4d4d"
            )

    title = tk.Label(
        parent_frame,
        text="File Hash & Integrity Checker",
        bg="#0d1117",
        fg="#00ff88",
        font=("Consolas", 18, "bold")
    )
    title.pack(pady=15)

    file_frame = tk.Frame(parent_frame, bg="#0d1117")
    file_frame.pack(pady=10)

    tk.Entry(
        file_frame,
        textvariable=selected_file,
        width=60
    ).pack(side="left", padx=5)

    tk.Button(
        file_frame,
        text="Browse",
        command=browse_file
    ).pack(side="left")

    btn_frame = tk.Frame(parent_frame, bg="#0d1117")
    btn_frame.pack(pady=10)

    tk.Button(
        btn_frame,
        text="Generate SHA-256",
        command=lambda: calculate_hash("sha256")
    ).pack(side="left", padx=5)

    tk.Button(
        btn_frame,
        text="Generate MD5",
        command=lambda: calculate_hash("md5")
    ).pack(side="left", padx=5)

    tk.Label(
        parent_frame,
        text="Generated Hash",
        bg="#0d1117",
        fg="white"
    ).pack()

    tk.Entry(
        parent_frame,
        textvariable=generated_hash,
        width=90
    ).pack(pady=5)

    tk.Label(
        parent_frame,
        text="Expected Hash",
        bg="#0d1117",
        fg="white"
    ).pack()

    expected_entry = tk.Entry(
        parent_frame,
        width=90
    )
    expected_entry.pack(pady=5)

    tk.Button(
        parent_frame,
        text="Verify Integrity",
        command=verify_hash
    ).pack(pady=10)

    result_label = tk.Label(
        parent_frame,
        text="",
        bg="#0d1117",
        font=("Consolas", 12, "bold")
    )
    result_label.pack(pady=10)
