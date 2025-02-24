import os
import sys

CONFIG = {}  # Stores config values globally

class ConfigReader:
    """Reads key-value config file and stores data in CONFIG."""
    
    def __init__(self, file_path):
        self.read_config(file_path)

    def read_config(self, file_path):
        """Reads config file and stores each key as a key-value pair in CONFIG."""
        global CONFIG

        try:
            with open(file_path, 'r') as config_file:
                for line in config_file:
                    line = line.strip()  # Remove leading/trailing whitespaces

                    if not line or line.startswith("#"):
                        continue
                    
                    if line.startswith("[") and line.endswith("]"):
                        continue  # Ignore section headers
                    
                    if '=' in line:
                        key, value = line.split('=', 1)
                        CONFIG[key.strip()] = value.strip()

        except FileNotFoundError:
            print("Config file not found! Please ensure the file exists.")
            print("Press any key to exit...")
            input()
            exit(1)
        except Exception as e:
            print(f"Failed to load config file: {e}")
            print("Press any key to exit...")
            input()
            exit(1)

def load_config():
    """Loads configuration at startup, ensuring it finds the correct config file location."""
    
    if getattr(sys, 'frozen', False):
        # Running as a compiled .exe
        script_dir = os.path.dirname(sys.executable)
    else:
        # Running as a script
        script_dir = os.path.dirname(os.path.abspath(__file__))

    config_path = os.path.join(script_dir, "esp_auto_shutdown.config")
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    ConfigReader(config_path)  # Assuming ConfigReader loads the config
    
    return CONFIG  # Return loaded config
