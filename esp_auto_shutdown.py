import requests
from datetime import datetime, timedelta
import os

from utils import load_config, auto_exit
from logger import Logger
from log_cleaner import LogCleaner

# Load configurations
CONFIG = load_config()

# Setup logger
logger_setup = Logger(CONFIG)
LOGGER = logger_setup.get_logger()

# Clean old logs
log_cleaner = LogCleaner(CONFIG, LOGGER)
log_cleaner.clean_old_logs()

def shutdown():
    """Shutdown the computer in 30 seconds"""
    debug_mode = CONFIG.get("debug_mode", "false").lower()

    if debug_mode == "true":
        LOGGER.info("Debug mode is enabled. Shutdown will not be initiated.")
    else:
        LOGGER.info("Shutdown request will be initiated in 30 seconds")
        os.system('shutdown /s /t 30')

def get_highest_stage(events_data, minutes_ahead):
    """Get the highest stage that matches the current time"""
    current_time = datetime.now() + timedelta(minutes=minutes_ahead)
    highest_stage = None

    LOGGER.info("Checking Load Shedding for Time: %s" % current_time.strftime('%Y-%m-%d %H:%M:%S'))
    LOGGER.info("Searching through schedule for upcoming load shedding events")

    for event in events_data:
        # Convert the ISO formatted datetime strings to datetime objects
        start_time = datetime.fromisoformat(event["start"]).replace(tzinfo=None)
        end_time = datetime.fromisoformat(event["end"]).replace(tzinfo=None)
        
        # Adjust the time by adding 2 hours (timedelta) to the naive datetime objects
        timezone_offset = timedelta(hours=2)
        start_time = start_time + timezone_offset
        end_time = end_time + timezone_offset

        LOGGER.debug("Looking at Schedule with StartTime: %s and End Time: %s" % (start_time.strftime('%Y-%m-%d %H:%M:%S'), end_time.strftime('%Y-%m-%d %H:%M:%S')))

        # Check if the current time falls within the start and end time of the event
        if start_time <= current_time <= end_time:
            # Get the stage number from the event note
            stage = int(event["note"].split()[1])
            LOGGER.debug(f"Stage found matching current time: Stage {stage}")

            # Check if the stage is higher than the current highest stage
            if highest_stage is None or stage > highest_stage:
                # Update the highest stage
                highest_stage = stage
                LOGGER.info(f"New highest stage found: Stage {highest_stage}")

    LOGGER.info(f"No upcoming load shedding events found.")
    return highest_stage

def check_time_ranges(schedule_data, highest_stage, minutes_ahead):
    """Check if the current time is within the time ranges of the current stage"""
    now = datetime.now() + timedelta(minutes=minutes_ahead)
    current_day = now.date()
    current_time = now.time()

    LOGGER.info(f"Checking for time ranges for current day: {current_day} and time: {current_time}")

    for day in schedule_data["days"]:
        if day['date'] == str(current_day):
            LOGGER.info(f"Schedule for current day found: {current_day}")
            
            LOGGER.info(f"Checking Times for Stage {highest_stage}")

            # Check the time ranges for the highest stage
            for time_range in day['stages'][highest_stage - 1]:
                LOGGER.debug(f"Checking Start and End Time: {time_range}")

                start_time_str, end_time_str = time_range.split("-")
                start_time = datetime.strptime(start_time_str, "%H:%M").time()
                end_time = datetime.strptime(end_time_str, "%H:%M").time()

                # **Handle cases where end_time is past midnight**
                if start_time <= end_time:
                    # Normal case (e.g., 14:00-16:30)
                    if start_time <= current_time <= end_time:
                        LOGGER.info(f"Time range for stage {highest_stage} falls in current time: {start_time} - {end_time}")
                        return True
                else:
                    # Case where the range crosses midnight (e.g., 22:00-00:30)
                    if current_time >= start_time or current_time <= end_time:
                        LOGGER.info(f"Time range for stage {highest_stage} falls in current time: {start_time} - {end_time}")
                        return True
                    
    LOGGER.info("No time range found for current time")
    return False

def main():
    """Main function to check for load shedding events and shutdown."""
    try:
        # Get the API Details from the configuration file
        e_area_id = CONFIG.get("area_id")
        e_url = f"https://developer.sepush.co.za/business/2.0/area?id={e_area_id}"
        e_headers = {'Token': CONFIG.get("api_token")}

        LOGGER.info(f"Requesting data from {e_url} with token {e_headers['Token'][:4]}**** (first 4 chars)")

        # Make the API request
        data = requests.get(url=e_url, headers=e_headers)
        
        # Check if the request was successful
        if data.status_code != 200:
            LOGGER.error(f"API request failed with status code: {data.status_code}. Response: {data.text}")
            auto_exit()
        
        # Get the JSON response
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
        highest_stage = get_highest_stage(response["events"], minutes_ahead)

        # Check if the current time falls within the time ranges of the highest stage
        if highest_stage and check_time_ranges(response["schedule"], highest_stage, minutes_ahead):
            LOGGER.info("Load shedding stage detected, initiating shutdown.")
            shutdown()

    except requests.exceptions.RequestException as e:
        if LOGGER:
            LOGGER.error(f"Error with the API request: {e}")
            auto_exit()
    except Exception as e:
        if LOGGER:
            LOGGER.error(f"An unexpected error occurred: {e}")
            auto_exit()
        else:
            print(f"An unexpected error occurred: {e}")
            auto_exit()

if __name__ == "__main__":
    main()  # Run the main function
