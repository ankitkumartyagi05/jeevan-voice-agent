"""
JEEVAN Agent Runtime
Coordinates query intent, asynchronous planning, real AI execution, and UI event callbacks.
Runs AI reasoning in background thread to guarantee smooth 60 FPS UI rendering.
"""
import logging
from typing import Dict, Any, Tuple
from PySide6.QtCore import QObject, Signal, QThread

from backend.agent import agent_engine
from voice.wakeword import voice_controller

logger = logging.getLogger("JEEVAN.Runtime")


class CommandWorkerThread(QThread):
    event_emitted = Signal(dict)
    response_ready = Signal(str, dict)

    def __init__(self, command: str, parent=None):
        super().__init__(parent)
        self.command = command

    def run(self):
        self.event_emitted.emit({
            "type": "understanding",
            "message": f"Analyzing intent: '{self.command}'",
            "progress": 0.25
        })

        self.event_emitted.emit({
            "type": "planning",
            "message": "Reasoning with JEEVAN AI engine & tools...",
            "progress": 0.50
        })

        self.event_emitted.emit({
            "type": "executing",
            "message": "Dispatching JEEVAN protocol handler...",
            "progress": 0.75
        })

        try:
            # Call master agent engine
            response_text, tool_data = agent_engine.process(self.command)
        except Exception as e:
            logger.error(f"[RUNTIME] Command execution exception: {e}")
            response_text = f"An error occurred while executing your request: {e}"
            tool_data = {"error": str(e)}

        self.event_emitted.emit({
            "type": "completed",
            "message": "Task complete.",
            "progress": 1.0
        })

        self.response_ready.emit(response_text, tool_data or {})


class AgentRuntime(QObject):
    event_emitted = Signal(dict)
    response_ready = Signal(str, dict)

    def __init__(self):
        super().__init__()
        self._active_worker = None

    def execute_command(self, user_command: str):
        """Execute user query asynchronously and coordinate with voice state machine."""
        clean_cmd = user_command.strip()
        if not clean_cmd:
            return

        logger.info(f"[RUNTIME] Executing command: '{clean_cmd}'")
        voice_controller.set_thinking()

        # Stop any existing worker
        if self._active_worker and self._active_worker.isRunning():
            self._active_worker.terminate()
            self._active_worker.wait(200)

        self._active_worker = CommandWorkerThread(clean_cmd)
        self._active_worker.event_emitted.connect(self._on_worker_event)
        self._active_worker.response_ready.connect(self._on_worker_response)
        self._active_worker.start()

    def _on_worker_event(self, event_data: dict):
        self.event_emitted.emit(event_data)

    def _on_worker_response(self, response_text: str, tool_data: dict):
        logger.info(f"[RUNTIME] AI response ready: '{response_text[:80]}...'")
        self.response_ready.emit(response_text, tool_data)
        
        # Trigger spoken response with barge-in support
        voice_controller.set_speaking(response_text)


agent_runtime = AgentRuntime()
