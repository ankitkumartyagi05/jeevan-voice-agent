"""
JEEVAN UI - Bottom Action Cards
Elegant floating action shortcut cards matching section 18 of specification.
"""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame, QPushButton
from PySide6.QtCore import Qt, Signal

class ActionCardsPanel(QWidget):
    card_clicked = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame#CardFrame {
                background-color: rgba(12, 18, 30, 0.7);
                border: 1px solid rgba(0, 210, 255, 0.2);
                border-radius: 12px;
            }
            QFrame#CardFrame:hover {
                background-color: rgba(0, 210, 255, 0.12);
                border: 1px solid rgba(0, 210, 255, 0.5);
            }
            QLabel#CardTitle {
                font-family: 'Segoe UI';
                font-size: 13px;
                font-weight: bold;
                color: #ffffff;
            }
            QLabel#CardSub {
                font-family: 'Segoe UI';
                font-size: 11px;
                color: #94a3b8;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        cards = [
            ("⚡ Work Smarter", "Search, research, analyze, create", "research"),
            ("📁 Organize Everything", "Files, emails, messages, tasks", "files"),
            ("🤖 Automate Workflows", "Save time, eliminate repetitive work", "automations"),
            ("💻 Build & Create", "Code, design, documents, apps", "code"),
        ]

        for title, sub, action in cards:
            frame = QFrame()
            frame.setObjectName("CardFrame")
            f_layout = QVBoxLayout(frame)
            f_layout.setContentsMargins(14, 12, 14, 12)
            f_layout.setSpacing(4)

            t_lbl = QLabel(title)
            t_lbl.setObjectName("CardTitle")
            s_lbl = QLabel(sub)
            s_lbl.setObjectName("CardSub")

            f_layout.addWidget(t_lbl)
            f_layout.addWidget(s_lbl)

            # Make clickable
            frame.mousePressEvent = lambda event, a=action: self.card_clicked.emit(a)
            layout.addWidget(frame)
