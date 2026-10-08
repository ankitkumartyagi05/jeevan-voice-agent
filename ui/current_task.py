"""
JEEVAN UI - Current Task Panel
Floating glass panel rendering current running task name, checklist progress, and cancel control.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class CurrentTaskPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QWidget#TaskFrame {
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
            QLabel#TaskName {
                font-family: 'Segoe UI';
                font-size: 13px;
                font-weight: 600;
                color: #ffffff;
            }
            QLabel#CheckItem {
                font-family: 'Segoe UI';
                font-size: 12px;
                color: #94a3b8;
            }
            QProgressBar {
                border: none;
                background-color: rgba(255, 255, 255, 0.1);
                height: 5px;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background-color: #00d2ff;
                border-radius: 2px;
            }
            QPushButton#CancelBtn {
                background: transparent;
                color: #ef4444;
                border: 1px solid rgba(239, 68, 68, 0.4);
                border-radius: 6px;
                font-size: 11px;
                padding: 4px 10px;
            }
            QPushButton#CancelBtn:hover {
                background-color: rgba(239, 68, 68, 0.2);
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        container = QWidget()
        container.setObjectName("TaskFrame")
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(16, 14, 16, 14)
        c_layout.setSpacing(8)

        # Header with Title and Cancel button
        header_box = QHBoxLayout()
        title = QLabel("CURRENT TASK")
        title.setObjectName("Title")
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("CancelBtn")
        cancel_btn.clicked.connect(self.cancel_task)
        header_box.addWidget(title)
        header_box.addStretch()
        header_box.addWidget(cancel_btn)
        c_layout.addLayout(header_box)

        # Active Task Name
        self.task_name_lbl = QLabel("JEEVAN Standby Mode")
        self.task_name_lbl.setObjectName("TaskName")
        c_layout.addWidget(self.task_name_lbl)

        # Checklist steps
        self.step1 = QLabel("✓ Initialize neural system core")
        self.step1.setObjectName("CheckItem")
        self.step2 = QLabel("✓ Connect voice & system protocols")
        self.step2.setObjectName("CheckItem")
        self.step3 = QLabel("◉ Tap microphone or say 'Hey Jeevan'")
        self.step3.setObjectName("CheckItem")
        self.step4 = QLabel("○ Standby for user command")
        self.step4.setObjectName("CheckItem")



        c_layout.addWidget(self.step1)
        c_layout.addWidget(self.step2)
        c_layout.addWidget(self.step3)
        c_layout.addWidget(self.step4)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(50)
        c_layout.addWidget(self.progress_bar)

        layout.addWidget(container)

    def set_active_task(self, name: str, progress: int = 0):
        self.task_name_lbl.setText(name)
        self.progress_bar.setValue(progress)
        self.step3.setText(f"◉ Executing: {name}")

    def cancel_task(self):
        self.task_name_lbl.setText("Task Cancelled")
        self.progress_bar.setValue(0)
        self.step3.setText("○ Cancelled by user")
