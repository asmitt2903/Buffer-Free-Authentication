# ==============================
# MODERN UI
# ==============================

import customtkinter as ctk
from tkinter import messagebox, simpledialog
import psutil, time, threading, datetime

# -----------------------------
# THEME
# -----------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# -----------------------------
# DUMMY AUTH (Replace with yours)
# -----------------------------
class AuthManager:
    def login(self, u, p, otp=None):
        if u == "admin" and p == "admin":
            return True, "Success"
        return False, "Invalid"

# -----------------------------
# MAIN APP
# -----------------------------
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Secure Monitor 🚀")
        self.geometry("1100x650")

        self.auth = AuthManager()

        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)

        self.show_login()

    def clear(self):
        for w in self.container.winfo_children():
            w.destroy()

    def show_login(self):
        self.clear()
        LoginFrame(self.container, self)

    def show_dashboard(self, user):
        self.clear()
        Dashboard(self.container, self, user)

# -----------------------------
# LOGIN UI
# -----------------------------
class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.pack(expand=True)

        card = ctk.CTkFrame(self, corner_radius=20)
        card.pack(pady=100, padx=100)

        ctk.CTkLabel(card, text="🔐 Secure Login", font=("Segoe UI", 26, "bold")).pack(pady=20)

        self.user = ctk.CTkEntry(card, placeholder_text="Username")
        self.user.pack(pady=10, padx=40)

        self.pwd = ctk.CTkEntry(card, placeholder_text="Password", show="*")
        self.pwd.pack(pady=10, padx=40)

        ctk.CTkButton(card, text="Login", command=self.login).pack(pady=10)
        ctk.CTkButton(card, text="Register", fg_color="gray").pack(pady=5)

    def login(self):
        u = self.user.get()
        p = self.pwd.get()

        status, msg = self.app.auth.login(u, p)

        if status:
            self.app.show_dashboard(u)
        else:
            messagebox.showerror("Error", msg)

# -----------------------------
# DASHBOARD UI
# -----------------------------
class Dashboard(ctk.CTkFrame):
    def __init__(self, parent, app, user):
        super().__init__(parent)
        self.app = app
        self.user = user
        self.pack(fill="both", expand=True)

        # Sidebar
        sidebar = ctk.CTkFrame(self, width=200)
        sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(sidebar, text="⚡ SYSTEM", font=("Segoe UI", 18, "bold")).pack(pady=20)
        ctk.CTkLabel(sidebar, text=f"User: {user}").pack(pady=10)

        ctk.CTkButton(sidebar, text="🔑 Rotate Keys").pack(pady=5)
        ctk.CTkButton(sidebar, text="🚪 Logout", fg_color="red",
                      command=self.app.show_login).pack(side="bottom", pady=20)

        # Content
        content = ctk.CTkFrame(self)
        content.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        # Cards
        self.cpu_card = self.card(content, "CPU Usage")
        self.cpu_card.grid(row=0, column=0, padx=10, pady=10)

        self.mem_card = self.card(content, "Memory")
        self.mem_card.grid(row=0, column=1, padx=10, pady=10)

        self.net_card = self.card(content, "Network")
        self.net_card.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        # Widgets
        self.cpu_bar = ctk.CTkProgressBar(self.cpu_card)
        self.cpu_bar.pack(pady=10)

        self.mem_bar = ctk.CTkProgressBar(self.mem_card)
        self.mem_bar.pack(pady=10)

        self.net_label = ctk.CTkLabel(self.net_card, text="Speed: 0 KB/s")
        self.net_label.pack(pady=10)

        threading.Thread(target=self.update_stats, daemon=True).start()

    def card(self, parent, title):
        card = ctk.CTkFrame(parent, corner_radius=15)
        ctk.CTkLabel(card, text=title, font=("Segoe UI", 16, "bold")).pack(pady=10)
        return card

    def update_stats(self):
        while True:
            cpu = psutil.cpu_percent()
            mem = psutil.virtual_memory().percent

            self.cpu_bar.set(cpu / 100)
            self.mem_bar.set(mem / 100)

            self.net_label.configure(text=f"CPU {cpu}% | RAM {mem}%")

            time.sleep(1)

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    app = App()
    app.mainloop()
