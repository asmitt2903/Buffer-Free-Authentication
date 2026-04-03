# ==============================
# MODIFIED UI
# ==============================

import customtkinter as ctk
from tkinter import messagebox
import random

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# -----------------------------
# MAIN APP
# -----------------------------
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Secure Monitor 🚀")
        self.geometry("1200x700")

        self.container = ctk.CTkFrame(self, fg_color="#0f172a")
        self.container.pack(fill="both", expand=True)

        self.show_login()

    def clear(self):
        for w in self.container.winfo_children():
            w.destroy()

    def show_login(self):
        self.clear()
        LoginUI(self.container, self)

    def show_dashboard(self, user="admin"):
        self.clear()
        DashboardUI(self.container, self, user)

# -----------------------------
# LOGIN UI (GLASS CARD)
# -----------------------------
class LoginUI(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="#0f172a")
        self.app = app
        self.pack(expand=True)

        card = ctk.CTkFrame(self, corner_radius=25, fg_color="#1e293b")
        card.pack(pady=120, padx=250)

        ctk.CTkLabel(
            card,
            text="🔐 Secure Access",
            font=("Segoe UI", 30, "bold"),
            text_color="#60a5fa"
        ).pack(pady=25)

        self.user = ctk.CTkEntry(card, placeholder_text="Username", width=300)
        self.user.pack(pady=10)

        self.pwd = ctk.CTkEntry(card, placeholder_text="Password", show="*", width=300)
        self.pwd.pack(pady=10)

        ctk.CTkButton(
            card,
            text="Login",
            width=250,
            corner_radius=15,
            fg_color="#3b82f6",
            hover_color="#2563eb",
            command=self.login
        ).pack(pady=15)

        ctk.CTkButton(
            card,
            text="Register",
            width=250,
            corner_radius=15,
            fg_color="#334155"
        ).pack(pady=5)

    def login(self):
        u = self.user.get()
        p = self.pwd.get()

        if u == "admin" and p == "admin":
            self.app.show_dashboard(u)
        else:
            messagebox.showerror("Error", "Invalid Credentials")

# -----------------------------
# DASHBOARD UI (GLASS STYLE)
# -----------------------------
class DashboardUI(ctk.CTkFrame):
    def __init__(self, parent, app, user):
        super().__init__(parent, fg_color="#0f172a")
        self.app = app
        self.pack(fill="both", expand=True)

        # Sidebar
        sidebar = ctk.CTkFrame(self, width=220, fg_color="#1e293b")
        sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(
            sidebar,
            text="⚡ SYSTEM",
            font=("Segoe UI", 22, "bold"),
            text_color="#60a5fa"
        ).pack(pady=20)

        ctk.CTkLabel(
            sidebar,
            text=f"User: {user}",
            text_color="#cbd5f5"
        ).pack(pady=10)

        self.btn(sidebar, "🔑 Rotate Keys").pack(pady=5)
        self.btn(sidebar, "📜 Logs").pack(pady=5)

        self.btn(
            sidebar,
            "🚪 Logout",
            "#ef4444",
            "#dc2626",
            self.app.show_login
        ).pack(side="bottom", pady=20)

        # Main Content
        content = ctk.CTkFrame(self, fg_color="#0f172a")
        content.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        content.grid_columnconfigure((0, 1), weight=1)

        # Cards
        self.cpu = self.card(content, "CPU Usage")
        self.cpu.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

        self.mem = self.card(content, "Memory")
        self.mem.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")

        self.net = self.card(content, "Network Activity")
        self.net.grid(row=1, column=0, columnspan=2, padx=15, pady=15, sticky="nsew")

        # Widgets
        self.cpu_bar = ctk.CTkProgressBar(self.cpu)
        self.cpu_bar.pack(pady=20, padx=30)

        self.mem_bar = ctk.CTkProgressBar(self.mem)
        self.mem_bar.pack(pady=20, padx=30)

        self.net_label = ctk.CTkLabel(self.net, text="Speed: 0 KB/s")
        self.net_label.pack(pady=25)

        self.animate()

    def btn(self, parent, text, fg="#3b82f6", hover="#2563eb", cmd=None):
        return ctk.CTkButton(
            parent,
            text=text,
            width=160,
            corner_radius=12,
            fg_color=fg,
            hover_color=hover,
            command=cmd
        )

    def card(self, parent, title):
        card = ctk.CTkFrame(parent, corner_radius=20, fg_color="#1e293b")
        ctk.CTkLabel(
            card,
            text=title,
            font=("Segoe UI", 18, "bold"),
            text_color="#93c5fd"
        ).pack(pady=15)
        return card

    def animate(self):
        cpu = random.randint(10, 90)
        mem = random.randint(20, 80)

        self.cpu_bar.set(cpu / 100)
        self.mem_bar.set(mem / 100)

        self.net_label.configure(text=f"CPU {cpu}% | RAM {mem}%")

        self.after(1000, self.animate)

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    app = App()
    app.mainloop()
