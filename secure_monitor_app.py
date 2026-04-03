# ==========================================
# FINAL UI...
# ==========================================

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import random
import math

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# -----------------------------
# PARTICLE BACKGROUND
# -----------------------------
class ParticleCanvas(tk.Canvas):
    def __init__(self, parent):
        super().__init__(parent, bg="#020617", highlightthickness=0)
        self.pack(fill="both", expand=True)
        self.particles = [self.create_particle() for _ in range(40)]
        self.animate()

    def create_particle(self):
        x = random.randint(0, 1200)
        y = random.randint(0, 700)
        size = random.randint(2, 4)
        speed = random.uniform(0.3, 1.2)
        return {"x": x, "y": y, "size": size, "speed": speed}

    def animate(self):
        self.delete("all")
        for p in self.particles:
            p["y"] += p["speed"]
            if p["y"] > 700:
                p["y"] = 0
            self.create_oval(
                p["x"], p["y"],
                p["x"] + p["size"], p["y"] + p["size"],
                fill="#22d3ee", outline=""
            )
        self.after(30, self.animate)

# -----------------------------
# MAIN APP
# -----------------------------
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("⚡ LEGEND SECURITY SYSTEM")
        self.geometry("1300x750")

        self.canvas = ParticleCanvas(self)

        self.container = ctk.CTkFrame(self.canvas, fg_color="transparent")
        self.canvas.create_window(0, 0, anchor="nw", window=self.container, relwidth=1, relheight=1)

        self.show_login()

    def clear(self):
        for w in self.container.winfo_children():
            w.destroy()

    def show_login(self):
        self.clear()
        LoginUI(self.container, self)

    def show_dashboard(self):
        self.clear()
        DashboardUI(self.container, self)

# -----------------------------
# LOGIN UI
# -----------------------------
class LoginUI(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="#0f172a", corner_radius=30)
        self.app = app
        self.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self, text="⚡ LEGEND ACCESS",
                     font=("Segoe UI", 30, "bold"),
                     text_color="#22d3ee").pack(pady=20)

        self.user = ctk.CTkEntry(self, placeholder_text="USERNAME", width=280)
        self.user.pack(pady=10)

        self.pwd = ctk.CTkEntry(self, placeholder_text="PASSWORD", show="*", width=280)
        self.pwd.pack(pady=10)

        ctk.CTkButton(self, text="ENTER SYSTEM",
                      fg_color="#06b6d4",
                      command=self.login).pack(pady=15)

    def login(self):
        if self.user.get() == "admin":
            self.app.show_dashboard()
        else:
            messagebox.showerror("DENIED", "ACCESS FAILED")

# -----------------------------
# DASHBOARD
# -----------------------------
class DashboardUI(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True)

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)

        self.cpu = self.card(content, "CPU")
        self.cpu.pack(pady=10)

        self.mem = self.card(content, "MEMORY")
        self.mem.pack(pady=10)

        self.term = self.card(content, "TERMINAL")
        self.term.pack(pady=10)

        self.cpu_bar = ctk.CTkProgressBar(self.cpu)
        self.cpu_bar.pack(pady=10)

        self.mem_bar = ctk.CTkProgressBar(self.mem)
        self.mem_bar.pack(pady=10)

        self.terminal = ctk.CTkTextbox(self.term, height=120)
        self.terminal.pack(fill="both", padx=10, pady=10)

        self.animate()
        self.logs()

    def card(self, parent, title):
        card = ctk.CTkFrame(parent, corner_radius=20, fg_color="#0f172a")
        ctk.CTkLabel(card, text=title,
                     font=("Segoe UI", 16, "bold"),
                     text_color="#22d3ee").pack(pady=10)
        return card

    def animate(self):
        cpu = random.randint(10, 90)
        mem = random.randint(20, 80)

        self.cpu_bar.set(cpu / 100)
        self.mem_bar.set(mem / 100)

        self.after(700, self.animate)

    def logs(self):
        msgs = ["Scanning...", "Encrypting...", "Monitoring...", "System OK"]
        self.terminal.insert("end", f"> {random.choice(msgs)}\n")
        self.terminal.see("end")
        self.after(1000, self.logs)

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    app = App()
    app.mainloop()
