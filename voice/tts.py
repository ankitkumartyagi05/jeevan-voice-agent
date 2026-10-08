"""
JEEVAN Voice - Text-To-Speech Engine
Supports native SAPI.SpVoice on Windows for zero-latency interruptible async speech,
with pyttsx3 fallback. Fully supports barge-in cancellation and configurable voice parameters.
"""
import os
import sys
import time
import logging
import threading
from typing import Optional, Callable

logger = logging.getLogger("JEEVAN.TTS")

class TTSEngine:
    def __init__(self):
        self._is_speaking = False
        self._lock = threading.Lock()
        self._sapi_voice = None
        self._pyttsx_engine = None
        self._use_sapi = False
        self._monitor_thread = None
        self._stop_event = threading.Event()
        self._current_callback: Optional[Callable[[], None]] = None
        self.rate = 1  # -10 to 10 for SAPI (0 is normal)
        self.volume = 100  # 0 to 100

        self._init_engine()

    def _init_engine(self):
        if sys.platform == "win32":
            try:
                import win32com.client
                # pythoncom must be initialized on thread if used
                self._sapi_voice = win32com.client.Dispatch("SAPI.SpVoice")
                self._sapi_voice.Rate = self.rate
                self._sapi_voice.Volume = self.volume
                # Select a modern desktop voice if available (e.g. Zira or David)
                voices = self._sapi_voice.GetVoices()
                for i in range(voices.Count):
                    desc = voices.Item(i).GetDescription().lower()
                    if "zira" in desc or "david" in desc:
                        self._sapi_voice.Voice = voices.Item(i)
                        break
                self._use_sapi = True
                logger.info("[VOICE] TTS initialized using native Windows SAPI.")
                return
            except Exception as e:
                logger.warning(f"[VOICE] Windows SAPI initialization failed, using pyttsx3 fallback: {e}")

        # Fallback to pyttsx3
        try:
            import pyttsx3
            self._pyttsx_engine = pyttsx3.init()
            self._pyttsx_engine.setProperty("rate", 175)
            self._pyttsx_engine.setProperty("volume", 0.95)
            self._use_sapi = False
            logger.info("[VOICE] TTS initialized using pyttsx3 fallback.")
        except Exception as e:
            logger.error(f"[VOICE] TTS engine initialization failed completely: {e}")

    def is_speaking(self) -> bool:
        """Returns True if speech is actively rendering."""
        if self._use_sapi and self._sapi_voice:
            try:
                # RunningState: 0 = speaking / queued, 1 = done
                return self._is_speaking and (self._sapi_voice.Status.RunningState == 0)
            except Exception:
                return self._is_speaking
        return self._is_speaking

    def stop(self):
        """Immediately interrupt / cancel active speech (Barge-in support)."""
        with self._lock:
            self._stop_event.set()
            if self._use_sapi and self._sapi_voice:
                try:
                    # Flag 2 = SVSFPurgeBeforeSpeak (purges active speech buffer instantly)
                    self._sapi_voice.Speak("", 2)
                except Exception as e:
                    logger.debug(f"[VOICE] SAPI purge error: {e}")
            elif self._pyttsx_engine:
                try:
                    self._pyttsx_engine.stop()
                except Exception:
                    pass

            if self._is_speaking:
                logger.info("[VOICE] TTS interrupted / cancelled.")
                self._is_speaking = False

            if self._current_callback:
                self._current_callback = None

    def speak(self, text: str, on_finish: Optional[Callable[[], None]] = None):
        """Speak given text asynchronously with auto-cancellation of previous speech."""
        if not text or not text.strip():
            if on_finish:
                on_finish()
            return

        clean_text = text.strip()
        # Cancel any ongoing speech first (never overlap speech!)
        self.stop()

        self._stop_event.clear()
        self._is_speaking = True
        self._current_callback = on_finish
        logger.info(f"[VOICE] TTS started: '{clean_text[:60]}...'")

        if self._use_sapi and self._sapi_voice:
            def run_sapi():
                try:
                    import pythoncom
                    pythoncom.CoInitialize()
                    # Flag 1 = SVSFlagsAsync (asynchronous, non-blocking)
                    self._sapi_voice.Speak(clean_text, 1)
                    
                    # Monitor until speech completes or is interrupted
                    while not self._stop_event.is_set():
                        try:
                            state = self._sapi_voice.Status.RunningState
                            if state == 1:  # Completed
                                break
                        except Exception:
                            break
                        time.sleep(0.05)

                    if not self._stop_event.is_set():
                        logger.info("[VOICE] TTS completed.")
                except Exception as e:
                    logger.error(f"[VOICE] SAPI speech error: {e}")
                finally:
                    self._is_speaking = False
                    cb = self._current_callback
                    self._current_callback = None
                    if cb and not self._stop_event.is_set():
                        try:
                            cb()
                        except Exception:
                            pass

            self._monitor_thread = threading.Thread(target=run_sapi, daemon=True)
            self._monitor_thread.start()
        else:
            # Fallback thread for pyttsx3
            def run_pyttsx():
                try:
                    if self._pyttsx_engine:
                        self._pyttsx_engine.say(clean_text)
                        self._pyttsx_engine.runAndWait()
                    if not self._stop_event.is_set():
                        logger.info("[VOICE] TTS completed.")
                except Exception as e:
                    logger.error(f"[VOICE] pyttsx speech error: {e}")
                finally:
                    self._is_speaking = False
                    cb = self._current_callback
                    self._current_callback = None
                    if cb and not self._stop_event.is_set():
                        try:
                            cb()
                        except Exception:
                            pass

            self._monitor_thread = threading.Thread(target=run_pyttsx, daemon=True)
            self._monitor_thread.start()

    def set_rate(self, rate_val: int):
        """Set speech rate (-5 to 5 for SAPI, 100-250 for pyttsx3)."""
        self.rate = rate_val
        if self._use_sapi and self._sapi_voice:
            try:
                self._sapi_voice.Rate = rate_val
            except Exception:
                pass
        elif self._pyttsx_engine:
            try:
                self._pyttsx_engine.setProperty("rate", rate_val)
            except Exception:
                pass

    def set_volume(self, vol_val: int):
        """Set speech volume (0 to 100)."""
        self.volume = max(0, min(100, vol_val))
        if self._use_sapi and self._sapi_voice:
            try:
                self._sapi_voice.Volume = self.volume
            except Exception:
                pass
        elif self._pyttsx_engine:
            try:
                self._pyttsx_engine.setProperty("volume", self.volume / 100.0)
            except Exception:
                pass

tts_engine = TTSEngine()
