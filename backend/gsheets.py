import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import random


""" ---===---==========================================---===--- """
"""          Auxiliary functions for gsheets interaction         """
""" ---===---==========================================---===--- """


def generate_registration_codes(num, type=0):
    """ Generate registration codes by number
    Each code is a 6-characters-number-letter code

    Args:
        num: Number of codes
        type: Type of user [0, 1, 2, 3]

    Returns:
        Codes: 6-characters-number-letter code - list [string, ...]

    """

    # string.ascii_uppercase
    symbols = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" + "0123456789" + "0123456789" + "0123456789"
    random.seed(0)
    symbols = ''.join(random.sample(symbols, len(symbols)))
    size = len(symbols)

    rez = []

    for i in range(num):
        code = symbols[random.randint(0, size-1)] + \
               symbols[random.randint(0, size-1)] + \
               symbols[i // size] + \
               symbols[i % size] + \
               symbols[i*i % size] + \
               symbols[( type % (size//5) + 1 ) * random.randint(0, size//5)]

        rez.append(code)

    return rez


# TODO: Max Optimize gsheet api
# TODO: Max Refactoring and comment
def api():
    pass


""" ---===---==========================================---===--- """
"""           Google Sheets interaction via GSheetsAPI           """
""" ---===---==========================================---===--- """



def get_day(day: str) -> list:
    """ Gets timetable from Google Sheets
        and returns it in pseudo-json format

    Args:
        day: calendar day, has to be same as sheet in GSheets - string

    Returns:
        timetable: timetable of the corresponding day in pseudo-json - list

    """

    # TODO waiting for Serova to get real day, not template
    # If modifying these scopes, delete the file token.pickle.
    # SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    day = 'Template'
    # The ID and range of a sample spreadsheet.
    spreadsheet_id = '1pRvEClStcVUe9TG3hRgBTJ-43zqbESOPDZvgdhRgPlI'
    spreadsheet_range = day + '!A1:J32'  # TODO: MAX J32 -just for sometime,  may be other

    # token.pickle stores the user's access and refresh tokens,
    # providing read/write access to GSheets.
    # It was actually created on local machine ( where it was created
    # automatically when the authorization flow completed for the first
    # time) and ctrl-pasted to server.
    token = open('/home/ubuntu/iHSE_web/backend/token.pickle', 'rb')
    creds = pickle.load(token)

    # Call the Sheets API
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    request = sheet.values().get(spreadsheetId=spreadsheet_id,
                                 range=spreadsheet_range)
    result = request.execute()
    values = result.get('values', [])

    # function for removing crlf from human-generated timetable
    def crlf(x):
        #y = x.replace('\n', ' - ')
        return x

    # removing \n
    for index, line in enumerate(values[2::], start=2):
        values[index] = list(map(lambda x: crlf(x), line))
    timetable = []  # resulting timetable
    mask = []  # selector for correct selection of GSheets verbose data
    titleplus = 0  # selector for correct differentiation of desc, loc, name
    for line in values[2::]:
        if line[0] != '':
            timetable.append({})
            timetable[-1]['time'] = line[0]
            timetable[-1]['events'] = []
            mask.clear()
            titleplus = 0
            for index, cell in enumerate(line[1::], start=1):
                if cell != '' and cell != '.':
                    mask.append(index)
                    timetable[-1]['events'].append({'title': cell})
        else:
            # TODO: Add correct event id
            if titleplus == 0:
                for pos, index in enumerate(mask):
                    timetable[-1]['events'][pos]['desc'] = line[index]
            elif titleplus == 1:
                for pos, index in enumerate(mask):
                    timetable[-1]['events'][pos]['host'] = line[index]
                    timetable[-1]['events'][pos]['id'] = 43  # TODO: See above
            elif titleplus == 2:
                for pos, index in enumerate(mask):
                    timetable[-1]['events'][pos]['loc'] = line[index]
            titleplus += 1

    return timetable


def save_feedback(user_obj, day, feedback_data):
    """ Save feedback of user in google sheets
    Create new user if it does not exist
    Save in table name, phone and team

    Args:
        user_obj: User object - (id, type, phone, name, pass, team)
        day: num of the day - string '16.04'
        feedback_data: Python obj of feedback - dictionary
                  {"overall": int,
                   "user1": string,
                   "user2": string,
                   "user3": string,
                   "event1": int,
                   "event2": int,
                   "event3": int,
                   "event1_text": string,
                   "event2_text": string,
                   "event3_text": string
                   }

    Returns:
        state: Success or not - bool

    """

    spreadsheet_id = '1pRvEClStcVUe9TG3hRgBTJ-43zqbESOPDZvgdhRgPlI'
    # token.pickle stores the user's access and refresh tokens,
    # providing read/write access to GSheets.
    # It was actually created on local machine ( where it was created
    # automatically when the authorization flow completed for the first
    # time) and ctrl-pasted to server.
    token = open('/home/ubuntu/iHSE_web/backend/token.pickle', 'rb')
    creds = pickle.load(token)
    service = build('sheets', 'v4', credentials=creds)

    # getting position to write to
    read_request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id,
                                                       range='Feedback!A1')
    read_response = read_request.execute()
    read_values = read_response.get('values', [])
    position = read_values[0][0]
    print(position)
    write_range = 'Feedback!A' + position + ':H' + str(int(position) + 2)

    # writing actual feedback
    data = {'values': [[user_obj[3], user_obj[2], user_obj[5],
                        feedback_data['overall'], feedback_data['user1'], feedback_data['event1'], feedback_data['event2'], feedback_data['event3']],
                       ['', '', '', '', feedback_data['user2'], feedback_data['event1_text'], feedback_data['event2_text'], feedback_data['event3_text']],
                       ['', '', '', '', feedback_data['user3']]],
            'range': write_range
            }
    body = {
        'valueInputOption': 'RAW',
        'data': data
    }
    write_request = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id,
                                                                body=body)
    write_response = write_request.execute()
    # print('{0} cells updated.'.format(write_response.get('updatedCells')))
    print('writing done')

    # updating next writing position
    update_request = service.spreadsheets().values().update(spreadsheetId=spreadsheet_id,
                                                            range='Feedback!A1',
                                                            valueInputOption='RAW',
                                                            body={'values': [[int(position) + 3]]})
    update_response = update_request.execute()
    # print('{0} cells updated.'.format(update_response.get('updatedCells')))
    print('updating done')

    return True  # TODO: check GSheetsAPI how to track success


# TODO: Max generate reg codes
def generate_codes(users, hosts, admins):
    """ Generate registration codes in google sheets
    Each code is a 6-characters-number-letter code

    Args:
        users, hosts, admins: Number  of codes for each type

    Returns:
        None

    """

    codes = generate_registration_codes(users, 0)
    codes = generate_registration_codes(hosts, 1)
    codes = generate_registration_codes(admins, 2)

    pass


def check_code(code):
    """ Check registration code in google sheets
    Get user type according this code

    Args:
        code: special code hash which will be responsible for the user type and permission to register - str


    Returns:
        type: type of user - int or None if registration allowed

    """

    spreadsheet_id = '1pRvEClStcVUe9TG3hRgBTJ-43zqbESOPDZvgdhRgPlI'
    # token.pickle stores the user's access and refresh tokens,
    # providing read/write access to GSheets.
    # It was actually created on local machine ( where it was created
    # automatically when the authorization flow completed for the first
    # time) and ctrl-pasted to server.
    token = open('/home/ubuntu/iHSE_web/backend/token.pickle', 'rb')
    creds = pickle.load(token)
    service = build('sheets', 'v4', credentials=creds)

    read_request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id,
                                                       range='Codes!A5:C9')
    read_response = read_request.execute()
    read_values = read_response.get('values', [])

    reg_allowed = False
    user_type = -1
    for index, code_line in enumerate(read_values, start=5):
        if code_line[0] == code and code_line[2] == '0':
            user_type = int(code_line[1])
            upd_range = 'Codes!C' + str(index)
            update_request = service.spreadsheets().values().update(spreadsheetId=spreadsheet_id,
                                                                    range=upd_range,
                                                                    valueInputOption='RAW',
                                                                    body={'values': [[1]]})
            update_response = update_request.execute()
            reg_allowed = True
            break

    if reg_allowed:
        return user_type
    else:
        return None


# TODO: Max get feedback
def get_feedback(day):
    """ Get description of day for feedback in google sheets
    Create new user if it does not exist
    Save in table id, name, phone type and team

    Args:
        day: num of the day - string '16.04'

    Returns:
        (title, [event1, event2, event3] )                  (TODO: not now: or None if already done)

    """

    return ('Day of the Russia', ['Event 1', 'Other event', 'And the last one'])


def get_projects(filter_obj):
    """ Get description of day for feedback in google sheets
    Create new user if it does not exist
    Save in table id, name, phone type and team

    Args:
        filter_obj: filter what we should return - (Name, type, name)   # TODO: Not now

    Returns:
        List of projects obj:
              [ {
                 "title": string,
                 "name": string,
                 "type": string,
                 "desc": string,
                 "anno": string
                 }, .........  ]

             (TODO: not now: or None if no one)
    """

    spreadsheet_id = '1pRvEClStcVUe9TG3hRgBTJ-43zqbESOPDZvgdhRgPlI'
    # token.pickle stores the user's access and refresh tokens,
    # providing read/write access to GSheets.
    # It was actually created on local machine ( where it was created
    # automatically when the authorization flow completed for the first
    # time) and ctrl-pasted to server.
    token = open('/home/ubuntu/iHSE_web/backend/token.pickle', 'rb')
    creds = pickle.load(token)
    service = build('sheets', 'v4', credentials=creds)

    # getting range to read from
    range_request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id,
                                                        range='Projects!A1')
    range_response = range_request.execute()
    range_values = range_response.get('values', [])
    position = range_values[0][0]
    read_range = 'Projects!A4:E' + str(int(position)-1)

    read_request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id,
                                                        range=read_range)
    read_response = read_request.execute()
    read_values = read_response.get('values', [])

    projects = []
    for project in read_values:
        projects.append({})
        projects[-1]['title'] = project[0]
        projects[-1]['type'] = project[1]
        projects[-1]['name'] = project[2]
        projects[-1]['desc'] = project[3]
        projects[-1]['anno'] = project[4]

    return projects


def save_users(users_list):
    """ Save list of registered users in google sheets

    Args:
        users_list: User objects - list [ (id, type, phone, name, pass, team), ....]

    Returns:
        none

    """

    spreadsheet_id = '1pRvEClStcVUe9TG3hRgBTJ-43zqbESOPDZvgdhRgPlI'
    # token.pickle stores the user's access and refresh tokens,
    # providing read/write access to GSheets.
    # It was actually created on local machine ( where it was created
    # automatically when the authorization flow completed for the first
    # time) and ctrl-pasted to server.
    token = open('/home/ubuntu/iHSE_web/backend/token.pickle', 'rb')
    creds = pickle.load(token)
    service = build('sheets', 'v4', credentials=creds)

    # getting position to write to
    read_request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id,
                                                       range='Users!A1')
    read_response = read_request.execute()
    read_values = read_response.get('values', [])
    position = read_values[0][0]

    for i in range(len(users_list)):
        write_range = 'Users!A' + str(5+i) + ':F' + str(5+i)

        data = {'values': [[users_list[i][0], users_list[i][1], users_list[i][2], users_list[i][3], users_list[i][4], users_list[i][5]]],
                'range': write_range
                }
        body = {
            'valueInputOption': 'RAW',
            'data': data
        }
        write_request = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id,
                                                                    body=body)
        write_response = write_request.execute()
        # print('{0} cells updated.'.format(write_response.get('updatedCells')))

    print('Users saved')


def get_users():
    """ Get list of users form google sheets

    Returns:
        state: Readed users # TODO: Comment

    """

    spreadsheet_id = '1pRvEClStcVUe9TG3hRgBTJ-43zqbESOPDZvgdhRgPlI'
    # token.pickle stores the user's access and refresh tokens,
    # providing read/write access to GSheets.
    # It was actually created on local machine ( where it was created
    # automatically when the authorization flow completed for the first
    # time) and ctrl-pasted to server.
    token = open('/home/ubuntu/iHSE_web/backend/token.pickle', 'rb')
    creds = pickle.load(token)
    service = build('sheets', 'v4', credentials=creds)

    read_request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id,
                                                       range='Users!A5:F15')  #TODO Max F15
    read_response = read_request.execute()
    read_values = read_response.get('values', [])

    print(read_values)

    return read_values


def save_project(user_obj, project_data):
    """ Save feedback of user in google sheets
    Create new user if it does not exist
    Save in table id, name, phone type and team

    Args:
        user_obj: User object - (id, type, phone, name, pass, team)
        project_data: Python obj of project - dictionary
                  {"title": string,
                   "name": [string, ...],
                   "type": string,
                   "desc": string,
                   "anno": string
                   }

    Returns:
        state: Success or not - bool

    """

    print('User obj:', user_obj)
    print('Project data:', project_data)

    spreadsheet_id = '1pRvEClStcVUe9TG3hRgBTJ-43zqbESOPDZvgdhRgPlI'
    # token.pickle stores the user's access and refresh tokens,
    # providing read/write access to GSheets.
    # It was actually created on local machine ( where it was created
    # automatically when the authorization flow completed for the first
    # time) and ctrl-pasted to server.
    token = open('/home/ubuntu/iHSE_web/backend/token.pickle', 'rb')
    creds = pickle.load(token)
    service = build('sheets', 'v4', credentials=creds)

    # getting position to write to
    read_request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id,
                                                       range='Projects!A1')
    read_response = read_request.execute()
    read_values = read_response.get('values', [])
    position = read_values[0][0]
    print(position)
    write_range = 'Projects!A' + position + ':E' + position

    # writing actual feedback    # TODO: Max Names by list
    data = {'values': [[project_data['title'], project_data['type'], str(project_data['name']), project_data['desc'], project_data['anno']]],
            'range': write_range
            }
    body = {
        'valueInputOption': 'RAW',
        'data': data
    }
    write_request = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id,
                                                                body=body)
    write_response = write_request.execute()
    # print('{0} cells updated.'.format(write_response.get('updatedCells')))
    print('writing done')

    # updating next writing position
    update_request = service.spreadsheets().values().update(spreadsheetId=spreadsheet_id,
                                                            range='Projects!A1',
                                                            valueInputOption='RAW',
                                                            body={'values': [[int(position) + 1]]})
    update_response = update_request.execute()
    # print('{0} cells updated.'.format(update_response.get('updatedCells')))
    print('updating done')

    return True  # TODO: check GSheetsAPI how to track success


# TODO: Max save credits
def save_credits(user_obj, event_obj):
    """ Save credits for some event of user in google sheets
    Create new user if it does not exist

    Args:
        user_obj: User object - (id, type, phone, name, pass, team)
        event_obj: Event object - (id, type, title, credits)

    Returns:
        state: Success or not - bool

    """

    pass


# TODO: Max update events
def update_events():
    """ Update events with description in google sheets
    Read and parse it from days sheets and save in 'Events' sheet

    Args:

    Returns:
        None

    """

    pass


# TODO: Max get events
def get_events():
    """ Get events from google sheets

    Args:

    Returns:
        events: description of the events - list [ (id, event_type, title, credits, total), ....
                                                 ]
    """

    return [(0, 'type1', 'event 1', 20, 20), (1, 'type2', 'othe one ', 100, 40), (2, 'type1', 'And more one', 10, 10)]


# TODO: Max get event
def get_event(id):
    """ Get event with description from google sheets
    Return full description

    Args:

    Returns:
        event: description of the event - (id, title, time, date, location, host, descriptiom, type, credits, total), ....

    """

    return (32, "title", "time", "date", "location", "host", "descriptiom", "type", 300,  24)
