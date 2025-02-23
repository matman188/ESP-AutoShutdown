import os
import logging
from datetime import datetime

class Logger:
    """Handles logger initialization and configuration."""
    
    def __init__(self, config):
        self.config = config
        self.logger = None
        self.setup_logger()

    def setup_logger(self):
        """Sets up logger and stores logs in the 'logs' folder."""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))  
            log_dir = os.path.join(script_dir, "logs")
            os.makedirs(log_dir, exist_ok=True)

            today = datetime.today().strftime("%Y%m%d")
            log_file_path = os.path.join(log_dir, f"esp_{today}.log")

            self.logger = logging.getLogger('my_logger')

            log_level = self.config.get("log_level", "INFO").upper()
            if log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
                log_level = "INFO"

            self.logger.setLevel(getattr(logging, log_level, logging.INFO))

            file_handler = logging.FileHandler(log_file_path)
            file_handler.setLevel(logging.DEBUG)

            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)

            self.logger.addHandler(file_handler)

            self.logger.info(f"Logger set up successfully at log path: {log_file_path}")

        except Exception as e:
            print(f"Error setting up logger: {e}")
            exit(1)

    def get_logger(self):
        """Returns the configured logger instance."""
        return self.logger
