"""
JEEVAN UI - Main Application Window
Assembles the complete dark glass desktop operating environment window.
Coordinates voice controller, agent runtime, and real-time state displays.
"""
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette

from app.config import config
from ui.header import HeaderWidget
from ui.navigation import NavigationPanel
from ui.command_bar import CommandBarWidget
from ui.intelligence_core import IntelligenceCoreWidget
from ui.spatial_tools import SpatialToolRingWidget
from ui.system_status import SystemStatusPanel
from ui.live_intelligence import LiveIntelligencePanel
from ui.current_task import CurrentTaskPanel
from ui.context_panel import ContextPanel
from ui.action_cards import ActionCardsPanel

from voice.wakeword import voice_controller
from agent.runtime import agent_runtime

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(config.app_title)
        self.resize(1440, 900)
        self.setMinimumSize(1280, 720)

        # Set graphite window background
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(9, 10, 15))
        self.setPalette(palette)

        # Central Widget
        
        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: #090a0f;")
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(14)

        # 1. Left Navigation
        self.nav_panel = NavigationPanel()
        main_layout.addWidget(self.nav_panel)

        # 2. Main Workspace Column
        center_column = QVBoxLayout()
        center_column.setSpacing(14)

        # Top Header
        self.header = HeaderWidget()
        center_column.addWidget(self.header)

        # Command Bar
        self.command_bar = CommandBarWidget()
        self.command_bar.command_submitted.connect(self._on_user_command)
        center_column.addWidget(self.command_bar)

        # Central Interactive Grid (3-column layout)
        grid_layout = QHBoxLayout()
        grid_layout.setSpacing(14)

        # Grid Left: Live Intelligence + System Status
        left_grid = QVBoxLayout()
        left_grid.setSpacing(14)
        self.live_intel = LiveIntelligencePanel()
        self.system_status = SystemStatusPanel()
        left_grid.addWidget(self.live_intel, stretch=1)
        left_grid.addWidget(self.system_status, stretch=1)
        grid_layout.addLayout(left_grid, stretch=1)

        # Grid Center: Intelligence Core & Spatial Ring
        center_grid = QVBoxLayout()
        center_grid.setSpacing(10)
        self.intel_core = IntelligenceCoreWidget()
        self.spatial_tools = SpatialToolRingWidget()
        self.spatial_tools.tool_selected.connect(self._on_tool_selected)
        center_grid.addWidget(self.intel_core, stretch=1, alignment=Qt.AlignCenter)
        center_grid.addWidget(self.spatial_tools, alignment=Qt.AlignCenter)
        grid_layout.addLayout(center_grid, stretch=2)

        # Grid Right: Current Task
        right_grid = QVBoxLayout()
        right_grid.setSpacing(14)
        self.current_task = CurrentTaskPanel()
        right_grid.addWidget(self.current_task, stretch=1)
        grid_layout.addLayout(right_grid, stretch=1)

        center_column.addLayout(grid_layout, stretch=1)

        # Bottom Action Cards
        self.action_cards = ActionCardsPanel()
        self.action_cards.card_clicked.connect(self._on_card_clicked)
        center_column.addWidget(self.action_cards)

        main_layout.addLayout(center_column, stretch=1)

        # 3. Right Context Panel
        self.context_panel = ContextPanel()
        main_layout.addWidget(self.context_panel)

        # Connect Signals
        voice_controller.state_changed.connect(self._on_voice_state_changed)
        voice_controller.command_received.connect(self._on_user_command)
        agent_runtime.event_emitted.connect(self.live_intel.update_from_agent_event)
        agent_runtime.response_ready.connect(self._on_agent_response)

    def closeEvent(self, event):
        """Cleanly shutdown voice background thread and UI timers when window closes."""
        voice_controller.stop_listening()
        if hasattr(self, 'system_status') and hasattr(self.system_status, 'timer'):
            self.system_status.timer.stop()
        if hasattr(self, 'intel_core') and hasattr(self.intel_core, 'timer'):
            self.intel_core.timer.stop()
        event.accept()

    def _on_voice_state_changed(self, state: str, message: str = ""):
        self.intel_core.set_state(state)
        self.header.update_status(state)
        if message:
            self.live_intel.add_event(f"Voice state: {state} ({message})")

    def _on_user_command(self, cmd: str):
        self.live_intel.add_event(f"User Command: '{cmd}'")
        self.current_task.set_active_task(cmd, progress=30)
        agent_runtime.execute_command(cmd)

    def _on_agent_response(self, text: str, tool_data: dict):
        self.live_intel.add_event(f"JEEVAN: {text}")
        self.current_task.set_active_task("Task Completed", progress=100)

    def _on_tool_selected(self, tool_name: str):
        cmd = f"open {tool_name}"
        self._on_user_command(cmd)

    def _on_card_clicked(self, action: str):
        cmd = f"prepare {action}"
        self._on_user_command(cmd)
