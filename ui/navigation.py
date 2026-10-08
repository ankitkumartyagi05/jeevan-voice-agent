"""
JEEVAN UI - Left Navigation Bar
Narrow vertical navigation panel matching the reference image dark glass aesthetic.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QFrame
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

class NavigationPanel(QWidget):
    nav_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(200)
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(12, 16, 26, 0.75);
                border-right: 1px solid rgba(0, 210, 255, 0.15);
                border-radius: 12px;
            }
            QPushButton {
                background: transparent;
                color: #a0aec0;
                text-align: left;
                padding: 10px 16px;
                border-radius: 8px;
                font-family: 'Segoe UI';
                font-size: 13px;
                font-weight: 500;
                border: 1px solid transparent;
            }
            QPushButton:hover {
                background-color: rgba(0, 210, 255, 0.1);
                color: #00d2ff;
                border: 1px solid rgba(0, 210, 255, 0.25);
            }
            QPushButton:checked {
                background-color: rgba(0, 210, 255, 0.2);
                color: #ffffff;
                border: 1px solid rgba(0, 210, 255, 0.5);
                font-weight: bold;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 20, 12, 20)
        layout.setSpacing(8)

        nav_items = [
            ("⚡ Home", "Home"),
            ("🎛️ Command Center", "Command Center"),
            ("📋 Tasks", "Tasks"),
            ("📁 Files", "Files"),
            ("💬 Messages", "Messages"),
            ("✉️ Email", "Email"),
            ("🔍 Research", "Research"),
            ("💻 Code", "Code"),
            ("🤖 Automations", "Automations"),
            ("⚙️ Settings", "Settings"),
        ]

        self.buttons = {}
        for label, key in nav_items:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, k=key: self._on_click(k))
            layout.addWidget(btn)
            self.buttons[key] = btn

        self.buttons["Home"].setChecked(True)
        layout.addStretch()

    def _on_click(self, key: str):
        for k, btn in self.buttons.items():
            btn.setChecked(k == key)
        self.nav_changed.emit(key)
