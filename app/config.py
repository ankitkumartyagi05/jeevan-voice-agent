"""
JEEVAN Desktop Application Configuration
Contains Pydantic settings, wake word configurations, paths, and environment settings.
"""
import os
from pathlib import Path
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

class JEEVANConfig(BaseModel):
    app_name: str = "JEEVAN"
    app_title: str = "JEEVAN — Personal AI Desktop Agent"
    version: str = "2.0.0"
    
    # User Profile
    user_name: str = "Sir"
    
    # Paths
    base_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent)
    data_dir: Path = Field(default_factory=lambda: Path.home() / ".jeevan")
    database_path: Path = Field(default_factory=lambda: Path.home() / ".jeevan" / "jeevan.db")
    
    # AI & API Settings
    gemini_api_key: str = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    default_model: str = "gemini-3.8-flash"
    
    # Wake Word & Voice Protocol
    wake_word: str = "jeevan"
    jeevan_activation_phrase: str = "Yes, I am listening."
    standby_timeout_seconds: int = 45
    
    # Modes
    demo_mode: bool = False
    debug_mode: bool = True
    
    # Audio Settings
    sample_rate: int = 44100
    chunk_size: int = 1024
    
    def initialize_system(self):
        self.data_dir.mkdir(parents=True, exist_ok=True)

config = JEEVANConfig()
config.initialize_system()
