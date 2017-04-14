# toggl-to-gcal
A simple script for uploading Toggl entries into a Google calendar.

## Requirements

- Python 3
- Toggl account
  - you need the API token from My Profile 
- Google account
- Google calendar
  - you need to get Calendar Address of the calendar from the settings of the calendar
- Google project with OAuth 2.0 client ID
  - https://developers.google.com/google-apps/calendar/quickstart/python#prerequisites
  - you need the client_secret.json file

1. Set the timezone in config.py
2. Enter the Toggl token and Calendar address
3. Cope the client_secret.json file to the folder with the script
4. run python3 toggl-to-gcal.py YYYY-MM-DD to copy the entriens from Toggl to Google Calendar

## Edited by livekn

1. use config.py
2. remove client

config.py demo:

```python
class config(object):
	timezone = '+08'
	api_token = 'FILL HERE'
	calendar_id = 'FILL HERE'
```
