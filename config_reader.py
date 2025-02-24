from utils import auto_exit

CONFIG = {}

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
            print("Config file loaded successfully.")
            
        except FileNotFoundError:
            print("Config file not found! Please ensure the file exists.")
            auto_exit()
        except Exception as e:
            print(f"Failed to load config file: {e}")
            auto_exit()