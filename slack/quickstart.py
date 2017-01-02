from __future__ import print_function
import httplib2
import os
import re
import time
import string

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from slackclient import SlackClient

# Remember to run the following:
# py -m pip install --upgrade slackclient
# py -m pip install --upgrade google-api-python-client

f = open('slack_token.txt', 'r')
slack_token = f.read()
sc = SlackClient(slack_token)

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def list_channels():
    channels_call = sc.api_call(
        "channels.list"
    )
    if channels_call.get('ok'):
        return channels_call['channels']
    return None

def main():

    if sc.rtm_connect():
        while True:
            """Shows basic usage of the Sheets API.

            Creates a Sheets API service object at the spreadsheetId below:
            https://docs.google.com/spreadsheets/d/1ax8w39o93QaOkRGZCPe_hEqdpZTkmNdDIo6fw3dHoqk/edit
            """
            credentials = get_credentials()
            http = credentials.authorize(httplib2.Http())
            discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                            'version=v4')
            service = discovery.build('sheets', 'v4', http=http,
                                      discoveryServiceUrl=discoveryUrl)
            # Spreadsheet ID here
            spreadsheetId = '1ax8w39o93QaOkRGZCPe_hEqdpZTkmNdDIo6fw3dHoqk'
            # Range of values we care about here
            headerRange = 'Sheet1!A1:E1'
            rangeName = 'Sheet1!A2:E'
            header = service.spreadsheets().values().get(
                spreadsheetId=spreadsheetId, range=headerRange).execute()
            columns = header.get('values', [])
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheetId, range=rangeName).execute()
            values = result.get('values', [])

            # Slack stuff
            channels = list_channels()
            channel_ids = {}
            if channels:
                print("Channels: ")
                for c in channels:
                    channel_ids[c['name']] = c['id']
                    # print(c['name'] + " (" + c['id'] + ")")
                print(channel_ids)
            else:
                print("Unable to authenticate.")
            # print(channel_names)

            if not values:
                print('No data found.')
            else:
                print(', '.join([str(i) for i in columns]) + ':')
                for row in values:
                    row.extend(['']*(7-len(row)))
                    puzzle = row[0]
                    meta = row[1]
                    status = row[2]
                    answer = row[3]
                    guesses = row[4]
                    puzzleLink = row[5]
                    spreadsheetLink = row[6]
                    print('%s, %s, %s' % (puzzle, status, answer))
                    join_response = sc.api_call(
                        "channels.join",
                        name=puzzle
                    )
                    # print(join_response)
                    if status.lower() != 'solved':
                        unarchive_response = sc.api_call(
                            "channels.unarchive",
                            channel=channel_ids[puzzle]
                        )
                        # print(unarchive_response)
                    else:
                        archive_response = sc.api_call(
                            "channels.archive",
                            channel=channel_ids[puzzle]
                        )
                    purpose_response = sc.api_call(
                        "channels.setPurpose",
                        channel=channel_ids[puzzle],
                        purpose=puzzleLink
                    )
                    topic_response = sc.api_call(
                        "channels.setTopic",
                        channel=channel_ids[puzzle],
                        topic=spreadsheetLink
                    )

            time.sleep(30)
    else:
        print("Connection Failed, invalid token?")

if __name__ == '__main__':
    main()
