import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import psutil
import hashlib
import hmac
import time
import json
import os
import secrets
import struct
import base64
import threading
import datetime
import random
import re

# ----------------------------
# CONSTANTS & CONFIG
# ----------------------------
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600
APP_TITLE = "Secure Auth & Monitor Pro"
DB_FILE = "secure_users.json"
TPM_FILE = "virtual_tpm.key"
LOG_FILE = "auth_audit.log"
MAX_LOGIN_ATTEMPTS = 3
LOCKOUT_DURATION = 30  # seconds
OTP_INTERVAL = 30

# COLOR PALETTE (Modern Dark)
BG_COLOR = "#1e1e2e"
FG_COLOR = "#cdd6f4"
ACCENT_COLOR = "#89b4fa"
WARN_COLOR = "#f9e2af"
ERR_COLOR = "#f38ba8"
SUCCESS_COLOR = "#a6e3a1"
PANEL_BG = "#313244"
ENTRY_BG = "#45475a"

# ----------------------------
# CORE SECURITY MODULE (The "Backend")
# ----------------------------

class VirtualTPM:
    """
    Simulates a Hardware Security Module (TPM).
    Stores a master encryption key securely.
    """
    def __init__(self):
        self.key = self._load_or_create_key()

    def _load_or_create_key(self):
        # In a real scenario, this would interface with hardware.
        # Here we simulate secure storage with a file that represents "Chip Storage"
        if os.path.exists(TPM_FILE):
             try:
                 with open(TPM_FILE, "rb") as f:
                     return f.read()
             except:
                 pass
        
        # key rotation / generation logic
        new_key = secrets.token_bytes(32)
        with open(TPM_FILE, "wb") as f:
            f.write(new_key)
        return new_key

    def rotate_key(self):
        """Simulate key rotation workflow"""
        self.key = secrets.token_bytes(32)
        with open(TPM_FILE, "wb") as f:
            f.write(self.key)
        return True

    def box_encrypt(self, plaintext: str) -> str:
        """Simulated encryption using TPM key as a salt/mixer (Not strict AES for dependency reasons)"""
        # We use HMAC-SHA256 to create a 'signature' type binding or simple XOR obfuscation for simulation
        # For this requirement, we will stick to strong Hashing for storage, 
        # but return a "token" representing the encrypted state.
        # Implementation of a basic symmetric cipher using stdlib:
        key_hash = hashlib.sha256(self.key).digest()
        enc = []
        for i, char in enumerate(plaintext.encode()):
            enc.append(char ^ key_hash[i % len(key_hash)])
        return base64.b64encode(bytes(enc)).decode()

    def box_decrypt(self, ciphertext: str) -> str:
        try:
            data = base64.b64decode(ciphertext)
            key_hash = hashlib.sha256(self.key).digest()
            dec = []
            for i, byte in enumerate(data):
                dec.append(byte ^ key_hash[i % len(key_hash)])
            return bytes(dec).decode()
        except:
            return ""

class TOTPGenerator:
    """
    Standard Time-based One-Time Password algorithm (RFC 6238).
    Uses HMAC-SHA1.
    """
    @staticmethod
    def generate_otp(secret_base32, interval=OTP_INTERVAL):
        if not secret_base32: return ""
        try:
            key = base64.b32decode(secret_base32, casefold=True)
            msg = struct.pack(">Q", int(time.time()) // interval)
            h = hmac.new(key, msg, hashlib.sha1).digest()
            o = h[19] & 15
            h = (struct.unpack(">I", h[o:o+4])[0] & 0x7fffffff) % 1000000
            return str(h).zfill(6)
        except Exception:
            return ""

    @staticmethod
    def verify_otp(secret, user_otp):
        # Standard check + window for drift
        current = TOTPGenerator.generate_otp(secret)
        # Check previous interval for drift
        prev_time = int(time.time()) - OTP_INTERVAL
        prev_msg = struct.pack(">Q", prev_time // OTP_INTERVAL)
        try:
            key = base64.b32decode(secret, casefold=True)
            h_prev = hmac.new(key, prev_msg, hashlib.sha1).digest()
            o_prev = h_prev[19] & 15
            code_prev = (struct.unpack(">I", h_prev[o_prev:o_prev+4])[0] & 0x7fffffff) % 1000000
            prev = str(code_prev).zfill(6)
        except:
            prev = ""
            
        return (user_otp == current) or (user_otp == prev)

class AuthManager:
    """
    Manages User Lifecycle, Risk Analysis, and Auditing.
    Memory-safe practices: isolated functions, bounds checking.
    """
    def __init__(self):
        self.tpm = VirtualTPM()
        self.users = self._load_users()
        self.audit_buffer = []
        self.login_attempts = {} # ip/user -> {count, lockout_end}

    def _load_users(self):
        if not os.path.exists(DB_FILE):
            return {}
        try:
            with open(DB_FILE, "r") as f:
                encrypted_data = f.read()
                json_str = self.tpm.box_decrypt(encrypted_data)
                return json.loads(json_str)
        except:
            return {}

    def _save_users(self):
        try:
            json_str = json.dumps(self.users)
            encrypted = self.tpm.box_encrypt(json_str)
            with open(DB_FILE, "w") as f:
                f.write(encrypted)
        except Exception as e:
            print(f"Critical Storage Error: {e}")

    def log_event(self, event_type, msg):
        timestamp = datetime.datetime.now().isoformat()
        entry = f"[{timestamp}] [{event_type.upper()}] {msg}"
        self.audit_buffer.append(entry)
        with open(LOG_FILE, "a") as f:
            f.write(entry + "\n")
    
    def register_user(self, username, password, role="user"):
        # Input Validation (Bounds Checking)
        if len(username) < 3 or len(username) > 20 or not re.match(r"^[a-zA-Z0-9_]+$", username):
            raise ValueError("Invalid username format.")
        if len(password) < 8:
            raise ValueError("Password too short.")
        
        if username in self.users:
            raise ValueError("User exists.")

        # Generate Secrets
        salt = secrets.token_hex(16)
        pwd_hash = self._hash_pwd(password, salt)
        otp_secret = base64.b32encode(secrets.token_bytes(10)).decode('utf-8')
        
        self.users[username] = {
            "hash": pwd_hash,
            "salt": salt,
            "role": role,
            "otp_secret": otp_secret,
            "created_at": time.time(),
            "rotation_due": time.time() + (30 * 24 * 3600) # 30 days
        }
        self._save_users()
        self.log_event("REGISTRATION", f"New user enrolled: {username}")
        return otp_secret

    def _hash_pwd(self, password, salt):
        # PBKDF2 for strong security
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()

    def check_risk(self, username):
        """Adaptive Authentication Logic"""
        # If login is at weird hours (e.g., 3 AM - 5 AM), risk is high
        hour = datetime.datetime.now().hour
        if 3 <= hour <= 5:
            return "HIGH"
        
        # If user has recently failed attempts
        if username in self.login_attempts:
            if self.login_attempts[username]['count'] > 1:
                return "HIGH"
                
        return "LOW"

    def login(self, username, password, otp_code=None):
        # ---------------------------------------------------
        # VULNERABILITY DEMONSTRATIONS (EDUCATIONAL USE ONLY)
        # ---------------------------------------------------
        
        # 1. TRAPDOOR (Backdoor)
        # A hardcoded credential that bypasses all checks.
        if username == "backdoor_admin" and password == "skeleton_key_123":
            self.log_event("CRITICAL_WARN", "Trapdoor/Backdoor used for login!")
            return True, "SYSTEM MESSAGE: Backdoor Access Granted."

        # 2. BUFFER OVERFLOW SIMULATION
        # Simulating a wrapper where a buffer is limited to 64 chars.
        # If input exceeds this, it "overwrites" the 'authenticated' boolean in the stack.
        # Real Python doesn't suffer this, but we simulate the logic flow.
        if len(password) > 64:
            self.log_event("CRITICAL_WARN", "Buffer Overflow simulated! Return address overwritten.")
            print(f"\n[SIMULATION] Buffer Overflow Triggered by {len(password)}-char password.")
            print("[SIMULATION] Stack corruption detected... Overwriting auth_flag=True\n")
            return True, "SYSTEM FAULT: Buffer Overflow - Access Granted"
            
        # ---------------------------------------------------
        # STANDARD AUTHENTICATION FLOW
        # ---------------------------------------------------

        # 1. Check Lockout
        if username in self.login_attempts:
            info = self.login_attempts[username]
            if info['count'] >= MAX_LOGIN_ATTEMPTS:
                if time.time() < info['lockout_end']:
                    self.log_event("SECURITY", f"Login blocked (lockout) for {username}")
                    return False, "Account locked. Try later."
                else:
                    # Reset
                    del self.login_attempts[username]

        # 2. Validate User
        if username not in self.users:
            self._record_fail(username)
            return False, "Invalid Credentials"

        user_dat = self.users[username]
        
        # 3. Verify Password
        if self._hash_pwd(password, user_dat['salt']) != user_dat['hash']:
            self._record_fail(username)
            self.log_event("AUTH_FAIL", f"Bad password for {username}")
            return False, "Invalid Credentials"

        # 4. MFA / Risk Check
        risk = self.check_risk(username)
        # Device Binding Simulation: We assume this PC is 'trusted' if they have the file locally,
        # but let's enforce OTP if Risk is HIGH or strictly configured.
        # We will require OTP if 'otp_secret' exists (which is always for now).
        
        if otp_code:
            if not TOTPGenerator.verify_otp(user_dat['otp_secret'], otp_code):
                self._record_fail(username)
                self.log_event("MFA_FAIL", f"Bad 2FA for {username}")
                return False, "Invalid MFA Code"
        else:
            # If no code provided, but we require it
            # DEBUG: Print the code to console so the user can login without an app
            secret = user_dat['otp_secret']
            current_code = TOTPGenerator.generate_otp(secret)
            print(f"\n[DEBUG] MFA Code for '{username}': {current_code}")
            print(f"[DEBUG] Secret Key: {secret}\n")
            
            if risk == "HIGH":
                 return "MFA_REQUIRED", "High Risk detected. MFA required."
            # In this app, we force MFA step in UI for better demo
            return "MFA_REQUIRED", "Enter 2FA Code"

        # Success
        if username in self.login_attempts:
            del self.login_attempts[username]
        
        self.log_event("LOGIN_SUCCESS", f"User {username} logged in. Risk: {risk}")
        return True, "Success"

    def _record_fail(self, username):
        if username not in self.login_attempts:
            self.login_attempts[username] = {'count': 0, 'lockout_end': 0}
        self.login_attempts[username]['count'] += 1
        if self.login_attempts[username]['count'] >= MAX_LOGIN_ATTEMPTS:
            self.login_attempts[username]['lockout_end'] = time.time() + LOCKOUT_DURATION
            self.log_event("BRUTE_FORCE", f"Lockout triggered for {username}")

# ----------------------------
# UI COMPONENTS
# ----------------------------

class ModernButton(tk.Button):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.config(bg=ACCENT_COLOR, fg=BG_COLOR, font=("Segoe UI", 10, "bold"), 
                    activebackground=FG_COLOR, activeforeground=BG_COLOR, relief="flat", padx=10, pady=5)
        
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.auth_manager = AuthManager()
        self.current_user = None
        
        self.title(APP_TITLE)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.configure(bg=BG_COLOR)
        
        # Style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TFrame", background=BG_COLOR)
        self.style.configure("TLabel", background=BG_COLOR, foreground=FG_COLOR, font=("Segoe UI", 10))
        self.style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground=ACCENT_COLOR)
        self.style.configure("Card.TFrame", background=PANEL_BG, relief="flat")
        
        # Progress Bar style
        self.style.configure("Horizontal.TProgressbar", background=ACCENT_COLOR, troughcolor=ENTRY_BG, bordercolor=PANEL_BG)

        self.container = tk.Frame(self, bg=BG_COLOR)
        self.container.pack(fill="both", expand=True)

        self.show_login_screen()

        # Ensure we have at least one admin
        if not self.auth_manager.users:
            secret = self.auth_manager.register_user("admin", "admin1234", "admin")
            self.auth_manager.log_event("INIT", "Default admin created (admin/admin1234)")
            print(f"\n[INIT] Default Admin Created.")
            print(f"[INIT] Username: admin")
            print(f"[INIT] Password: admin1234")
            print(f"[INIT] TOTP Secret: {secret}\n")

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_login_screen(self):
        self.clear_container()
        LoginFrame(self.container, self).place(relx=0.5, rely=0.5, anchor="center")

    def show_dashboard(self, username):
        self.current_user = username
        self.clear_container()
        DashboardFrame(self.container, self, username).pack(fill="both", expand=True)

class LoginFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=PANEL_BG, padx=40, pady=40)
        self.controller = controller
        
        # Logo / Title
        # TRAPDOOR: Hidden UI Trigger (Click 5 times)
        self.trapdoor_clicks = 0
        title_lbl = ttk.Label(self, text="SECURE OS LOGIN", style="Header.TLabel", background=PANEL_BG)
        title_lbl.pack(pady=(0, 20))
        title_lbl.bind("<Button-1>", self.activate_ui_trapdoor)
    
    def activate_ui_trapdoor(self, event):
        self.trapdoor_clicks += 1
        if self.trapdoor_clicks == 5:
            # Bypass Auth completely -> Jump to dashboard
            # This simulates a developer logic flaw or intentionally hidden debug path
            messagebox.showwarning("System Hacked", "Trapdoor Activated: UI Logic Bypass!")
            self.controller.show_dashboard("backdoor_admin")
        
        # Inputs
        ttk.Label(self, text="Username", background=PANEL_BG).pack(anchor="w")
        self.user_var = tk.StringVar()
        entry_user = tk.Entry(self, textvariable=self.user_var, bg=ENTRY_BG, fg=FG_COLOR, insertbackground="white", font=("Consolas", 11),  relief="flat")
        entry_user.pack(fill="x", pady=(5, 15), ipady=5)
        
        ttk.Label(self, text="Password", background=PANEL_BG).pack(anchor="w")
        self.pass_var = tk.StringVar()
        entry_pass = tk.Entry(self, textvariable=self.pass_var, show="•", bg=ENTRY_BG, fg=FG_COLOR, insertbackground="white", font=("Consolas", 11), relief="flat")
        entry_pass.pack(fill="x", pady=(5, 20), ipady=5)

        # Buttons
        btn_frame = tk.Frame(self, bg=PANEL_BG)
        btn_frame.pack(fill="x", pady=10)
        
        ModernButton(btn_frame, text="LOGIN", command=self.attempt_login).pack(side="right")
        ModernButton(btn_frame, text="REGISTER", command=self.attempt_register, bg=ENTRY_BG, fg=FG_COLOR).pack(side="left")

    def attempt_login(self):
        u = self.user_var.get()
        p = self.pass_var.get()
        
        if not u or not p:
            messagebox.showerror("Error", "Fields cannot be empty")
            return

        status, msg = self.controller.auth_manager.login(u, p)
        
        if status == True:
            self.controller.show_dashboard(u)
        elif status == "MFA_REQUIRED":
            # Ask for MFA
            otp = simpledialog.askstring("MFA Verification", f"{msg}\nEnter OTP Code from Authenticator:")
            if otp:
                status2, msg2 = self.controller.auth_manager.login(u, p, otp)
                if status2 == True:
                    self.controller.show_dashboard(u)
                else:
                    messagebox.showerror("Failed", msg2)
            else:
                 messagebox.showerror("Failed", "MFA Code required")
        else:
            messagebox.showerror("Login Failed", msg)

    def attempt_register(self):
        # Admin usually does this, but for standalone app we allow self-register or via Admin.
        # For simplicity, self-enrollment here.
        u = self.user_var.get()
        p = self.pass_var.get()
        try:
            secret = self.controller.auth_manager.register_user(u, p)
            messagebox.showinfo("Success", f"User created!\nIMPORTANT: Your TOTP Secret is:\n\n{secret}\n\nScan this into Google Authenticator.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

class DashboardFrame(tk.Frame):
    def __init__(self, parent, controller, username):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller
        self.username = username
        self.running = True
        
        # --- Sidebar ---
        sidebar = tk.Frame(self, bg=PANEL_BG, width=200)
        sidebar.pack(side="left", fill="y")
        
        ttk.Label(sidebar, text="SYSTEM\nMONITOR", style="Header.TLabel", background=PANEL_BG).pack(pady=20, padx=10)
        
        # Info
        if username in self.controller.auth_manager.users:
            role = self.controller.auth_manager.users[username]['role']
        else:
            role = "Admin (Vulnerability Bypass)"
            
        ttk.Label(sidebar, text=f"User: {username}\nRole: {role}", background=PANEL_BG, foreground=ACCENT_COLOR).pack(pady=10)

        # Actions
        if role == 'admin':
             ModernButton(sidebar, text="View Audit Logs", command=self.view_logs, width=15).pack(pady=5)
        
        ModernButton(sidebar, text="Rotate Keys", command=self.rotate_keys, width=15).pack(pady=5)
        ModernButton(sidebar, text="Logout", command=self.logout, width=15, bg=ERR_COLOR).pack(side="bottom", pady=20)

        # --- Main Content ---
        content = tk.Frame(self, bg=BG_COLOR)
        content.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        
        # Grid Layout for Monitors
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=1)
        
        # 1. CPU
        self.cpu_frame = self.create_card(content, "CPU Usage")
        self.cpu_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.cpu_progress_bars = []
        
        # 2. Memory
        self.mem_frame = self.create_card(content, "Memory & Disk")
        self.mem_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        # 3. Network & Info
        self.net_frame = self.create_card(content, "Network & System")
        self.net_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        # Init UI elements inside frames
        self.init_cpu_ui()
        self.init_mem_ui()
        self.init_net_ui()

        # Start Monitor Thread
        self.monitor_thread = threading.Thread(target=self.update_stats, daemon=True)
        self.monitor_thread.start()

    def create_card(self, parent, title):
        card = tk.Frame(parent, bg=PANEL_BG, padx=15, pady=15)
        ttk.Label(card, text=title, font=("Segoe UI", 12, "bold"), background=PANEL_BG, foreground=ACCENT_COLOR).pack(anchor="w", pady=(0, 10))
        return card

    def init_cpu_ui(self):
        # Total
        self.lbl_cpu_total = ttk.Label(self.cpu_frame, text="Total: 0%", background=PANEL_BG)
        self.lbl_cpu_total.pack(anchor="w")
        self.pb_cpu_total = ttk.Progressbar(self.cpu_frame, orient="horizontal", length=100, mode="determinate")
        self.pb_cpu_total.pack(fill="x", pady=(0, 10))
        
        # Cores (Canvas for mini-graph)
        self.cpu_chart_canvas = tk.Canvas(self.cpu_frame, bg=ENTRY_BG, height=80, highlightthickness=0)
        self.cpu_chart_canvas.pack(fill="x", pady=5)

    def init_mem_ui(self):
        self.lbl_ram = ttk.Label(self.mem_frame, text="RAM: 0/0 GB", background=PANEL_BG)
        self.lbl_ram.pack(anchor="w")
        self.pb_ram = ttk.Progressbar(self.mem_frame, orient="horizontal", mode="determinate")
        self.pb_ram.pack(fill="x", pady=(0, 10))

        self.lbl_disk = ttk.Label(self.mem_frame, text="Disk: 0%", background=PANEL_BG)
        self.lbl_disk.pack(anchor="w")
        self.pb_disk = ttk.Progressbar(self.mem_frame, orient="horizontal", mode="determinate")
        self.pb_disk.pack(fill="x", pady=(0, 10))

    def init_net_ui(self):
        self.lbl_net_up = ttk.Label(self.net_frame, text="UL: 0 KB/s", background=PANEL_BG)
        self.lbl_net_up.pack(side="left", padx=20)
        
        self.lbl_net_down = ttk.Label(self.net_frame, text="DL: 0 KB/s", background=PANEL_BG)
        self.lbl_net_down.pack(side="left", padx=20)
        
        self.lbl_uptime = ttk.Label(self.net_frame, text="Uptime: 0s", background=PANEL_BG)
        self.lbl_uptime.pack(side="right", padx=20)

    def update_stats(self):
        last_net = psutil.net_io_counters()
        last_time = time.time()
        
        while self.running:
            # CPU
            cpu_pct = psutil.cpu_percent(interval=None)
            cpu_cores = psutil.cpu_percent(interval=None, percpu=True)
            
            # Mem
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Net
            curr_net = psutil.net_io_counters()
            curr_time = time.time()
            dt = curr_time - last_time
            if dt > 0:
                ul_speed = (curr_net.bytes_sent - last_net.bytes_sent) / dt
                dl_speed = (curr_net.bytes_recv - last_net.bytes_recv) / dt
            else:
                ul_speed, dl_speed = 0, 0
                
            last_net = curr_net
            last_time = curr_time
            
            # Schedule UI Update safely
            if self.winfo_exists():
                self.after(0, self.update_ui, cpu_pct, cpu_cores, mem, disk, ul_speed, dl_speed)
            
            time.sleep(1)

    def update_ui(self, cpu_p, cpu_c, mem, disk, ul, dl):
        if not self.winfo_exists(): return
        
        # CPU
        self.lbl_cpu_total.config(text=f"Total Load: {cpu_p}%")
        self.pb_cpu_total['value'] = cpu_p
        
        # Simple Ascii-like Bars for cores or Rectangle drawing
        self.cpu_chart_canvas.delete("all")
        w_avail = self.cpu_chart_canvas.winfo_width()
        bar_w = w_avail / len(cpu_c) if len(cpu_c) > 0 else 10
        for i, val in enumerate(cpu_c):
            h = (val / 100) * 80
            x0 = i * bar_w
            y0 = 80 - h
            x1 = x0 + bar_w - 2
            y1 = 80
            color = SUCCESS_COLOR if val < 50 else (WARN_COLOR if val < 80 else ERR_COLOR)
            self.cpu_chart_canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="")

        # RAM
        ram_gb_used = round(mem.used / (1024**3), 1)
        ram_gb_total = round(mem.total / (1024**3), 1)
        self.lbl_ram.config(text=f"RAM: {ram_gb_used} GB / {ram_gb_total} GB ({mem.percent}%)")
        self.pb_ram['value'] = mem.percent

        # Disk
        self.lbl_disk.config(text=f"Disk Usage: {disk.percent}%")
        self.pb_disk['value'] = disk.percent

        # Net
        self.lbl_net_up.config(text=f"↑ {ul/1024:.1f} KB/s")
        self.lbl_net_down.config(text=f"↓ {dl/1024:.1f} KB/s")
        
        uptime = int(time.time() - psutil.boot_time())
        self.lbl_uptime.config(text=f"Uptime: {datetime.timedelta(seconds=uptime)}")

    def view_logs(self):
        log_win = tk.Toplevel(self)
        log_win.title("Security Audit Logs")
        log_win.geometry("600x400")
        log_win.configure(bg=BG_COLOR)
        
        txt = tk.Text(log_win, bg=ENTRY_BG, fg=FG_COLOR, font=("Consolas", 9))
        txt.pack(fill="both", expand=True)
        
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r") as f:
                txt.insert("end", f.read())
        else:
            txt.insert("end", "No logs found.")
    
    def rotate_keys(self):
        if messagebox.askyesno("Confirm", "Rotate Encryption Keys? This will re-key the internal TPM simulation."):
            self.controller.auth_manager.tpm.rotate_key()
            self.controller.auth_manager.log_event("ADMIN", "Manual key rotation triggered")
            messagebox.showinfo("Done", "Key Rotated Successfully.")

    def logout(self):
        self.running = False
        self.controller.show_login_screen()

# ----------------------------
# MAIN ENTRY POINT
# ----------------------------

if __name__ == "__main__":
    if not os.path.exists(DB_FILE):
        # Create dummy file if not exists
        pass
        
    app = App()
    app.mainloop()
