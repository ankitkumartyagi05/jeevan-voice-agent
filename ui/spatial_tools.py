"""
JEEVAN UI - Spatial Tool Ring Panel
Interactive circular nodes placed around the central intelligence core.
"""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt, Signal

class SpatialToolRingWidget(QWidget):
    tool_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QPushButton#ToolNode {
                background-color: rgba(12, 20, 34, 0.8);
                color: #00d2ff;
                border: 1px solid rgba(0, 210, 255, 0.35);
                border-radius: 20px;
                font-family: 'Segoe UI';
                font-size: 12px;
                font-weight: 600;
                padding: 6px 14px;
            }
            QPushButton#ToolNode:hover {
                background-color: rgba(0, 210, 255, 0.25);
                color: #ffffff;
                border: 1px solid rgba(0, 210, 255, 0.7);
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        tools = [
            ("📁 Files", "files"),
            ("💬 Messages", "messages"),
            ("✉️ Email", "email"),
            ("🌐 Web", "web"),
            ("💻 Code", "code"),
            ("🔍 Research", "research"),
            ("🤖 Automations", "automations"),
            ("📱 Apps", "apps"),
            ("⚙️ System", "system"),
        ]

        for label, name in tools:
            btn = QPushButton(label)
            btn.setObjectName("ToolNode")
            btn.clicked.connect(lambda checked, n=name: self.tool_selected.emit(n))
            layout.addWidget(btn)
