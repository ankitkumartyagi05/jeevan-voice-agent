"""
JEEVAN Voice - Master Voice Pipeline & State Machine Controller
Coordinates microphone activation, permission checks, adaptive recording,
STT transcription, barge-in cancellation, TTS playback, and UI state signals.
"""
import time
import logging
from typing import Optional
from PySide6.QtCore import QObject, Signal

from app.config import config
from voice.tts import tts_engine
from voice.stt import InteractiveVoiceRecorder, check_microphone_available

logger = logging.getLogger("JEEVAN.VoiceController")


class VoiceSessionController(QObject):
    """
    Master voice state machine and session controller.
    Supported states:
    - IDLE: "Tap the microphone to talk"
    - LISTENING: "Listening..."
    - PROCESSING: "Processing your command..."
    - THINKING: "JEEVAN is thinking..."
    - SPEAKING: "JEEVAN is speaking..."
    - ERROR: "Voice connection failed. Try again."
    """

    # Primary UI Signals
    state_changed = Signal(str, str)        # (state, display_message)
    audio_level = Signal(float)             # 0.0 to 1.0 audio energy
    interim_transcript = Signal(str)        # Live speech feedback
    command_received = Signal(str)          # Final speech command ready for AI
    error_received = Signal(str)            # Error message for UI notification
    speech_interrupted = Signal()           # Barge-in signal

    def __init__(self):
        super().__init__()
        self.state = "IDLE"
        self.status_message = "Tap the microphone to talk"
        self.recorder_thread: Optional[InteractiveVoiceRecorder] = None
        self._is_shutting_down = False

    def get_state(self) -> str:
        return self.state

    def set_state(self, state: str, message: str):
        self.state = state
        self.status_message = message
        logger.info(f"[VOICE] State transition -> {state}: '{message}'")
        self.state_changed.emit(state, message)

    def toggle_listening(self):
        """Interactive microphone toggle handler (attached to UI microphone button)."""
        if self._is_shutting_down:
            return

        # 1. If currently speaking, clicking mic interrupts speech
        if self.state == "SPEAKING" or tts_engine.is_speaking():
            logger.info("[VOICE] User interrupted speech via microphone button.")
            self.stop_speaking()
            self.start_interactive_listening()
            return

        # 2. If already listening, clicking mic manually stops listening and transcribes
        if self.state == "LISTENING" and self.recorder_thread and self.recorder_thread.isRunning():
            logger.info("[VOICE] User manually ended listening.")
            self.set_state("PROCESSING", "Processing your command...")
            self.recorder_thread.finish_listening()
            return

        # 3. Otherwise start listening
        self.start_interactive_listening()

    def start_interactive_listening(self):
        """Validates microphone and starts voice recording."""
        if self.state == "LISTENING" and self.recorder_thread and self.recorder_thread.isRunning():
            return  # Prevent duplicate sessions

        # Always stop any previous TTS before listening starts
        tts_engine.stop()

        # Check permissions and hardware availability
        available, detail = check_microphone_available()
        if not available:
            logger.error(f"[VOICE] Microphone validation failed: {detail}")
            self.set_state("ERROR", detail)
            self.error_received.emit(detail)
            return

        logger.info("[VOICE] Permission granted & microphone verified.")
        self.set_state("LISTENING", "Listening...")
        self.interim_transcript.emit("Listening...")

        # Initialize and launch recorder thread
        self.recorder_thread = InteractiveVoiceRecorder()
        self.recorder_thread.audio_level.connect(self._on_audio_level)
        self.recorder_thread.speech_started.connect(self._on_speech_started)
        self.recorder_thread.transcript_ready.connect(self._on_transcript_ready)
        self.recorder_thread.error_occurred.connect(self._on_recorder_error)
        self.recorder_thread.start()

    def stop_listening_cancel(self):
        """Immediately cancel listening without executing commands."""
        if self.recorder_thread and self.recorder_thread.isRunning():
            self.recorder_thread.stop_capture()
        self.return_to_idle()

    def stop_speaking(self):
        """Immediately stop TTS speech playback."""
        tts_engine.stop()
        self.return_to_idle()

    def set_thinking(self):
        self.set_state("THINKING", "JEEVAN is thinking...")

    def set_speaking(self, response_text: str):
        """Set state to SPEAKING and begin audio synthesis."""
        self.set_state("SPEAKING", "JEEVAN is speaking...")

        def on_done():
            if self.state == "SPEAKING":
                self.return_to_idle()

        tts_engine.speak(response_text, on_finish=on_done)

    def return_to_idle(self):
        self.set_state("IDLE", "Tap the microphone to talk")
        self.audio_level.emit(0.0)

    # -------------------------------------------------------------
    # Recorder Signal Handlers
    # -------------------------------------------------------------
    def _on_audio_level(self, level: float):
        if self.state == "LISTENING":
            self.audio_level.emit(level)

    def _on_speech_started(self):
        """Barge-in detection: triggered the moment speech energy is registered."""
        if tts_engine.is_speaking():
            logger.info("[VOICE] User speech detected during TTS playback. Triggering barge-in!")
            tts_engine.stop()
            self.speech_interrupted.emit()
        self.interim_transcript.emit("Listening to you...")

    def _on_transcript_ready(self, transcript: str):
        clean = transcript.strip()
        if not clean:
            self.set_state("ERROR", "No speech recognized. Tap microphone to speak.")
            return

        logger.info(f"[VOICE] Sending command to AI pipeline: '{clean}'")
        self.interim_transcript.emit(clean)
        self.set_state("PROCESSING", "Processing your command...")
        self.command_received.emit(clean)

    def _on_recorder_error(self, err_msg: str):
        logger.warning(f"[VOICE] Recorder error: {err_msg}")
        self.set_state("ERROR", err_msg)
        self.error_received.emit(err_msg)

    # -------------------------------------------------------------
    # Text input bridge for wake-word compatibility / keyboard commands
    # -------------------------------------------------------------
    def process_text_input(self, text: str):
        if not text:
            return
        raw = text.strip()
        lower = raw.lower()

        wake_words = ["jeevan", "hey jeevan", "tech buddy", "hey tech buddy", "jarvis", "hey jarvis"]
        matched_wake = None
        for w in wake_words:
            if lower.startswith(w):
                matched_wake = w
                break

        if matched_wake:
            clean_cmd = raw[len(matched_wake):].strip(" ,!.")
            if clean_cmd:
                self.set_state("PROCESSING", "Processing your command...")
                self.command_received.emit(clean_cmd)
            else:
                # Wake word alone activates interactive listening!
                self.start_interactive_listening()
        else:
            self.set_state("PROCESSING", "Processing your command...")
            self.command_received.emit(raw)

    def start_listening(self):
        """Compatibility method for application startup."""
        logger.info("[VOICE] Master Voice Pipeline ready in IDLE mode.")
        self.return_to_idle()

    def stop_listening(self):
        """Clean shutdown handler on window close."""
        self._is_shutting_down = True
        if self.recorder_thread:
            self.recorder_thread.stop_capture()
            self.recorder_thread = None
        tts_engine.stop()
        logger.info("[VOICE] Voice pipeline shutdown cleanly.")


# Global singleton instance (aliased as wake_word_detector for backwards compatibility)
voice_controller = VoiceSessionController()
wake_word_detector = voice_controller
