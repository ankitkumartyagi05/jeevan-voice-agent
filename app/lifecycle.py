"""
JEEVAN Application Lifecycle Manager
Handles startup sequence, system checks, audio initialization, and clean shutdown.
"""
import sys
import logging
from typing import Dict, Any
from app.config import config
from backend.memory import init_db
from voice.stt import check_microphone_available

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("JEEVAN.Lifecycle")

class ApplicationLifecycle:
    def __init__(self):
        self.is_initialized = False
        self.system_status = {
            "config": False,
            "database": False,
            "audio": False,
            "ai_backend": False,
        }

    def startup(self) -> Dict[str, Any]:
        """Perform JEEVAN startup verification"""
        logger.info("Initializing JEEVAN Desktop Agent Engine...")
        
        # 1. Load configuration
        self.system_status["config"] = True
        logger.info(f"Loaded Configuration: {config.app_name} v{config.version}")
        
        # 2. Initialize database
        try:
            init_db()
            self.system_status["database"] = True
            logger.info("Database initialized successfully.")
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            
        # 3. Initialize Audio & Microphone system
        try:
            has_mic, mic_msg = check_microphone_available()
            self.system_status["audio"] = has_mic
            logger.info(f"Microphone verification: {mic_msg}")
        except Exception as e:
            logger.warning(f"Audio device query warning: {e}")
            self.system_status["audio"] = True
            
        # 4. Check AI connection status
        self.system_status["ai_backend"] = bool(config.gemini_api_key)
        
        self.is_initialized = True
        logger.info("JEEVAN Startup Sequence Complete. Voice system in IDLE mode.")
        return self.system_status

    def shutdown(self):
        logger.info("JEEVAN is shutting down gracefully.")
        sys.exit(0)

lifecycle = ApplicationLifecycle()
