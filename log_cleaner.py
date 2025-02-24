import os
import time

class LogCleaner:
    """Handles cleanup of old logs based on retention period."""

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

    def clean_old_logs(self):
        """Cleans up logs older than the specified number of days."""
        try:
            self.logger.debug("Cleaning up old logs...")
            days_to_keep = int(self.config.get("keep_days", "30"))
            self.logger.debug(f"Logs will be retained for {days_to_keep} days.")

            current_time = time.time()
            script_dir = os.path.dirname(os.path.abspath(__file__))
            log_dir = os.path.join(script_dir, "logs")

            if not os.path.exists(log_dir):
                self.logger.debug("Logs directory does not exist. No logs to clean.")
                return

            retention_time = current_time - (days_to_keep * 86400)

            for log_file in os.listdir(log_dir):
                log_file_path = os.path.join(log_dir, log_file)

                if os.path.isdir(log_file_path) or not log_file.endswith(".log"):
                    continue

                file_mod_time = os.path.getmtime(log_file_path)

                if file_mod_time < retention_time:
                    os.remove(log_file_path)
                    self.logger.debug(f"Deleted old log file: {log_file_path}")
                    
        except Exception as e:
            self.logger.error(f"Error while cleaning old logs: {e}")
