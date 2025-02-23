-------------------------------------------------------------------------
PURPOSE:
-------------------------------------------------------------------------

The Purpose of the script is to check at the 45 min mark on every hour whether there is load shedding in the next 20 minutes.
If it detects load shedding will occur, a command is run to the OS to shutdown.

This is built for a Windows Machine.

Shutdown command is given with 30 seconds grace for processes to end. After 30 seconds any processes stopping shutdown will be forced to close.

This is done with a python script using the EskomSePush API and the Windows Task Scheduler.

---------------------------------------------------------------------
REQUIREMENTS:
-------------------------------------------------------------------------

Firstly, make sure Python is installed on Windows and that the python "Requests" library is installed.

To install Python, the easiest method is to go to MS Store and install the latest Python version (example to date is "Python 3.11")

To install the "Requests" Python library, run the below command in cmd with admin privileges.

pip install requests

--------------------------------------------------------------------
API SIGNUP:
-------------------------------------------------------------------------

To use the EskomSePush API, you need to sign up to the API in order to obtain your API Token, and your Area ID.

Sign up:
https://eskomsepush.gumroad.com/l/api

Once you sign up, you will receive an API Token, save this as you will need it.

-----------------------------------------------------------------------------
OBTAIN AREA ID AND UPDATE CONFIG FILE:
-------------------------------------------------------------------------

Using the below guide and an application such as POSTMAN, you can obtain your Area ID.

The ID will look something like: "capetown-5-claremont"

API Guide:
https://documenter.getpostman.com/view/1296288/UzQuNk3E

You will need to use the "GET Areas Search (Text)" command to obtain your area ID.

Once you have your Area ID and Token, you must configure the "esp.config" file.

api_url=

api_token=<API Token>
config_path=<path to write logs>

example of API URL would be https://developer.sepush.co.za/business/2.0/area?id=capetown-5-claremont

Save the config file

------------------------------------------------------------------------------
MOVE FILES TO DIRECTORY:
-------------------------------------------------------------------------

Move the config and python file to the below directory. (Note that folder names need to be exact)

C:\Scripts\LoadSheddingAutoRestart\

------------------------------------------------------------------------------
SET UP TASK SCHEDULE:
-------------------------------------------------------------------------

Set up a Windows TASK SCHEDULER with the below settings: 
If setting is not mentioned, leave as default unless you suspect you need it.

GENERAL:
Name: LoadSheddingShutDown

Run with highest privileges: TRUE


TRIGGERS:
Add a Trigger for each hour of the day at 45 min mark (00:45, 01:45... , 23:45)

Set each trigger to re-occur evert 1 days


ACTIONS:
Action: Start a program

Program/Script: C:\Users\<user>\AppData\Local\Microsoft\WindowsApps\python3.exe
(Note: this location assumes you installed from the microsoft store. python.exe location may be different on your machine)

Add Arguments: C:\Scripts\LoadSheddingAutoRestart\LoadSheddingAutoRestart.py


SETTINGS:
Run Task as if a scheduled start is missed: FALSE

Recommend setting "Do Not Start a new Instance" if the task is already running.

Any other settings can be changed as required.

----------------------------------------------------------------------------------

Set up is now complete.
You can run task manually to confirm it works (Assuming you have upcoming load shedding in next 15 - 20 minutes)
