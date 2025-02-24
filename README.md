# OVERVIEW:

The purpose of this application is to check if for any upcoming load shedding within your area, and automatically shut down your PC should it detect load shedding.

By running this application as a Scheduled Job, you could automatically shut down your machine before load shedding commences.


## REQUIREMENTS/COMPATIBILITY:

This application is compatible with <b>Windows 10</b> and higher.

## API SETUP:
### ESP SIGNUP:

To use the EskomSePush API, you need to sign up to the API in order to obtain your API Token, and your Area ID.

Sign up:
https://eskomsepush.gumroad.com/l/api

Once you sign up, you will receive an API Token, save this as you will need it.

### OBTAIN AREA ID:

Using the below guide and an application such as POSTMAN, you can obtain your Area ID.

The ID will look something like: "capetown-5-claremont"

API Guide:
https://documenter.getpostman.com/view/1296288/UzQuNk3E

You will need to use the "GET Areas Search (Text)" command to obtain your area ID.

###  UPDATE CONFIG FILE:

Once you have your Area ID and Token, you must configure the "config.config" file.

Below is an example of how it may look:

area_id = capetown-5-claremont<br/>
api_token = xxxxxxxxx-xxxxxxxxx-xxxxxxxx-xxxxxxxx<br/>
debug_mode = false<br/>
log_level = INFO<br/>
keep_days = 30<br/>
check_ahead_min = 30<br/>

area_id: Unique identifier for the area<br/>
api_token: API authentication token (Keep this secure)<br/>
debug_mode: Debug mode to prevent shutdown while testing (true/false)<br/>
log_level: Log Level (DEBUG/INFO/WARNING/ERROR/CRITICAL)<br/>
keep_days: Number of days to retain logs before deletion (Default: 30)<br/>
check_ahead_min: How many minutes ahead to check for scheduled Load Shedding (Default: 30)<br/>

Save the config file

----------------------------------------------------------

Your setup is now complete.
