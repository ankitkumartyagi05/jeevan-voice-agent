"""
JEEVAN UI - Live Intelligence Event Log Panel
Floating dark glass panel showing live agent reasoning event updates.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QColor

class LiveIntelligencePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QWidget#LiveFrame {
                background-color: rgba(12, 18, 30, 0.75);
                border: 1px solid rgba(0, 210, 255, 0.2);
                border-radius: 14px;
            }
            QLabel#Title {
                font-family: 'Segoe UI';
                font-size: 11px;
                font-weight: bold;
                color: #00d2ff;
                letter-spacing: 1.5px;
            }
            QListWidget {
                background: transparent;
                border: none;
                color: #cbd5e1;
                font-family: 'Segoe UI';
                font-size: 12px;
            }
            QListWidget::item {
                padding: 6px 0px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        container = QWidget()
        container.setObjectName("LiveFrame")
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(16, 14, 16, 14)
        c_layout.setSpacing(10)

        title = QLabel("LIVE INTELLIGENCE")
        title.setObjectName("Title")
        c_layout.addWidget(title)

        self.list_widget = QListWidget()
        c_layout.addWidget(self.list_widget)

        layout.addWidget(container)

        # Default initial events
        self.add_event("⚡ JEEVAN system online & operational")
        self.add_event("🎤 Voice pipeline active: Tap microphone to speak")


    def add_event(self, text: str):
        item = QListWidgetItem(f"•  {text}")
        self.list_widget.addItem(item)
        self.list_widget.scrollToBottom()

    def update_from_agent_event(self, data: dict):
        msg = data.get("message", "Processing...")
        self.add_event(msg)

