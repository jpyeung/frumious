from __future__ import print_function
import getopt
import httplib2
import os
import re
import time
import string
import sys

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from slackclient import SlackClient

# Remember to run the following:
# py -m pip install --upgrade slackclient
# py -m pip install --upgrade google-api-python-client

# Required files:
#   slack_token.txt (for Slack API), client_secret.json (for Google Drive/Sheets API)

def usage():
    print("Usage: python3 quickstart.py -f [folderId] -s [spreadsheetId]\n"+
        "\t-f, --folder: the folder id where new spreadsheets should be created\n"+
        "\t-s, --spreadsheet: the spreadsheet id of the master sheet to be parsed\n"+
        "\t-h, --help: display this usage message"
)

# Initialization stuff
f = open('slack_token.txt', 'r')
slack_token = f.read()
sc = SlackClient(slack_token)
try:
    opts, args = getopt.getopt(sys.argv[1:], "hf:s:", ["help","folder=", "spreadsheet="])
except (getopt.GetoptError) as err:
    # print help information and exit:
    print(str(err))  # will print something like "option -a not recognized"
    usage()
    sys.exit(2)
folderId = None
spreadsheetId = None
for o, a in opts:
    if o in ("-h", "--help"):
        usage()
        sys.exit()
    elif o in ("-f", "--folder"):
        folderId = a
    elif o in ("-s", "--spreadsheet"):
        spreadsheetId = a
    else:
        assert False, "unhandled option"
if not folderId:
    print("-f was not given")
    usage()
    sys.exit(2)
if not spreadsheetId:
    print("-s was not given")
    usage()
    sys.exit(2)

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets https://www.googleapis.com/auth/drive.file'
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

def set_spreadsheet_title(spreadsheet_id, title):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)
    requests = []
    # Change the spreadsheet's title
    requests.append({
        'updateSpreadsheetProperties': {
            'properties': {
                'title': title
            },
            'fields': 'title'
        }
    })

    body = {
        'requests': requests
    }
    response = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id,
                                                   body=body).execute()
    return response

def create_puzzle_spreadsheet(puzzle):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('drive', 'v3', http=http)
    file_metadata = {
        'name': puzzle,
        'mimeType': 'application/vnd.google-apps.spreadsheet',
        'parents': [folderId],
    }
    file = service.files().create(body=file_metadata,
                                    fields='id').execute()
    return file.get('id')

def update_spreadsheet_link(rangeName,puzzleSpreadsheetId):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)
    link = "https://docs.google.com/spreadsheets/d/"+puzzleSpreadsheetId+"/edit"
    values = [
        [link],
    ]
    body = {
      'values': values
    }
    valueInputOption = 'RAW'
    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheetId, range=rangeName,
        valueInputOption=valueInputOption, body=body).execute()
    return result

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
            # Range of values we care about here
            headerRange = 'Sheet1!A1:1'
            header = service.spreadsheets().values().get(
                spreadsheetId=spreadsheetId, range=headerRange).execute()
            columns = header.get('values', [])[0]
            rangeName = 'Sheet1!A2:Z'
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheetId, range=rangeName).execute()
            values = result.get('values', [])

            if not values:
                print('No data found.')
            else:
                print('Puzzle, Status, Answer:')
                rownum = 1
                puzzleIndex = columns.index('Puzzle')
                statusIndex = columns.index('Status')
                answerIndex = columns.index('Answer')
                puzzleLinkIndex = columns.index('Puzzle Link')
                spreadsheetLinkIndex = columns.index('Spreadsheet Link')
                for row in values:
                    rownum += 1
                    row.extend(['']*(5-len(row)))
                    puzzle = row[puzzleIndex]
                    status = row[statusIndex]
                    answer = row[answerIndex]
                    puzzleLink = row[puzzleLinkIndex]
                    spreadsheetLink = row[spreadsheetLinkIndex]

                    # If nothing in the puzzle column, skip to the next row
                    if not puzzle:
                        continue

                    # Create the slack channel name (spaces -> hyphens, remove other chars, shorten to 21 chars)
                    print('%s, %s, %s' % (puzzle, status, answer))
                    shortPuzzle = re.sub(r' ', '-', puzzle)
                    shortPuzzle = re.sub(r'[^a-zA-Z0-9_-]', '', shortPuzzle)[:21]
                    shortPuzzle = shortPuzzle.lower()

                    # Join the channel, or create it if it doesn't exist
                    join_response = sc.api_call(
                        "channels.join",
                        name=shortPuzzle
                    )

                    # Grab spreadsheet ID from spreadsheet link column
                    puzzleSpreadsheetId = ''
                    if spreadsheetLink:
                        matchObj = re.match(r'.*/d/(\w+)/.*', spreadsheetLink)
                        if matchObj:
                            puzzleSpreadsheetId = matchObj.group(1)
                    else:
                        puzzleSpreadsheetId = create_puzzle_spreadsheet(puzzle)
                        update_spreadsheet_link('E'+str(rownum), puzzleSpreadsheetId)

                    # Get list of Slack channels and pull channel ids
                    channels = list_channels()
                    channel_ids = {}
                    if channels:
                        for c in channels:
                            channel_ids[c['name']] = c['id']
                    else:
                        print("Unable to authenticate.")

                    # If not yet solved, unarchive the channel and set the title of the spreadsheet to the puzzle name
                    if status.lower() != 'solved':
                        unarchive_response = sc.api_call(
                            "channels.unarchive",
                            channel=channel_ids[shortPuzzle]
                        )
                        if puzzleSpreadsheetId:
                            set_title_response = set_spreadsheet_title(puzzleSpreadsheetId, puzzle)
                    # If solved, archive the channel and set the title to [SOLVED] puzzlename - answer
                    else:
                        archive_response = sc.api_call(
                            "channels.archive",
                            channel=channel_ids[shortPuzzle]
                        )
                        if puzzleSpreadsheetId:
                            set_title_response = set_spreadsheet_title(puzzleSpreadsheetId, '[SOLVED] '+puzzle+' - '+answer)

                    channel_info = sc.api_call(
                        "channels.info",
                        channel=channel_ids[shortPuzzle],
                    )
                    # Set the purpose of the channel to be the the puzzle link
                    if channel_info['channel']['purpose']['value'] != puzzleLink:
                        purpose_response = sc.api_call(
                            "channels.setPurpose",
                            channel=channel_ids[shortPuzzle],
                            purpose=puzzleLink
                        )
                    # Set the topic of the channel to be the spreadsheet link
                    if channel_info['channel']['topic']['value'] != spreadsheetLink:
                        topic_response = sc.api_call(
                            "channels.setTopic",
                            channel=channel_ids[shortPuzzle],
                            topic=spreadsheetLink
                        )

            # Set refresh time here in seconds
            time.sleep(10)
    else:
        print("Connection Failed, invalid token?")

if __name__ == '__main__':
    main()
