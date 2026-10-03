"""
Main Application Entry Point
Starts the Face Recognition Attendance System
"""

import sys
import logging
from pathlib import Path

# Setup logging
from utils.utils import setup_logging
logger = setup_logging()

def main():
    """
    Main function to start the application.
    """
    try:
        logger.info("=" * 50)
        logger.info("Starting Face Recognition Attendance System")
        logger.info("=" * 50)
        
        # Import GUI after logging is setup
        from gui.dashboard import FaceAttendanceDashboard
        import tkinter as tk
        
        logger.info("Initializing GUI...")
        
        root = tk.Tk()
        app = FaceAttendanceDashboard(root)
        
        logger.info("GUI loaded successfully")
        logger.info("Application started!")
        
        root.mainloop()
        
        logger.info("Application closed")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.critical(f"Application crashed: {e}", exc_info=True)
        print(f"Error: {e}")
        print("Check the log file for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
