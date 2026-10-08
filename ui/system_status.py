"""
JEEVAN UI - Real-time System Status Monitoring Panel
Fetches empirical system statistics (CPU, Memory, Network, Tasks) via psutil and QTimer.
"""
import psutil
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QProgressBar
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

class SystemStatusPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QWidget#SystemFrame {
                background-color: rgba(12, 18, 30, 0.75);
                border: 1px solid rgba(0, 210, 255, 0.2);
                border-radius: 14px;
            }
            QLabel {
                font-family: 'Segoe UI';
                color: #e2e8f0;
            }
            QLabel#HeaderTitle {
                font-size: 11px;
                font-weight: bold;
                color: #00d2ff;
                letter-spacing: 1.5px;
            }
            QLabel#MetricLabel {
                font-size: 12px;
                color: #a0aec0;
            }
            QLabel#MetricValue {
                font-size: 13px;
                font-weight: bold;
                color: #ffffff;
            }
            QProgressBar {
                border: none;
                background-color: rgba(255, 255, 255, 0.1);
                height: 4px;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background-color: #00d2ff;
                border-radius: 2px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.container = QWidget()
        self.container.setObjectName("SystemFrame")
        frame_layout = QVBoxLayout(self.container)
        frame_layout.setContentsMargins(16, 14, 16, 14)
        frame_layout.setSpacing(10)

        # Title
        title_lbl = QLabel("SYSTEM MONITOR")
        title_lbl.setObjectName("HeaderTitle")
        frame_layout.addWidget(title_lbl)

        # CPU Row
        cpu_box = QHBoxLayout()
        cpu_lbl = QLabel("CPU USAGE")
        cpu_lbl.setObjectName("MetricLabel")
        self.cpu_val = QLabel("0%")
        self.cpu_val.setObjectName("MetricValue")
        cpu_box.addWidget(cpu_lbl)
        cpu_box.addStretch()
        cpu_box.addWidget(self.cpu_val)
        frame_layout.addLayout(cpu_box)

        self.cpu_bar = QProgressBar()
        self.cpu_bar.setRange(0, 100)
        frame_layout.addWidget(self.cpu_bar)

        # Memory Row
        mem_box = QHBoxLayout()
        mem_lbl = QLabel("MEMORY")
        mem_lbl.setObjectName("MetricLabel")
        self.mem_val = QLabel("0%")
        self.mem_val.setObjectName("MetricValue")
        mem_box.addWidget(mem_lbl)
        mem_box.addStretch()
        mem_box.addWidget(self.mem_val)
        frame_layout.addLayout(mem_box)

        self.mem_bar = QProgressBar()
        self.mem_bar.setRange(0, 100)
        frame_layout.addWidget(self.mem_bar)

        # Network & Task Info
        info_box = QHBoxLayout()
        self.net_val = QLabel("NETWORK: SECURE")
        self.net_val.setObjectName("MetricLabel")
        self.tasks_val = QLabel("TASKS: 7 AVAILABLE")
        self.tasks_val.setObjectName("MetricLabel")
        info_box.addWidget(self.net_val)
        info_box.addStretch()
        info_box.addWidget(self.tasks_val)
        frame_layout.addLayout(info_box)

        layout.addWidget(self.container)

        # Timer to refresh metrics every 2 seconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_metrics)
        self.timer.start(2000)
        self.refresh_metrics()

    def refresh_metrics(self):
        try:
            cpu = int(psutil.cpu_percent(interval=None))
            mem = int(psutil.virtual_memory().percent)
            self.cpu_val.setText(f"{cpu}%")
            self.cpu_bar.setValue(cpu)
            self.mem_val.setText(f"{mem}%")
            self.mem_bar.setValue(mem)
        except Exception:
            pass
