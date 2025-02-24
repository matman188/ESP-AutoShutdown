import os
import logging
from datetime import datetime
import sys

from utils import auto_exit

class Logger:
    """Handles logger initialization and configuration."""
    
    def __init__(self, config):
        self.config = config
        self.logger = None
        self.setup_logger()

    def setup_logger(self):
        """Sets up logger and stores logs in the 'logs' folder."""
        try:
            # Get the script directory
            # Check if running as a frozen executable
            if getattr(sys, 'frozen', False):
                # Running as a bundled executable
                script_dir = os.path.dirname(sys.executable)  # Get directory of the executable
            else:
                # Running as a script
                script_dir = os.path.dirname(os.path.abspath(__file__))

            log_dir = os.path.join(script_dir, "logs")
            os.makedirs(log_dir, exist_ok=True)

            # Create a log file with the current date
            today = datetime.today().strftime("%Y%m%d")
            log_file_path = os.path.join(log_dir, f"esp_{today}.log")
            
            # Create a logger
            self.logger = logging.getLogger('my_logger')

            # Set the log level based on the config
            log_level = self.config.get("log_level", "INFO").upper()
            if log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
                log_level = "INFO"
            self.logger.setLevel(getattr(logging, log_level, logging.INFO))

            # Create a file handler to log to the file
            file_handler = logging.FileHandler(log_file_path)
            file_handler.setLevel(logging.DEBUG)

            # Create a stream handler to log to the console
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)

            # Create a formatter and set it for both handlers
            file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(file_formatter)

            console_formatter = logging.Formatter('%(levelname)s - %(message)s')
            console_handler.setFormatter(console_formatter)

            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

            print(f"Logger set up successfully at log path: {log_file_path}")

        except Exception as e:
            print(f"Error setting up logger: {e}")
            auto_exit()

    def get_logger(self):
        """Returns the configured logger instance."""
        return self.logger
