import tkinter as tk
from modules.password_analyzer import launch

root = tk.Tk()
root.title("CyberShield Toolkit")
root.geometry("800x600")

frame = tk.Frame(root)
frame.pack(fill="both", expand=True)

launch(frame)

root.mainloop()

