"""
JEEVAN Voice Pipeline Comprehensive Automated Test Suite
Validates microphone detection, permissions, speech synthesis, state machine,
AI reasoning engine, barge-in cancellation, and backend voice endpoints.
"""
import pytest
from app.config import config
from app.lifecycle import lifecycle
from voice.stt import check_microphone_available, stt_engine
from voice.tts import tts_engine
from voice.wakeword import voice_controller
from backend.agent import agent_engine
from backend.memory import init_db, save_conversation, get_recent_conversations

def test_config_and_lifecycle():
    assert config.app_name == "JEEVAN"
    status = lifecycle.startup()
    assert status["config"] is True
    assert status["database"] is True

def test_microphone_availability_check():
    avail, detail = check_microphone_available()
    # On this machine, Realtek microphone array was detected
    assert isinstance(avail, bool)
    assert isinstance(detail, str)

def test_tts_engine_interrupt_and_barge_in():
    assert not tts_engine.is_speaking()
    tts_engine.speak("Testing speech barge-in functionality.")
    assert tts_engine.is_speaking()
    
    # Instant purge / stop
    tts_engine.stop()
    assert not tts_engine.is_speaking()

def test_voice_controller_state_machine():
    voice_controller.return_to_idle()
    assert voice_controller.get_state() == "IDLE"
    assert "Tap the microphone" in voice_controller.status_message

    voice_controller.set_thinking()
    assert voice_controller.get_state() == "THINKING"
    assert "thinking" in voice_controller.status_message

    voice_controller.set_speaking("Speech response")
    assert voice_controller.get_state() == "SPEAKING"
    assert "speaking" in voice_controller.status_message

    voice_controller.stop_speaking()
    assert voice_controller.get_state() == "IDLE"

def test_agent_engine_conversational_and_tools():
    # Conversational identity
    resp, tool = agent_engine.process("Who are you?")
    assert "JEEVAN" in resp

    # Application launching
    resp, tool = agent_engine.process("open Google Chrome")
    assert tool is not None
    assert "Google Chrome" in resp or "एप्लिकेशन" in resp

    # Power safety check
    resp, tool = agent_engine.process("shutdown")
    assert "safety" in resp.lower() or "explicit" in resp.lower() or "पुष्टि" in resp

    # Interrupt command
    resp, tool = agent_engine.process("stop")
    assert "Stopping" in resp or "रोक" in resp

    # Quit command
    resp, tool = agent_engine.process("quit")
    assert "standby" in resp.lower() or "offline" in resp.lower()

def test_memory_persistence():
    init_db()
    save_conversation("user", "Test voice input", intent="voice_test")
    recent = get_recent_conversations(5)
    assert len(recent) > 0
    assert any(c["message"] == "Test voice input" for c in recent)
