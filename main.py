"""
JEEVAN Desktop Application Launcher
Entry point for starting the native PySide6 JEEVAN AI Desktop Operating Environment.
"""
import sys
import logging
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

from app.lifecycle import lifecycle
from ui.main_window import MainWindow
from voice.wakeword import voice_controller

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("JEEVAN.Main")

def main():
    logger.info("Starting JEEVAN Desktop Application...")
    
    # 1. Initialize QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("JEEVAN")
    app.setOrganizationName("JEEVAN Protocol")

    # Set default UI font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # 2. Run Application Lifecycle Startup Checks
    lifecycle.startup()

    # 3. Create & Show Main Window
    window = MainWindow()
    window.show()

    # 4. Initialize Voice Controller in IDLE state
    voice_controller.start_listening()

    logger.info("JEEVAN Desktop GUI active and visible.")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
