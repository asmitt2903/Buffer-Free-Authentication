import sys, random, psutil
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import pyqtgraph as pg

# -----------------------------
# LOGIN WINDOW
# -----------------------------
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("⚡ Secure Cyber System")
        self.setGeometry(200, 100, 1200, 700)

        self.setStyleSheet("""
        QWidget { background:#0a0f1c; color:white; font-family:Segoe UI; }
        QFrame { background:#111827; border-radius:20px; border:2px solid #22d3ee; }
        QLineEdit { padding:10px; border-radius:10px; border:1px solid #22d3ee; background:#1f2937; }
        QPushButton { background:#06b6d4; border-radius:15px; padding:10px; font-weight:bold; }
        QPushButton:hover { background:#0891b2; }
        """)

        layout = QVBoxLayout()

        card = QFrame()
        card.setFixedSize(400, 300)
        v = QVBoxLayout()

        title = QLabel("⚡ LEGEND ACCESS")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size:24px; color:#22d3ee;")
        v.addWidget(title)

        self.user = QLineEdit()
        self.user.setPlaceholderText("USERNAME")
        v.addWidget(self.user)

        self.pwd = QLineEdit()
        self.pwd.setPlaceholderText("PASSWORD")
        self.pwd.setEchoMode(QLineEdit.EchoMode.Password)
        v.addWidget(self.pwd)

        btn = QPushButton("ENTER SYSTEM")
        btn.clicked.connect(self.login)
        v.addWidget(btn)

        card.setLayout(v)

        layout.addStretch()
        layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        self.setLayout(layout)

    def login(self):
        if self.user.text() == "admin":
            self.dashboard = Dashboard()
            self.dashboard.show()
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Access Denied")

# -----------------------------
# DASHBOARD
# -----------------------------
class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("⚡ GOD MODE DASHBOARD")
        self.setGeometry(200, 100, 1300, 750)

        self.setStyleSheet("""
        QWidget { background:#020617; color:white; }
        QFrame { background:#111827; border-radius:15px; border:1px solid #22d3ee; }
        QLabel { font-size:14px; }
        """)

        layout = QVBoxLayout()

        title = QLabel("⚡ LIVE SYSTEM MONITOR")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size:26px; color:#22d3ee;")
        layout.addWidget(title)

        grid = QGridLayout()

        # CPU GRAPH
        self.cpu_plot = self.create_graph("CPU Usage")
        grid.addWidget(self.cpu_plot["frame"], 0, 0)

        # MEMORY GRAPH
        self.mem_plot = self.create_graph("Memory Usage")
        grid.addWidget(self.mem_plot["frame"], 0, 1)

        # TERMINAL
        self.terminal = QTextEdit()
        self.terminal.setStyleSheet("background:#000; color:#22d3ee;")
        grid.addWidget(self.terminal, 1, 0, 1, 2)

        layout.addLayout(grid)
        self.setLayout(layout)

        # Data
        self.cpu_data = [0]*50
        self.mem_data = [0]*50

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(1000)

    def create_graph(self, title):
        frame = QFrame()
        v = QVBoxLayout()

        lbl = QLabel(title)
        lbl.setStyleSheet("color:#22d3ee; font-size:16px;")
        v.addWidget(lbl)

        plot = pg.PlotWidget()
        plot.setBackground("#111827")
        curve = plot.plot(pen=pg.mkPen("#22d3ee", width=2))

        v.addWidget(plot)
        frame.setLayout(v)

        return {"frame": frame, "plot": plot, "curve": curve}

    def update_data(self):
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent

        self.cpu_data = self.cpu_data[1:] + [cpu]
        self.mem_data = self.mem_data[1:] + [mem]

        self.cpu_plot["curve"].setData(self.cpu_data)
        self.mem_plot["curve"].setData(self.mem_data)

        self.terminal.append(f"> CPU: {cpu}% | MEM: {mem}%")

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = LoginWindow()
    win.show()
    sys.exit(app.exec())
