import threading
import sys
import os

def load_config():
    try:
        """Loads configuration at startup, ensuring it finds the correct config file location."""
        
        # Import inside function to fix issue with circular import.
        from config_reader import ConfigReader, CONFIG

        if getattr(sys, 'frozen', False):
            # Running as a compiled .exe
            script_dir = os.path.dirname(sys.executable)
        else:
            # Running as a script
            script_dir = os.path.dirname(os.path.abspath(__file__))

        config_path = os.path.join(script_dir, "config.config")
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        ConfigReader(config_path)  # Assuming ConfigReader loads the config
        
        return CONFIG  # Return loaded config
    except Exception as e:
        print(f"Error loading config: {e}")
        auto_exit()

def auto_exit():
    # Automatically Exit after 30 seconds of no input.
    timer = threading.Timer(30, sys.exit, args=[1])
    timer.start()

    input("Application will close in 30 seconds. Press Enter Key to exit manually...")

    timer.cancel()  
    sys.exit(1)