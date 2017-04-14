'''
Based on Google example

uploads entries to the google calendar

https://developers.google.com/google-apps/calendar/quickstart/python


Tomas Barton, tommz9@gmail.com
'''

from __future__ import print_function
import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
import googleapiclient.errors
import datetime

import config as c
config = c.config()

import argparse

SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    credential_path = 'calendar-credential.json'

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args([])
        credentials = tools.run_flow(flow, store, flags)

        print('Storing credentials to ' + credential_path)
    return credentials


def entry_to_event(entry):
    event = {
        'summary': entry['description'] + ' - ' + entry['project'],
        'description': 'duration: ' + str(entry['duration']),
        'id': entry['id'],
        'start': {
            'dateTime': entry['start']
        },
        'end': {
            'dateTime': entry['stop']
        }
    }
    return event


def push_entries(entries, calendar_id):
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    for entry in entries:
        event = entry_to_event(entry)
        print(event)
        try:
            event = service.events().insert(calendarId=calendar_id, body=event).execute()
            print('Event created: {}'.format(event.get('htmlLink')))
        except googleapiclient.errors.HttpError:
            print('Error while pushing entry #{}'.format(entry['id']))


if __name__ == '__main__':
    test_data = [
        {'description': 'sensors',
         'duration': 13686,
         'id': 356980409,
         'project': 'Others',
         'start': '2017-04-16T13:49:24+00:00',
         'stop': '2017-04-16T17:37:30+00:00'},
        {'description': '',
         'duration': 6974,
         'id': 357027440,
         'project': 'Climbing',
         'start': '2017-04-16T22:00:35+00:00',
         'stop': '2017-04-16T23:56:49+00:00'}]

    push_entries(test_data, config.calendar_id)
