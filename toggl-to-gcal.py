#!/usr/bin/python3

'''
toggl-to-gcal

A simple script for uploading Toggl entries into a Google calendar.

Requirements

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

Tomas Barton, tommz9@gmail.com

---

Add by livekn

config.py demo:

class config(object):
	timezone = '+08'
	api_token = 'FILL HERE'
	calendar_id = 'FILL HERE'

'''
import requests
from requests.auth import HTTPBasicAuth
from urllib.parse import urlencode

import config as c
config = c.config()

import pickle

import datetime
import iso8601

import sys

from gpush import push_entries

timezone = config.timezone

# Toggl
api_token = config.api_token

# Google calendar
calendar_id = config.calendar_id


def get_project_details(pid):
    url = 'https://www.toggl.com/api/v8/projects/{}'.format(pid)
    headers = {'content-type': 'application/json'}
    print('getting project from toggl')
    r = requests.get(url, headers=headers,
                     auth=HTTPBasicAuth(api_token, 'api_token'))
    return r.json()['data']

def get_entries(day):
    '''
    Get the list of entries for one particular day from Toggl
    '''

    url = 'https://www.toggl.com/api/v8/time_entries'
    headers = {'content-type': 'application/json'}

    isoday_start = day + 'T00' + timezone
    isoday_end = day + 'T23:59:59' + timezone
    isoday_start = iso8601.parse_date(isoday_start).isoformat()
    isoday_end = iso8601.parse_date(isoday_end).isoformat()

    query = {
        'start_date': isoday_start,
        'end_date': isoday_end
    }

    url += '?' + urlencode(query)
    r = requests.get(url, headers=headers,
                     auth=HTTPBasicAuth(api_token, 'api_token'))
    return r.json()

    '''
    return demo:
    {'wid': 1234567, 'stop': '2017-04-13T09:42:29+00:00', 'duronly': False, 'id': 123456789, 'at': '2017-04-13T09:42:37+00:00', 'start': '2017-04-13T
09:24:52+00:00', 'uid': 1234567, 'pid': 12345678, 'duration': 1057, 'description': 'Hello World', 'billable': False}
    '''


class Cache:
    ''' Cache for project details. To avoid multiple queries to
    API of Toggle while translating the project id to name.

    Can be serialized to file and used in the following runs
    '''

    def __init__(self, file='cache'):

        self.cache_file = file

        # try to load the cache from a file
        try:
            with open(file, 'rb') as f:
                self.projects = pickle.load(f)
        except (FileNotFoundError, pickle.PickleError):
            # Just reset the cache
            self.projects = {}

    def get_project(self, pid):
        try:
            project = self.projects[pid]
        except KeyError:
            project = get_project_details(pid)
            self.projects[pid] = project

        return project

    def serialize(self):
        with open(self.cache_file, 'wb') as f:
            pickle.dump((self.projects), f)


def decode_entries(entries, cache):
    ''' 
    Translates Toggl entry to a more readable format
    '''
    decoded = []
    for entry in entries:
        e = {}
        e['id'] = entry['id']
        e['start'] = entry['start']
        e['stop'] = entry['stop']
        e['duration'] = entry['duration']

        try:
            e['description'] = entry['description']
        except KeyError:
            e['description'] = ''

        if entry.get('pid'):
             project = cache.get_project(entry['pid'])
             e['project'] = project['name']
        else:
            e['project'] = ""

        decoded.append(e)
    return decoded

if __name__ == '__main__':

	# Tak one parameter - the day which will be processed
    if len(sys.argv) != 2:
        print('The first argument is a date with YYY-MM-DD format')
        sys.exit(1)

    # Get the entries for one day from Toggl
    entries = get_entries(sys.argv[1])

    # Cache saves the project and client descriptions to disk
    cache = Cache()

    # Replace project id and client id with the names
    entries = decode_entries(entries, cache)

    # Save updated cache to the disk
    cache.serialize()

    # Send events to the calendar
    push_entries(entries, calendar_id)
