"""
JEEVAN Voice - Resilient Multilingual Speech-To-Text Engine
Provides microphone permission validation, adaptive ambient noise thresholding,
audio-reactive energy stream, SpeechRecognition (Google STT) & faster-whisper fallback.
"""
import io
import time
import wave
import logging
from typing import Tuple, Optional
import numpy as np
import sounddevice as sd
from PySide6.QtCore import QThread, Signal, QObject

logger = logging.getLogger("JEEVAN.STT")


def check_microphone_available() -> Tuple[bool, str]:
    """Validates hardware microphone existence and permission."""
    try:
        devices = sd.query_devices()
        input_devices = [d for d in devices if d.get('max_input_channels', 0) > 0]
        if not input_devices:
            return False, "No microphone input device detected on system."

        default_in = sd.query_devices(kind='input')
        if not default_in:
            return False, "No default microphone input configured."

        # Quick test stream to verify OS privacy permission
        sr = int(default_in.get('default_samplerate', 44100))
        with sd.InputStream(samplerate=sr, channels=1, blocksize=512):
            pass
        return True, "Microphone available and permission verified."
    except sd.PortAudioError as pe:
        logger.error(f"[VOICE] Microphone PortAudio error: {pe}")
        return False, f"Microphone access error: {pe}"
    except Exception as e:
        logger.error(f"[VOICE] Microphone permission exception: {e}")
        return False, f"Microphone permission denied or device busy: {e}"


class SpeechToTextEngine:
    def __init__(self, model_size="tiny"):
        self.model = None
        self.model_size = model_size
        self._whisper_attempted = False

    def _ensure_whisper_loaded(self):
        if self.model is None and not self._whisper_attempted:
            self._whisper_attempted = True
            try:
                from faster_whisper import WhisperModel
                logger.info(f"[VOICE] Loading local Whisper model '{self.model_size}'...")
                self.model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
                logger.info("[VOICE] Local Whisper model loaded successfully.")
            except Exception as e:
                logger.warning(f"[VOICE] Local Whisper initialization warning: {e}")

    def transcribe_wav_bytes(self, wav_bytes: bytes) -> str:
        """Transcribe WAV bytes using SpeechRecognition first (fast online), then faster-whisper fallback."""
        if not wav_bytes or len(wav_bytes) < 1000:
            return ""

        # Tier 1: SpeechRecognition (Google STT)
        try:
            import speech_recognition as sr
            r = sr.Recognizer()
            with sr.AudioFile(io.BytesIO(wav_bytes)) as source:
                audio_data = r.record(source)

            # Try English first (primary)
            try:
                text = r.recognize_google(audio_data, language="en-US")
                if text and text.strip():
                    return text.strip()
            except Exception:
                pass

            # Try Hindi / Hinglish
            try:
                text = r.recognize_google(audio_data, language="hi-IN")
                if text and text.strip():
                    return text.strip()
            except Exception:
                pass
        except Exception as e:
            logger.debug(f"[VOICE] SpeechRecognition tier exception: {e}")

        # Tier 2: Local faster-whisper fallback
        return self._transcribe_with_whisper(wav_bytes)

    def _transcribe_with_whisper(self, wav_bytes: bytes) -> str:
        try:
            self._ensure_whisper_loaded()
            if self.model is None:
                return ""

            with wave.open(io.BytesIO(wav_bytes), 'rb') as wf:
                sr_rate = wf.getframerate()
                n_frames = wf.getnframes()
                raw_data = wf.readframes(n_frames)
                audio_int16 = np.frombuffer(raw_data, dtype=np.int16)
                audio_float32 = audio_int16.astype(np.float32) / 32768.0

            if sr_rate != 16000 and len(audio_float32) > 0:
                new_len = int(len(audio_float32) * 16000 / sr_rate)
                audio_float32 = np.interp(
                    np.linspace(0, len(audio_float32), new_len),
                    np.arange(len(audio_float32)),
                    audio_float32
                ).astype(np.float32)

            segments, _ = self.model.transcribe(audio_float32, beam_size=1)
            text = " ".join([seg.text for seg in segments]).strip()
            return text
        except Exception as e:
            logger.error(f"[VOICE] Whisper fallback transcription error: {e}")
            return ""


stt_engine = SpeechToTextEngine()


class InteractiveVoiceRecorder(QThread):
    """
    Dedicated audio capture thread with adaptive VAD (Voice Activity Detection),
    audio level broadcasting for visualization, manual stop, and barge-in trigger.
    """
    audio_level = Signal(float)          # 0.0 to 1.0 for real-time visualization
    speech_started = Signal()            # Emitted as soon as user begins speaking (triggers barge-in!)
    transcript_ready = Signal(str)       # Final transcribed command
    error_occurred = Signal(str)         # Human-friendly error description
    capture_cancelled = Signal()         # Emitted on explicit abort

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_running = False
        self.manual_stop_requested = False
        self.native_samplerate = 44100
        self.stream = None

        # Determine native sample rate
        try:
            dev = sd.query_devices(kind='input')
            if dev and 'default_samplerate' in dev:
                self.native_samplerate = int(dev['default_samplerate'])
        except Exception:
            self.native_samplerate = 44100

    def stop_capture(self):
        """Immediately abort recording without processing."""
        self.is_running = False
        self.manual_stop_requested = False
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
        self.quit()
        self.wait(500)

    def finish_listening(self):
        """Signal to finalize current speech and transcribe what was captured so far."""
        self.manual_stop_requested = True

    def _to_wav_bytes(self, audio_data: np.ndarray, samplerate: int) -> bytes:
        audio_int16 = (np.clip(audio_data, -1.0, 1.0) * 32767).astype(np.int16)
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(samplerate)
            wf.writeframes(audio_int16.tobytes())
        return buf.getvalue()

    def run(self):
        self.is_running = True
        self.manual_stop_requested = False
        logger.info(f"[VOICE] Listening started (hardware sample rate: {self.native_samplerate}Hz)...")

        chunk_size = int(self.native_samplerate * 0.1)  # 100ms chunks
        silence_limit = 0.8  # seconds of silence before finalizing
        audio_buffer = []
        silence_duration = 0.0
        speaking = False
        speech_triggered_signal = False

        # Phase 1: Calibrate ambient noise level over first 300ms
        calibration_chunks = []
        adaptive_threshold = 0.015

        try:
            with sd.InputStream(samplerate=self.native_samplerate, channels=1, dtype='float32') as stream:
                self.stream = stream

                # Collect calibration chunks (3 chunks = 300ms)
                for _ in range(3):
                    if not self.is_running:
                        return
                    data, _ = stream.read(chunk_size)
                    chunk = data.flatten()
                    calibration_chunks.append(float(np.sqrt(np.mean(chunk**2))))

                ambient_noise = float(np.mean(calibration_chunks)) if calibration_chunks else 0.005
                adaptive_threshold = max(0.012, ambient_noise * 2.8)
                logger.info(f"[VOICE] Ambient noise: {ambient_noise:.4f}, Adaptive threshold: {adaptive_threshold:.4f}")

                # Phase 2: Active capture loop
                max_listening_timeout = 15.0  # Max seconds before auto-stop
                start_time = time.time()

                while self.is_running:
                    # Timeout check
                    if time.time() - start_time > max_listening_timeout and not speaking:
                        logger.info("[VOICE] Listening timed out with no speech.")
                        self.error_occurred.emit("No speech detected. Tap microphone to try again.")
                        return

                    if self.manual_stop_requested:
                        # User clicked mic to finish listening
                        break

                    data, _ = stream.read(chunk_size)
                    if not self.is_running:
                        break

                    audio_chunk = data.flatten()
                    rms = float(np.sqrt(np.mean(audio_chunk**2)))
                    
                    # Normalize audio level for UI (0.0 to 1.0)
                    norm_level = min(1.0, max(0.0, (rms - ambient_noise) / (adaptive_threshold * 3.0)))
                    self.audio_level.emit(norm_level)

                    if rms > adaptive_threshold:
                        if not speaking:
                            speaking = True
                            if not speech_triggered_signal:
                                speech_triggered_signal = True
                                self.speech_started.emit()
                        audio_buffer.append(audio_chunk)
                        silence_duration = 0.0
                    elif speaking:
                        audio_buffer.append(audio_chunk)
                        silence_duration += 0.1
                        if silence_duration >= silence_limit:
                            logger.info("[VOICE] User finished speaking (silence detected).")
                            break
                    else:
                        # Keep last 2 chunks as pre-speech buffer
                        if len(audio_buffer) >= 2:
                            audio_buffer.pop(0)
                        audio_buffer.append(audio_chunk)

        except Exception as e:
            logger.error(f"[VOICE] Audio capture stream error: {e}")
            self.error_occurred.emit(f"Microphone input error: {e}")
            return
        finally:
            self.is_running = False

        # Phase 3: Transcribe captured speech
        if not audio_buffer or len(audio_buffer) < 3:
            logger.info("[VOICE] Captured audio buffer is empty or too short.")
            self.error_occurred.emit("No speech detected. Tap microphone to speak.")
            return

        full_audio = np.concatenate(audio_buffer)
        duration_sec = len(full_audio) / self.native_samplerate

        if duration_sec < 0.4:
            logger.info(f"[VOICE] Audio duration too short ({duration_sec:.2f}s).")
            self.error_occurred.emit("Speech too brief. Please speak clearly.")
            return

        logger.info(f"[VOICE] Transcribing {duration_sec:.2f}s of speech...")
        wav_bytes = self._to_wav_bytes(full_audio, self.native_samplerate)
        text = stt_engine.transcribe_wav_bytes(wav_bytes)

        if text and text.strip():
            clean_text = text.strip()
            logger.info(f"[VOICE] Final transcript received: '{clean_text}'")
            self.transcript_ready.emit(clean_text)
        else:
            logger.info("[VOICE] Transcription returned empty text.")
            self.error_occurred.emit("Could not understand audio. Please try again.")
