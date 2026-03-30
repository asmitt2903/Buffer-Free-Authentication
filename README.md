## 1. Project Overview
This application is a dual-purpose desktop tool built with Python and Tkinter. It demonstrates two core computer science concepts:
1.  **Secure Authentication Module**: A simulation of Operating System-level security, featuring Multi-Factor Authentication (MFA/2FA), encrypted credential storage (simulated TPM), and audit logging.
2.  **Real-Time System Monitor**: A live dashboard that tracks your computer's performance (CPU, RAM, Disk, Network) similar to Windows Task Manager or macOS Activity Monitor.

### Key Technical Features
*   **MFA (Multi-Factor Authentication)**: Uses TOTP (Time-based One-Time Password) identical to Google Authenticator.
*   **Simulated TPM (Trusted Platform Module)**: Credentials are not stored in plain text. They are encrypted using a "hardware" key stored in `virtual_tpm.key`.
*   **Audit Logging**: Every login attempt, failure, and security event is cryptographically logged to `auth_audit.log`.
*   **Adaptive Security**: The system detects "high risk" logins (e.g., unusual times or repeated failures) and enforces stricter checks.
*   **Non-Blocking UI**: Uses threading to update system stats every second without freezing the interface.

---

## 2. Getting Started

### Prerequisites
*   Python 3.x installed.
*   The `psutil` library installed (`pip install psutil`).

### Running the App
Run the script from your terminal:
```bash
python secure_monitor_app.py
```

---

## 3. User Manual: How to Use

### A. The Login Screen
When you first open the app, you are greeted by the Secure OS Login screen.

*   **Username & Password**: Enter your credentials here.
    *   *Default Admin*: `admin` / `admin1234`
*   **LOGIN Button**: checks your credentials against the secure database.
    *   If correct, it will ask for an **MFA Code**.
    *   *Note*: Since this is a simulation, check your **Command Prompt / Terminal** window. The app prints the required 6-digit code there (e.g., `[DEBUG] MFA Code: 123456`).
*   **REGISTER Button**: Use this to create a new user.
    *   Enter a new username and password, then click Register.
    *   **Important**: The system will display a "TOTP Secret" (a long string of letters). In a real scenario, you would scan this into an app like Google Authenticator. For this demo, the app will simply print the valid code to the console when you try to log in.

### B. The Dashboard (Main Interface)
Once logged in, you see the System Monitor Dashboard.

#### 1. Sidebar Controls (Left Panel)
*   **User Info**: Displays your current username and role (e.g., `User: admin`, `Role: admin`).
*   **View Audit Logs** *(Admin Only)*:
    *   Opens a new window showing the raw security log.
    *   Use this to see who logged in, when, and if there were any brute-force attacks or key rotations.
*   **Rotate Keys**:
    *   Simulates a hardware security event where the master encryption key is changed.
    *   This re-encrypts the internal "TPM" key. It’s a maintenance task to ensure old backups of the key file become useless.
*   **Logout**:
    *   Securely closes your session and returns you to the Login Screen.

#### 2. System Monitors (Right Panel)
These panels update automatically every second.

*   **CPU Usage**:
    *   **Total Load**: The overall percentage of generic processing power being used.
    *   **Core Visualizer**: A series of colored bars representing each logical core in your CPU.
        *   <span style="color:green">Green</span>: Low usage
        *   <span style="color:yellow">Yellow</span>: Medium usage
        *   <span style="color:red">Red</span>: High usage
*   **Memory & Disk**:
    *   **RAM**: Shows used vs. total memory (e.g., `8.2 GB / 16.0 GB`).
    *   **Disk**: Shows the percentage of space used on your main C: drive.
*   **Network & System**:
    *   **UL (Upload)**: Current speed of data being sent to the internet.
    *   **DL (Download)**: Current speed of data being received.
    *   **Uptime**: How long your computer has been running since the last restart.

---

## 4. Troubleshooting
*   **"Invalid MFA Code"**: Check the terminal window. The code changes every 30 seconds. If you wait too long, the code printed in the terminal might expire. Look for a new one or try again.
*   **"Account Locked"**: If you fail to login 3 times in a row, the system simulates a brute-force protection lockout for 30 seconds. Wait and try again.
