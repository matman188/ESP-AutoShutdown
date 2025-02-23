import requests
from datetime import datetime, timedelta
import time
import os
import logging

# Global variables
CONFIG = {}  # Stores config values globally
LOGGER = None  # Global logger variable

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

                    # Skip empty lines or comments (lines starting with '#')
                    if not line or line.startswith("#"):
                        continue
                    
                    # Handle section headers (e.g., [general], [logging])
                    if line.startswith("[") and line.endswith("]"):
                        continue  # Ignore section headers
                    
                    # Ensure lines with '=' are processed as key=value pairs
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()  # Remove leading/trailing spaces from the key
                        value = value.strip()  # Remove leading/trailing spaces from the value
                        
                        # Store the key-value pair directly without the section prefix
                        CONFIG[key] = value

        except FileNotFoundError:
            if LOGGER:
                LOGGER.error("Config file not found! Please ensure the file exists.")
        except Exception as e:
            if LOGGER:
                LOGGER.error(f"Failed to load config file: {e}")
            exit(1)  # Exit the program if an error occurs while reading config

def load_config():
    """Loads configuration at startup and makes it globally accessible."""
    script_dir = os.path.dirname(os.path.abspath(__file__))  
    config_path = os.path.join(script_dir, "esp.config")

    # Read config file and store values in CONFIG
    ConfigReader(config_path)

def setup_logger():
    """Sets up global logger and stores logs in the 'logs' folder."""
    global LOGGER

    try:
        # Get script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))  
        log_dir = os.path.join(script_dir, "logs")  

        # Ensure logs directory exists
        os.makedirs(log_dir, exist_ok=True)

        # Log filename based on date
        today = datetime.today().strftime("%Y%m%d")
        log_file_path = os.path.join(log_dir, f"esp_{today}.log")

        # Setup logger
        LOGGER = logging.getLogger('my_logger')

        # Get the log level from the config file (default to INFO)
        log_level = CONFIG.get("log_level", "INFO").upper()

        # Ensure log level is valid
        if log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            log_level = "INFO"  # Fallback to default if invalid log level

        LOGGER.setLevel(getattr(logging, log_level, logging.INFO))  # Set log level dynamically

        # Create file handler
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(logging.DEBUG)

        # Format logs
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        # Add handler to logger
        LOGGER.addHandler(file_handler)

        LOGGER.info(f"Logger set up successfully at log path: {log_file_path}")

    except Exception as e:
        print(f"Error setting up logger: {e}")
        exit(1)  # Exit the program if logging setup fails

def clean_old_logs():
    """Cleans up logs older than the specified number of days from the 'logs' directory."""
    try:
        LOGGER.debug("Cleaning up old logs...")

        # Get the number of days to retain logs (from the config file)
        days_to_keep = int(CONFIG.get("keep_days", "30"))  # Default to 30 days if not provided
        LOGGER.debug(f"Logs will be retained for {days_to_keep} days.")
        
        # Get the current time
        current_time = time.time()
        
        # Get script directory and logs folder
        script_dir = os.path.dirname(os.path.abspath(__file__))
        log_dir = os.path.join(script_dir, "logs")
        
        # Check if log directory exists
        if not os.path.exists(log_dir):
            if LOGGER:
                LOGGER.debug("Logs directory does not exist. No logs to clean.")
            return
        
        # Get the current time in seconds (for comparison)
        retention_time = current_time - (days_to_keep * 86400)  # 86400 seconds in a day
        
        # Loop through all log files in the directory
        for log_file in os.listdir(log_dir):
            log_file_path = os.path.join(log_dir, log_file)
            
            # Skip directories and non-log files
            if os.path.isdir(log_file_path) or not log_file.endswith(".log"):
                continue
            
            # Get the last modification time of the file
            file_mod_time = os.path.getmtime(log_file_path)
            
            # If the log file is older than the retention time, delete it
            if file_mod_time < retention_time:
                os.remove(log_file_path)
                if LOGGER:
                    LOGGER.debug(f"Deleted old log file: {log_file_path}")
                
    except Exception as e:
        if LOGGER:
            LOGGER.error(f"Error while cleaning old logs: {e}")
        else:
            print(f"Error while cleaning old logs: {e}")

def shutdown():
    """Shutdown the computer in 30 seconds"""
    LOGGER.info("Shutdown request will be initiated in 30 seconds")
    #os.system('shutdown /s /t 30')

def get_highest_stage_matching_current_time(events_data, minutes_ahead):
    """Get the highest stage that matches the current time"""
    current_time = datetime.now() + timedelta(minutes=minutes_ahead)
    highest_stage = None

    LOGGER.info("Checking Load Shedding for Time: %s" % current_time.strftime('%Y-%m-%d %H:%M:%S'))
    LOGGER.info("Searching through schedule for upcoming load shedding events")

    for event in events_data:
        
        start_time = datetime.fromisoformat(event["start"]).replace(tzinfo=None)
        end_time = datetime.fromisoformat(event["end"]).replace(tzinfo=None)
        
        LOGGER.debug("Looking at Schedule with StartTime: %s and End Time: %s" % (start_time.strftime('%Y-%m-%d %H:%M:%S'), end_time.strftime('%Y-%m-%d %H:%M:%S')))

        if start_time <= current_time <= end_time:
            
            stage = int(event["note"].split()[1])
            LOGGER.debug(f"Stage found matching current time: Stage {stage}")

            if highest_stage is None or stage > highest_stage:
                highest_stage = stage
                LOGGER.info(f"New highest stage found: Stage {highest_stage}")

    LOGGER.info(f"No upcoming load shedding events found.")
    return highest_stage

def check_time_ranges_in_current_time(schedule_data, highest_stage, minutes_ahead):
    """Check if the current time is within the time ranges of the current stage"""
    now = datetime.now() + timedelta(minutes=minutes_ahead)
    current_day = now.date()
    current_time = now.time()

    LOGGER.info(f"Checking for time ranges for current day: {current_day} and time: {current_time}")

    for day in schedule_data["days"]:
        if day['date'] == str(current_day):
            LOGGER.info(f"Schedule for current day found: {current_day}")
            
            LOGGER.info(f"Checking Times for Stage {highest_stage}")

            for time_range in day['stages'][highest_stage - 1]:
                LOGGER.debug(f"Checking Start and End Time: {time_range}")

                start_time_str, end_time_str = time_range.split("-")
                start_time = datetime.strptime(start_time_str, "%H:%M").time()
                end_time = datetime.strptime(end_time_str, "%H:%M").time()

                if current_time <= end_time or current_time >= start_time:
                    if start_time <= current_time:
                        LOGGER.info(f"Time range for stage {highest_stage} falls in current time: {start_time} - {end_time}")
                        return True
                else:
                    if start_time <= current_time <= end_time:
                        LOGGER.info(f"Time range for stage falls in current time: {start_time} - {end_time}")
                        return True
                    
    LOGGER.info("No time range found for current time")
    return False

def main():
    """Main function to check for load shedding events and shutdown."""
    try:
        e_area_id = CONFIG.get("area_id")
        e_url = f"https://developer.sepush.co.za/business/2.0/area?id={e_area_id}"
        e_headers = {'Token': CONFIG.get("api_token")}

        LOGGER.info(f"Requesting data from {e_url} with token {e_headers['Token'][:4]}**** (first 4 chars)")

        data = requests.get(url=e_url, headers=e_headers)
        
        if data.status_code != 200:
            LOGGER.error(f"API request failed with status code: {data.status_code}. Response: {data.text}")
            exit(1)
         
        response = data.json()
        LOGGER.debug(f"API Status Code: {data.status_code}. Response: {response}")
        
        """
        Sample Response:
        {
            "events": [
                {
                    "end": "2025-02-23T16:30:00+02:00",
                    "note": "Stage 6",
                    "start": "2025-02-23T14:00:00+02:00"
                },
                {
                    "end": "2025-02-24T00:30:00+02:00",
                    "note": "Stage 6",
                    "start": "2025-02-23T20:00:00+02:00"
                }
            ],
            "info": {
                "name": "Kenilworth (5)",
                "region": "City of Cape Town"
            },
            "schedule": {
                "days": [
                    {
                        "date": "2025-02-23",
                        "name": "Sunday",
                        "stages": [
                            [
                                "22:00-00:30"
                            ],
                            [
                                "06:00-08:30",
                                "22:00-00:30"
                            ],
                            [
                                "06:00-08:30",
                                "22:00-00:30"
                            ]
                        ]
                    },
                    {
                        "date": "2025-02-24",
                        "name": "Monday",
                        "stages": [
                            [],
                            [
                                "14:00-16:30"
                            ],
                            [
                                "06:00-08:30",
                                "14:00-16:30"
                            ],
                            [
                                "06:00-08:30",
                                "14:00-16:30",
                                "22:00-00:30"
                            ]
                        ]
                    }
                ],
                "source": "https://www.capetown.gov.za/loadshedding/"
            }
        }
        """

        # Get the number of minutes to check ahead
        minutes_ahead = CONFIG.get("check_ahead_min")
        if minutes_ahead is None:
            minutes_ahead = 30
        else:
            minutes_ahead = int(minutes_ahead)

        LOGGER.info(f"Checking for load shedding events within the next {minutes_ahead} minutes.")

        # Get the highest matching stage
        highest_stage = get_highest_stage_matching_current_time(response["events"], minutes_ahead)

        if highest_stage and check_time_ranges_in_current_time(response, highest_stage, minutes_ahead):
            LOGGER.info("Load shedding stage detected, initiating shutdown.")
            shutdown()

    except requests.exceptions.RequestException as e:
        if LOGGER:
            LOGGER.error(f"Error with the API request: {e}")
    except Exception as e:
        if LOGGER:
            LOGGER.error(f"An unexpected error occurred: {e}")
        else:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    load_config()  # Load configuration at startup
    setup_logger()  # Set up logger
    clean_old_logs()  # Clean up old logs
    main()  # Run the main function
