"""
JEEVAN UI - Right Context Panel
Narrow floating glass context panel with tabbed navigation (Recent, Tasks, Messages, Files).
"""
import os
from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget, QListWidget, QListWidgetItem
from PySide6.QtCore import Qt

class ContextPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(260)
        self.setStyleSheet("""
            QWidget#ContextContainer {
                background-color: rgba(12, 16, 26, 0.75);
                border-left: 1px solid rgba(0, 210, 255, 0.15);
                border-radius: 12px;
            }
            QLabel#Title {
                font-family: 'Segoe UI';
                font-size: 11px;
                font-weight: bold;
                color: #00d2ff;
                letter-spacing: 1.5px;
            }
            QTabWidget::pane {
                border: none;
                background: transparent;
            }
            QTabBar::tab {
                background: transparent;
                color: #94a3b8;
                font-family: 'Segoe UI';
                font-size: 11px;
                font-weight: 500;
                padding: 6px 10px;
                border: 1px solid transparent;
            }
            QTabBar::tab:selected {
                color: #00d2ff;
                border-bottom: 2px solid #00d2ff;
                font-weight: bold;
            }
            QListWidget {
                background: transparent;
                border: none;
                color: #e2e8f0;
                font-family: 'Segoe UI';
                font-size: 12px;
            }
            QListWidget::item {
                padding: 8px 4px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        container = QWidget()
        container.setObjectName("ContextContainer")
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(14, 16, 14, 16)
        c_layout.setSpacing(10)

        title = QLabel("CONTEXT & RECENT")
        title.setObjectName("Title")
        c_layout.addWidget(title)

        tabs = QTabWidget()
        
        # Recent Files tab
        recent_list = QListWidget()
        try:
            home = Path.home()
            docs = list(home.glob("Documents/*.*"))[:5]
            if not docs:
                docs = list(Path(__file__).resolve().parent.parent.glob("*.*"))[:5]
            for f in docs:
                recent_list.addItem(f"📄 {f.name}")
        except Exception:
            recent_list.addItem("📄 AI_Tools_Comparison.pdf")
            recent_list.addItem("📄 Project_Plan.md")
            recent_list.addItem("📄 Model_Research.xlsx")

        tabs.addTab(recent_list, "Files")

        # Tasks tab
        tasks_list = QListWidget()
        tasks_list.addItem("📋 Team Sync Brief")
        tasks_list.addItem("📋 Code Architecture Review")
        tasks_list.addItem("📋 Deep Research Report")
        tabs.addTab(tasks_list, "Tasks")

        # Messages tab
        msg_list = QListWidget()
        msg_list.addItem("💬 Alex Rivera: Review draft")
        msg_list.addItem("✉️ Gmail: Invoice confirmation")
        tabs.addTab(msg_list, "Messages")

        c_layout.addWidget(tabs)
        layout.addWidget(container)
