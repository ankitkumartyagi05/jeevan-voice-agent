"""
JEEVAN UI - Top Header & Dynamic Greeting
Displays JEEVAN branding, dynamic time-based greeting, and real-time voice state badge.
"""
from datetime import datetime
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from app.config import config
from voice.wakeword import voice_controller

class HeaderWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QLabel#AppTitle {
                font-family: 'Segoe UI';
                font-size: 26px;
                font-weight: 300;
                color: #ffffff;
                letter-spacing: 8px;
            }
            QLabel#AppSub {
                font-family: 'Segoe UI';
                font-size: 11px;
                color: #00d2ff;
                letter-spacing: 2px;
            }
            QLabel#StatusBadge {
                font-family: 'Segoe UI';
                font-size: 11px;
                font-weight: bold;
                border-radius: 10px;
                padding: 4px 12px;
            }
            QLabel#GreetingTitle {
                font-family: 'Segoe UI';
                font-size: 22px;
                font-weight: 600;
                color: #ffffff;
            }
            QLabel#GreetingSub {
                font-family: 'Segoe UI';
                font-size: 14px;
                color: #94a3b8;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Top Header Bar
        top_bar = QHBoxLayout()
        top_bar.addStretch()

        # Center Title
        title_box = QVBoxLayout()
        title_box.setAlignment(Qt.AlignCenter)
        
        app_lbl = QLabel("J E E V A N")
        app_lbl.setObjectName("AppTitle")
        app_lbl.setAlignment(Qt.AlignCenter)

        sub_lbl = QLabel("Personal AI Desktop Agent")
        sub_lbl.setObjectName("AppSub")
        sub_lbl.setAlignment(Qt.AlignCenter)

        title_box.addWidget(app_lbl)
        title_box.addWidget(sub_lbl)

        top_bar.addLayout(title_box)
        top_bar.addStretch()

        # Right Status Badge
        self.status_badge = QLabel("● IDLE — READY")
        self.status_badge.setObjectName("StatusBadge")
        top_bar.addWidget(self.status_badge)

        layout.addLayout(top_bar)

        # Greeting Area
        greeting_box = QVBoxLayout()
        greeting_box.setAlignment(Qt.AlignCenter)
        greeting_box.setSpacing(4)

        greeting_text = self._get_time_greeting()
        self.greet_lbl = QLabel(f"{greeting_text}, {config.user_name}.")
        self.greet_lbl.setObjectName("GreetingTitle")
        self.greet_lbl.setAlignment(Qt.AlignCenter)

        sub_greet = QLabel("What should I take care of?")
        sub_greet.setObjectName("GreetingSub")
        sub_greet.setAlignment(Qt.AlignCenter)

        greeting_box.addWidget(self.greet_lbl)
        greeting_box.addWidget(sub_greet)

        layout.addLayout(greeting_box)

        # Connect voice state changes
        voice_controller.state_changed.connect(self._on_voice_state)
        self.update_status("IDLE")

    def _get_time_greeting(self) -> str:
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return "Good morning"
        elif 12 <= hour < 17:
            return "Good afternoon"
        elif 17 <= hour < 22:
            return "Good evening"
        else:
            return "Good night"

    def _on_voice_state(self, state_str: str, message: str):
        self.update_status(state_str)

    def update_status(self, state_str: str):
        if state_str in ["IDLE", "STANDBY"]:
            self.status_badge.setText("● IDLE — READY")
            self.status_badge.setStyleSheet("""
                color: #00d2ff;
                background-color: rgba(0, 210, 255, 0.15);
                border: 1px solid rgba(0, 210, 255, 0.35);
            """)
        elif state_str == "LISTENING":
            self.status_badge.setText("● LISTENING...")
            self.status_badge.setStyleSheet("""
                color: #ef4444;
                background-color: rgba(239, 68, 68, 0.2);
                border: 1px solid rgba(239, 68, 68, 0.5);
            """)
        elif state_str == "PROCESSING":
            self.status_badge.setText("● PROCESSING...")
            self.status_badge.setStyleSheet("""
                color: #a855f7;
                background-color: rgba(168, 85, 247, 0.2);
                border: 1px solid rgba(168, 85, 247, 0.5);
            """)
        elif state_str == "THINKING":
            self.status_badge.setText("● THINKING...")
            self.status_badge.setStyleSheet("""
                color: #c084fc;
                background-color: rgba(192, 132, 252, 0.2);
                border: 1px solid rgba(192, 132, 252, 0.5);
            """)
        elif state_str == "SPEAKING":
            self.status_badge.setText("● SPEAKING...")
            self.status_badge.setStyleSheet("""
                color: #10b981;
                background-color: rgba(16, 185, 129, 0.2);
                border: 1px solid rgba(16, 185, 129, 0.5);
            """)
        elif state_str == "ERROR":
            self.status_badge.setText("● VOICE ERROR")
            self.status_badge.setStyleSheet("""
                color: #f59e0b;
                background-color: rgba(245, 158, 11, 0.2);
                border: 1px solid rgba(245, 158, 11, 0.5);
            """)
