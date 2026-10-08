"""
JEEVAN Core Protocol - Backend Configuration Module
"""
import os
from pathlib import Path
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

class JEEVANSettings(BaseModel):
    app_name: str = "JEEVAN"
    version: str = "2.0.0"
    port: int = 8080
    host: str = "0.0.0.0"
    
    # Paths
    base_dir: Path = Path(__file__).resolve().parent.parent
    data_dir: Path = Field(default_factory=lambda: Path.home() / ".jeevan")
    database_path: Path = Field(default_factory=lambda: Path.home() / ".jeevan" / "jeevan.db")
    
    # AI Settings & Invoke Syntax
    gemini_api_key: str = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    default_model: str = "gemini-3.8-flash"
    wake_word: str = "jeevan"
    
    # Protocol Flags
    interrupt_sensitivity: str = "balanced" # soft, balanced, aggressive
    web_search_permission_required: bool = True

    def initialize_directories(self):
        self.data_dir.mkdir(parents=True, exist_ok=True)

settings = JEEVANSettings()
settings.initialize_directories()
