# JEEVAN — Personal AI Desktop Agent

<p align="center">
  <img src="https://img.shields.io/badge/JEEVAN-Personal%20AI%20Desktop%20Agent-00D2FF?style=for-the-badge" alt="JEEVAN">
  <img src="https://img.shields.io/badge/Voice--First-Interruptible%20Agent-7C3AED?style=for-the-badge" alt="Voice-First Agent">
  <img src="https://img.shields.io/badge/UI-Dark%20Glass%20Neural%20Core-00B8D4?style=for-the-badge" alt="Dark Glass UI">
</p>

<p align="center">
  <strong>"Think it. Say it. JEEVAN handles the rest."</strong>
</p>

<p align="center">
  JEEVAN is a personal AI desktop operating layer featuring a native, interruptible, production-grade voice pipeline with hardware microphone detection, adaptive speech recognition, real AI reasoning, and natural text-to-speech feedback.
</p>

---

## 🎙️ Real Voice Pipeline Architecture

```text
Microphone Input
       ↓
Permission Check & Ambient Noise Calibration (44.1kHz / 16kHz)
       ↓
Speech Recognition (Google STT + Local Faster-Whisper Fallback)
       ↓
User Transcript Live Feedback
       ↓
JEEVAN AI Reasoning Engine (Google Gemini + Context Memory + OS Tools)
       ↓
Barge-In Capable TTS (Native Windows SAPI / PyTTSx3)
       ↓
Spoken Response + Conversation History Database
```

---

## ⚡ Voice State Machine

JEEVAN displays its current voice state across the UI:

| State | Display Message | Visual Indicator |
|---|---|---|
| **IDLE** | `Tap the microphone to talk` | Cyan mic outline, ambient breathing pulse |
| **LISTENING** | `Listening...` | Crimson recording ring, audio-reactive waveform expansion |
| **PROCESSING** | `Processing your command...` | Violet orbital spin, transcript locked |
| **THINKING** | `JEEVAN is thinking...` | High-speed neural data-flow animation |
| **SPEAKING** | `JEEVAN is speaking...` | Emerald harmonic waveform, stop button active |
| **ERROR** | `Voice connection failed. Try again.` | Amber alert badge with retry option |

---

## ⚡ Interruption & Barge-In

JEEVAN supports **true conversational barge-in**:
- If JEEVAN is speaking and you begin talking, speech playback is **instantly cancelled** and JEEVAN seamlessly transitions to `LISTENING` mode to capture your new command.
- You can also click the microphone button or the `⏹ Stop Speaking` button at any time to immediately interrupt playback.

---

## 🚀 Quick Start

### 1. Requirements
- Windows 10/11 (or macOS/Linux)
- Python 3.10+
- Dependencies: `sounddevice`, `speech_recognition`, `faster-whisper`, `pyttsx3`, `pydantic`, `PySide6`

### 2. Run Desktop Application
```bash
# Double-click or run batch script
run_app.bat

# Or run directly via Python
python main.py
```

### 3. Run Backend REST API Server
```bash
python backend/server.py
```

---

## 🌐 Voice REST Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/voice/status` | Hardware microphone check & voice pipeline readiness |
| `POST` | `/api/voice/command` | Submit text or voice command to JEEVAN AI engine |
| `POST` | `/api/voice/transcribe` | Transcribe base64 WAV audio with STT engine |
| `POST` | `/api/voice/speak` | Synthesize speech via TTS |
| `GET` | `/api/status` | System metrics & agent status |
| `GET` | `/api/conversations` | Conversation history |

---

## 🗣️ Common Voice Commands

- *"Open Google Chrome"*
- *"Close window"*
- *"Set volume to 70"*
- *"Prepare an email to Alex"*
- *"Create presentation on Artificial Intelligence"*
- *"Deep research quantum computing"*
- *"Stop"* / *"Wait"* (Instant interrupt)
- *"Quit"* (Puts agent in standby)

---

## 🔒 Security & Privacy

- Microphone streams are processed locally and discarded immediately after transcription.
- High-risk operations (e.g. system power controls) require explicit target identification (`"PC"` or `"computer"`).
- Private credentials and OAuth tokens are never committed to persistent conversation history.
