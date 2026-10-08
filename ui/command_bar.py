"""
JEEVAN UI - Primary Command Bar
Features interactive microphone with real-time state feedback (IDLE, LISTENING, PROCESSING,
THINKING, SPEAKING, ERROR), live transcript display, stop/retry controls, and dark-glass styling.
"""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton, QLabel, QFrame
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QColor
from voice.wakeword import voice_controller

class CommandBarWidget(QWidget):
    command_submitted = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_state = "IDLE"
        self.setFixedHeight(74)

        self.setStyleSheet("""
            QWidget#BarContainer {
                background-color: rgba(12, 18, 30, 0.88);
                border: 1px solid rgba(0, 210, 255, 0.3);
                border-radius: 18px;
            }
            QLineEdit#InputField {
                background: transparent;
                border: none;
                color: #ffffff;
                font-family: 'Segoe UI';
                font-size: 15px;
                padding-left: 10px;
            }
            QLineEdit#InputField::placeholder {
                color: rgba(160, 175, 200, 0.55);
            }
            QLabel#StatusBanner {
                font-family: 'Segoe UI';
                font-size: 11px;
                color: #00d2ff;
                padding-left: 10px;
                padding-bottom: 2px;
            }
            QPushButton#MicBtn {
                background-color: rgba(0, 210, 255, 0.15);
                color: #00d2ff;
                border: 1px solid rgba(0, 210, 255, 0.4);
                border-radius: 22px;
                font-size: 17px;
                min-width: 44px;
                min-height: 44px;
            }
            QPushButton#MicBtn:hover {
                background-color: rgba(0, 210, 255, 0.35);
                color: #ffffff;
            }
            QPushButton#StopBtn {
                background-color: rgba(239, 68, 68, 0.2);
                color: #ef4444;
                border: 1px solid rgba(239, 68, 68, 0.5);
                border-radius: 14px;
                font-weight: bold;
                padding: 8px 14px;
                font-size: 12px;
            }
            QPushButton#StopBtn:hover {
                background-color: rgba(239, 68, 68, 0.4);
                color: #ffffff;
            }
            QPushButton#SendBtn {
                background-color: #00d2ff;
                color: #090a0f;
                font-weight: bold;
                border: none;
                border-radius: 14px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton#SendBtn:hover {
                background-color: #33e0ff;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.container = QWidget()
        self.container.setObjectName("BarContainer")
        bar_layout = QHBoxLayout(self.container)
        bar_layout.setContentsMargins(12, 8, 12, 8)
        bar_layout.setSpacing(10)

        # 1. Interactive Microphone Button
        self.mic_btn = QPushButton("🎤")
        self.mic_btn.setObjectName("MicBtn")
        self.mic_btn.setToolTip("Tap microphone to talk")
        self.mic_btn.clicked.connect(self._on_mic_click)
        bar_layout.addWidget(self.mic_btn)

        # 2. Central Input & Live Status Column
        center_box = QVBoxLayout()
        center_box.setSpacing(2)

        self.input_field = QLineEdit()
        self.input_field.setObjectName("InputField")
        self.input_field.setPlaceholderText("Ask JEEVAN anything or tap the microphone to talk...")
        self.input_field.returnPressed.connect(self._on_submit)
        center_box.addWidget(self.input_field)

        self.status_banner = QLabel("Tap the microphone to talk")
        self.status_banner.setObjectName("StatusBanner")
        center_box.addWidget(self.status_banner)

        bar_layout.addLayout(center_box, stretch=1)

        # 3. Stop Button (Visible during LISTENING or SPEAKING)
        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.setObjectName("StopBtn")
        self.stop_btn.setToolTip("Interrupt / Stop current speech")
        self.stop_btn.clicked.connect(self._on_stop_click)
        self.stop_btn.setVisible(False)
        bar_layout.addWidget(self.stop_btn)

        # 4. Execute / Send Button
        self.send_btn = QPushButton("Execute ➔")
        self.send_btn.setObjectName("SendBtn")
        self.send_btn.clicked.connect(self._on_submit)
        bar_layout.addWidget(self.send_btn)

        layout.addWidget(self.container)

        # Connect voice controller signals
        voice_controller.state_changed.connect(self.update_voice_state)
        voice_controller.interim_transcript.connect(self.update_interim_transcript)
        voice_controller.error_received.connect(self.show_error)

    def _on_mic_click(self):
        """Toggle microphone listening or stop if speaking."""
        voice_controller.toggle_listening()

    def _on_stop_click(self):
        """Direct stop button handler."""
        if self.current_state == "SPEAKING":
            voice_controller.stop_speaking()
        elif self.current_state == "LISTENING":
            voice_controller.stop_listening_cancel()
        else:
            voice_controller.return_to_idle()

    def _on_submit(self):
        text = self.input_field.text().strip()
        if text:
            self.input_field.clear()
            self.command_submitted.emit(text)
            voice_controller.set_state("PROCESSING", "Processing your command...")

    def update_voice_state(self, state: str, message: str):
        self.current_state = state
        self.status_banner.setText(message)

        if state == "IDLE":
            self.mic_btn.setText("🎤")
            self.mic_btn.setToolTip("Tap microphone to talk")
            self.mic_btn.setStyleSheet("""
                background-color: rgba(0, 210, 255, 0.15);
                color: #00d2ff;
                border: 1px solid rgba(0, 210, 255, 0.4);
            """)
            self.status_banner.setStyleSheet("color: #94a3b8;")
            self.stop_btn.setVisible(False)

        elif state == "LISTENING":
            self.mic_btn.setText("🔴")
            self.mic_btn.setToolTip("Listening... (Tap to finish or stop)")
            self.mic_btn.setStyleSheet("""
                background-color: rgba(239, 68, 68, 0.25);
                color: #ef4444;
                border: 2px solid #ef4444;
            """)
            self.status_banner.setStyleSheet("color: #ef4444; font-weight: bold;")
            self.stop_btn.setText("⏹ Finish")
            self.stop_btn.setVisible(True)

        elif state == "PROCESSING":
            self.mic_btn.setText("⏳")
            self.mic_btn.setToolTip("Processing your command...")
            self.mic_btn.setStyleSheet("""
                background-color: rgba(168, 85, 247, 0.2);
                color: #a855f7;
                border: 1px solid #a855f7;
            """)
            self.status_banner.setStyleSheet("color: #a855f7; font-weight: bold;")
            self.stop_btn.setVisible(False)

        elif state == "THINKING":
            self.mic_btn.setText("🧠")
            self.mic_btn.setToolTip("JEEVAN is thinking...")
            self.mic_btn.setStyleSheet("""
                background-color: rgba(168, 85, 247, 0.25);
                color: #c084fc;
                border: 1px solid #c084fc;
            """)
            self.status_banner.setStyleSheet("color: #c084fc; font-weight: bold;")
            self.stop_btn.setVisible(False)

        elif state == "SPEAKING":
            self.mic_btn.setText("🔊")
            self.mic_btn.setToolTip("JEEVAN is speaking (Tap to stop / interrupt)")
            self.mic_btn.setStyleSheet("""
                background-color: rgba(16, 185, 129, 0.2);
                color: #10b981;
                border: 1px solid #10b981;
            """)
            self.status_banner.setStyleSheet("color: #10b981; font-weight: bold;")
            self.stop_btn.setText("⏹ Stop Speaking")
            self.stop_btn.setVisible(True)

        elif state == "ERROR":
            self.mic_btn.setText("⚠️")
            self.mic_btn.setToolTip("Voice error. Tap to retry.")
            self.mic_btn.setStyleSheet("""
                background-color: rgba(245, 158, 11, 0.2);
                color: #f59e0b;
                border: 1px solid #f59e0b;
            """)
            self.status_banner.setStyleSheet("color: #f59e0b; font-weight: bold;")
            self.stop_btn.setVisible(False)

    def update_interim_transcript(self, text: str):
        if text and text != "Listening...":
            self.status_banner.setText(f'🗣️ "{text}"')
            if self.current_state in ["PROCESSING", "THINKING"]:
                self.input_field.setText(text)

    def show_error(self, err_msg: str):
        self.status_banner.setText(f"⚠️ {err_msg}")
        self.status_banner.setStyleSheet("color: #ef4444; font-weight: bold;")
