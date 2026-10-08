"""
JEEVAN Core Protocol - Pure Standalone Python REST API Backend Server
Contains NO frontend static file logic. Serves strictly JSON REST API endpoints on port 8080 with CORS support.
Includes voice endpoints: /api/voice/command, /api/voice/transcribe, /api/voice/speak, /api/voice/status.
"""
import http.server
import socketserver
import json
import base64
import urllib.parse
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import settings
from backend.agent import agent_engine
from backend.memory import get_recent_conversations, get_all_preferences
from voice.stt import stt_engine, check_microphone_available
from voice.tts import tts_engine

PORT = settings.port

class JEEVANPureAPIHandler(http.server.BaseHTTPRequestHandler):
    
    def _send_cors_headers(self):
        """Sends CORS headers enabling any client to connect."""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')

    def do_OPTIONS(self):
        """Preflight CORS handler."""
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else "{}"

        # 1. Main Command Endpoints (/api/command and /api/voice/command)
        if parsed_path.path in ["/api/command", "/api/voice/command"]:
            try:
                data = json.loads(body)
                user_text = data.get("text", "") or data.get("command", "")
                
                if not user_text or not user_text.strip():
                    self.send_response(400)
                    self._send_cors_headers()
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": False, "error": "Command text cannot be empty"}).encode('utf-8'))
                    return

                resp_text, tool_result = agent_engine.process(user_text)
                
                response_payload = {
                    "success": True,
                    "response": resp_text,
                    "tool_result": tool_result
                }
                
                self.send_response(200)
                self._send_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response_payload).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self._send_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode('utf-8'))
            return

        # 2. Voice Transcription Endpoint (/api/voice/transcribe)
        if parsed_path.path == "/api/voice/transcribe":
            try:
                data = json.loads(body)
                audio_b64 = data.get("audio_base64", "")
                if not audio_b64:
                    self.send_response(400)
                    self._send_cors_headers()
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": False, "error": "Missing audio_base64 data"}).encode('utf-8'))
                    return

                wav_bytes = base64.b64decode(audio_b64)
                transcript = stt_engine.transcribe_wav_bytes(wav_bytes)

                self.send_response(200)
                self._send_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "transcript": transcript}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self._send_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode('utf-8'))
            return

        # 3. Voice TTS Endpoint (/api/voice/speak)
        if parsed_path.path == "/api/voice/speak":
            try:
                data = json.loads(body)
                text_to_speak = data.get("text", "")
                if text_to_speak:
                    tts_engine.speak(text_to_speak)
                
                self.send_response(200)
                self._send_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "status": "Speaking initiated"}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self._send_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode('utf-8'))
            return

        # Endpoint Not Found
        self.send_response(404)
        self._send_cors_headers()
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"error": "Endpoint Not Found"}).encode('utf-8'))

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        
        if parsed_path.path == "/api/status":
            payload = {
                "app": settings.app_name,
                "version": settings.version,
                "status": "ONLINE & LISTENING",
                "interrupt_sensitivity": settings.interrupt_sensitivity,
                "gemini_api_key_set": bool(settings.gemini_api_key)
            }
            self.send_response(200)
            self._send_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(payload).encode('utf-8'))
            return

        if parsed_path.path == "/api/voice/status":
            mic_avail, mic_msg = check_microphone_available()
            payload = {
                "microphone_available": mic_avail,
                "microphone_status": mic_msg,
                "tts_speaking": tts_engine.is_speaking(),
                "stt_engine": "SpeechRecognition (Google STT) + Faster-Whisper Fallback"
            }
            self.send_response(200)
            self._send_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(payload).encode('utf-8'))
            return

        if parsed_path.path == "/api/conversations":
            conversations = get_recent_conversations(30)
            self.send_response(200)
            self._send_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(conversations).encode('utf-8'))
            return

        if parsed_path.path == "/api/preferences":
            preferences = get_all_preferences()
            self.send_response(200)
            self._send_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(preferences).encode('utf-8'))
            return

        self.send_response(404)
        self._send_cors_headers()
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"error": "Pure API Backend Server - No Frontend Files Loaded Here"}).encode('utf-8'))

def run_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), JEEVANPureAPIHandler) as httpd:
        print(f"====================================================")
        print(f"  {settings.app_name} v{settings.version} PURE REST API BACKEND SERVER")
        print(f"  API URL: http://localhost:{PORT}")
        print(f"  Endpoints: /api/command | /api/voice/command | /api/voice/transcribe | /api/voice/status")
        print(f"====================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nJEEVAN Pure API Backend Server stopping...")
            httpd.server_close()

if __name__ == "__main__":
    run_server()
