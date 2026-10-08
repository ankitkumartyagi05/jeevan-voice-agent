"""
JEEVAN UI - Central Intelligence Core Rendering Engine
PySide6 QPainter canvas rendering multi-ring concentric neural geometry, particles, orbital nodes,
audio-reactive waveform visualization, and dynamic voice states (IDLE, LISTENING, THINKING, SPEAKING, ERROR).
"""
import math
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer, QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QRadialGradient
from voice.wakeword import voice_controller

class IntelligenceCoreWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(360, 360)
        self.rotation_angle = 0.0
        self.pulse_factor = 0.0
        self.pulse_direction = 1
        self.audio_energy = 0.0
        self.state = "IDLE"  # IDLE, LISTENING, PROCESSING, THINKING, SPEAKING, ERROR

        # Connect voice controller signals
        voice_controller.state_changed.connect(self._on_voice_state)
        voice_controller.audio_level.connect(self._on_audio_level)

        # Animation timer (60 FPS)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16)

    def _on_voice_state(self, state: str, message: str):
        self.set_state(state)

    def _on_audio_level(self, level: float):
        # Smooth interpolation of audio energy
        self.audio_energy = max(self.audio_energy * 0.7, level)

    def set_state(self, new_state: str):
        self.state = new_state
        try:
            self.update()
        except RuntimeError:
            pass

    def closeEvent(self, event):
        if hasattr(self, 'timer') and self.timer.isActive():
            self.timer.stop()
        super().closeEvent(event)

    def hideEvent(self, event):
        if hasattr(self, 'timer') and self.timer.isActive():
            self.timer.stop()
        super().hideEvent(event)

    def showEvent(self, event):
        if hasattr(self, 'timer') and not self.timer.isActive():
            self.timer.start(16)
        super().showEvent(event)

    def update_animation(self):
        try:
            if not self.isVisible():
                return

            speed = 0.8
            if self.state == "LISTENING":
                speed = 1.8 + (self.audio_energy * 3.0)
            elif self.state in ["PROCESSING", "THINKING"]:
                speed = 4.2
            elif self.state == "SPEAKING":
                speed = 2.6
            elif self.state == "ERROR":
                speed = 0.4

            self.rotation_angle = (self.rotation_angle + speed) % 360.0

            # Pulse breathing effect
            step = 0.015 if self.state != "LISTENING" else 0.03
            self.pulse_factor += step * self.pulse_direction
            if self.pulse_factor >= 1.0:
                self.pulse_factor = 1.0
                self.pulse_direction = -1
            elif self.pulse_factor <= 0.0:
                self.pulse_factor = 0.0
                self.pulse_direction = 1

            # Natural audio energy decay
            self.audio_energy = max(0.0, self.audio_energy - 0.03)

            self.update()
        except RuntimeError:
            if hasattr(self, 'timer') and self.timer.isActive():
                self.timer.stop()

    def paintEvent(self, event):
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)

            width = self.width()
            height = self.height()
            cx = width / 2.0
            cy = height / 2.0
            base_radius = min(width, height) / 2.0 - 20

            # Audio reactive expansion factor
            expansion = self.audio_energy * 24.0 if self.state == "LISTENING" else 0.0
            radius = base_radius + expansion

            # Color Palettes by Voice State
            if self.state in ["IDLE", "STANDBY"]:
                primary_color = QColor(0, 210, 255, 170)
                glow_color = QColor(0, 150, 255, 35)
                status_str = "Tap microphone to talk"
            elif self.state == "LISTENING":
                primary_color = QColor(239, 68, 68, 220)
                glow_color = QColor(239, 68, 68, 70 + int(self.audio_energy * 100))
                status_str = "LISTENING..."
            elif self.state in ["PROCESSING", "THINKING"]:
                primary_color = QColor(168, 85, 247, 240)
                glow_color = QColor(140, 80, 245, 90)
                status_str = "JEEVAN IS THINKING..."
            elif self.state == "SPEAKING":
                primary_color = QColor(16, 185, 129, 230)
                glow_color = QColor(16, 185, 129, 75)
                status_str = "JEEVAN IS SPEAKING..."
            elif self.state == "ERROR":
                primary_color = QColor(245, 158, 11, 200)
                glow_color = QColor(245, 158, 11, 50)
                status_str = "VOICE ERROR"
            else:
                primary_color = QColor(0, 220, 255, 190)
                glow_color = QColor(0, 180, 255, 50)
                status_str = "READY"

            # 1. Background Radial Glow
            grad = QRadialGradient(cx, cy, radius * 1.25)
            grad.setColorAt(0.0, glow_color)
            grad.setColorAt(0.65, QColor(8, 14, 28, 25))
            grad.setColorAt(1.0, QColor(0, 0, 0, 0))
            painter.setBrush(QBrush(grad))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPointF(cx, cy), radius * 1.25, radius * 1.25)

            # 2. Outer Concentric Waveform Rings
            pen_dashed = QPen(primary_color, 1.2)
            pen_dashed.setStyle(Qt.DashLine)
            painter.setPen(pen_dashed)
            painter.drawEllipse(QPointF(cx, cy), radius, radius)

            # Solid inner pulse ring
            pen_solid = QPen(primary_color, 1.5)
            pen_solid.setStyle(Qt.SolidLine)
            painter.setPen(pen_solid)
            r_inner = radius * 0.85 + (self.pulse_factor * 5.0) + (self.audio_energy * 8.0)
            painter.drawEllipse(QPointF(cx, cy), r_inner, r_inner)

            # 3. Rotating Orbital Nodes & Tech Arcs
            painter.save()
            painter.translate(cx, cy)
            painter.rotate(self.rotation_angle)

            arc_radius = radius * 0.70
            arc_rect = QRectF(-arc_radius, -arc_radius, arc_radius * 2, arc_radius * 2)
            pen_arc = QPen(primary_color, 2.5)
            painter.setPen(pen_arc)
            painter.drawArc(arc_rect, 0 * 16, 60 * 16)
            painter.drawArc(arc_rect, 120 * 16, 60 * 16)
            painter.drawArc(arc_rect, 240 * 16, 60 * 16)

            # Orbital Node Dots
            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                nx = arc_radius * math.cos(rad)
                ny = arc_radius * math.sin(rad)
                painter.setBrush(QBrush(primary_color))
                painter.drawEllipse(QPointF(nx, ny), 3.5, 3.5)

            painter.restore()

            # Counter-rotating Inner Arc
            painter.save()
            painter.translate(cx, cy)
            painter.rotate(-self.rotation_angle * 1.4)
            arc_rect_inner = QRectF(-radius * 0.52, -radius * 0.52, radius * 1.04, radius * 1.04)
            pen_inner = QPen(QColor(140, 100, 255, 200), 2.0)
            painter.setPen(pen_inner)
            painter.drawArc(arc_rect_inner, 45 * 16, 90 * 16)
            painter.drawArc(arc_rect_inner, 225 * 16, 90 * 16)
            painter.restore()

            # 4. Center Typography
            painter.setPen(QPen(QColor(255, 255, 255, 240)))
            font_title = QFont("Segoe UI", 16, QFont.Bold)
            font_title.setLetterSpacing(QFont.AbsoluteSpacing, 5)
            painter.setFont(font_title)
            painter.drawText(QRectF(cx - 150, cy - 36, 300, 30), Qt.AlignCenter, "JEEVAN")

            font_sub = QFont("Segoe UI", 9, QFont.Medium)
            font_sub.setLetterSpacing(QFont.AbsoluteSpacing, 2)
            painter.setFont(font_sub)
            painter.setPen(QPen(primary_color))
            painter.drawText(QRectF(cx - 150, cy - 6, 300, 20), Qt.AlignCenter, "INTELLIGENCE CORE")

            font_status = QFont("Segoe UI", 8, QFont.Normal)
            painter.setFont(font_status)
            painter.setPen(QPen(QColor(180, 200, 220, 180)))
            painter.drawText(QRectF(cx - 150, cy + 20, 300, 20), Qt.AlignCenter, status_str)

        except RuntimeError:
            pass
