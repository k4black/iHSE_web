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


def update():
    """Update cached version of Google Sheets
    Download it from online table

    """

    # TODO: Update cache

    pass


# TODO: Max Optimize gsheet api
# TODO: Max Refactoring and comment
# TODO: Check post by position - if 2 write in one time


""" ---===---==========================================---===--- """
"""            Main functions for gsheets interaction            """
""" ---===---==========================================---===--- """


def get(token_path: str, sheet_id: str, list_name: str, list_range: str) -> list:
    """Generic function for getting values from Google Sheets

    Args:
        token_path - absolute path to token file
        sheet_id - id of Google Spreadsheet
        list_name - name of list of Google Spreadsheet
        list_range - range of values requested
        
    Return:
        values - list of values requested
        
    """
    
    token = open(token_path, "rb")
    creds = pickle.load(token)
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    range_ = list_name + "!" + list_range
    request = sheet.values().get(spreadsheetId=sheet_id, range=range_)
    result = request.execute()
    values = result.get('values', [])
    
    return values


def post(token_path: str, sheet_id: str, list_name: str, list_range: str, values: list):
    """Generic function for saving values to Google Sheets

    Args:
        token_path - absolute path to token file
        sheet_id - id of Google Spreadsheet
        list_name - name of list of Google Spreadsheet
        list_range - range of values requested
        values - values to save to the given range
        
    """

    token = open(token_path, "rb")
    creds = pickle.load(token)
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    range_ = list_name + "!" + list_range
    data = {"values": values, "range": range_}
    body = {"valueInputOption": "RAW", "data": data}
    request = sheet.values().batchUpdate(spreadsheetId=sheet_id, body=body)
    response = request.execute()

    return response


""" ---===---==========================================---===--- """
"""       Google Sheets interaction via generic GSheetsAPI       """
""" ---===---==========================================---===--- """


def get_day(day: str) -> list:
    """ Gets timetable from Google Sheets and returns it in pseudo-json format

    Args:
        day: has to be same as sheet in GSheets
        
    Return:
        timetable of the corresponding day in pseudo-json
        
    """

    # TODO: waiting for Serova to get real day, not template
    # If modifying these scopes, delete the file token.pickle.
    # SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    token = '/home/ubuntu/iHSE_web/backend/token.pickle'
    id_ = '1pRvEClStcVUe9TG3hRgBTJ-43zqbESOPDZvgdhRgPlI'
    # TODO: MAX J32 -just for sometime, may be other
    values = get(token, id_, 'Template', 'A1:J32')

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
                    timetable[-1]['events'][pos]['id'] = 42  # TODO: See above
            elif titleplus == 2:
                for pos, index in enumerate(mask):
                    timetable[-1]['events'][pos]['loc'] = line[index]
            titleplus += 1

    return timetable


def save_feedback(user_obj: tuple, day: str, feedback_data: dict) -> bool:
    # TODO: save to day, not to default position
    # TODO: check GSheetsAPI how to track success
    """ Save feedback of user in google sheets
    Create new user if it does not exist
    Save in table name, phone and team

    Args:
        user_obj: User object (id, type, phone, name, pass, team)
        day: num of the day 'DD.MM'
        feedback_data: feedback in the following format
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
    Return:
        state: success or not
        
    """
    
    token = '/home/ubuntu/iHSE_web/backend/token.pickle'
    id_ = '1pRvEClStcVUe9TG3hRgBTJ-43zqbESOPDZvgdhRgPlI'

    position = get(token, id_, "Feedback", "A1")[0][0]

    print(position)

    range_ = "A" + position + ":H" + str(int(position) + 2)
    values = [[user_obj[3], user_obj[2], user_obj[5], feedback_data['overall'], feedback_data['user1'], feedback_data['event1'], feedback_data['event2'], feedback_data['event3']],
              ['', '', '', '', feedback_data['user2'], feedback_data['event1_text'], feedback_data['event2_text'], feedback_data['event3_text']],
              ['', '', '', '', feedback_data['user3']]]
    response = post(token, id_, "Feedback", range_, values)
    # print('{0} cells updated.'.format(write_response.get('updatedCells')))

    response = post(token, id_, "Feedback", "A1", [[int(position) + 3]])
    # print('{0} cells updated.'.format(update_response.get('updatedCells')))

    return True


# TODO: Max generate reg codes
def generate_codes(users, hosts, admins):
    """ Generate registration codes to google sheets
    Each code is a 6-characters-number-letter code

    Args:
        users: number of codes for this type of users
        hosts: number of codes for this type of users
        admins: number of codes for this type of users
        
    """
    
    codes = generate_registration_codes(users, 0)
    codes = generate_registration_codes(hosts, 1)
    codes = generate_registration_codes(admins, 2)
    
    pass


def check_code(code: str):
    """ Check registration code in Google Sheets
    Get user type according this code

    Args:
        code: special code hash which will be responsible for
                    the user type and permission to register


    Return:
        type: type of user, int or None if registration rejected
    
    """
    
    token = '/home/ubuntu/iHSE_web/backend/token.pickle'
    id_ = '1pRvEClStcVUe9TG3hRgBTJ-43zqbESOPDZvgdhRgPlI'
    read_values = get(token, id_, "Codes", "A5:C9")

    reg_allowed = False
    user_type = -1
    for index, code_line in enumerate(read_values, start=5):
        if code_line[0] == code and code_line[2] == '0':
            user_type = int(code_line[1])

            update_response = post(token, id_,
                                           "Codes",
                                           "C" + str(index),
                                           [[1]])
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
        (title, [event1, event2, event3] )  #  TODO not now: or None if already done

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

    token = '/home/ubuntu/iHSE_web/backend/token.pickle'
    id_ = '1pRvEClStcVUe9TG3hRgBTJ-43zqbESOPDZvgdhRgPlI'
    position = get(token, id_, "Projects", "A1")[0][0]

    read_values = get(token,
                              id_,
                              "Projects",
                              "A4:E" + str(int(position)-1))

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
    """ Save list of registered users to google sheets

    Args:
        users_list: User objects - list [ (id, type, phone, name, pass, team, credits, avatar), ....]

    Returns:
        none

    """

    token = '/home/ubuntu/iHSE_web/backend/token.pickle'
    id_ = '1pRvEClStcVUe9TG3hRgBTJ-43zqbESOPDZvgdhRgPlI'

    position = get(token, id_, "Users", "A1")[0][0]
    for i in range(len(users_list)):
        data = [[users_list[i][0],
                            users_list[i][1],
                            users_list[i][2],
                            users_list[i][3],
                            users_list[i][4],
                            users_list[i][5],
                            users_list[i][6],
                            users_list[i][7]]]
        write_response = post(token,
                                      id_,
                                      "Users",
                                      "A" + str(5+i) + ":I" + str(5+i),
                                      data)

    response = post(token,
                            id_,
                            "Users",
                            "A1",
                            [[int(position) + len(users_list)]])


def get_users():
    """ Get list of users form google sheets

    Returns:
        state: Read users # TODO: Comment

    """

    token = '/home/ubuntu/iHSE_web/backend/token.pickle'
    id_ = '1pRvEClStcVUe9TG3hRgBTJ-43zqbESOPDZvgdhRgPlI'

    position = get(token, id_, "Users", "A1")[0][0]
    read_values = get(token, id_, "Users", "A5:H" + position)
    # print(read_values)

    return read_values


def save_project(user_obj, project_data):
    """ Save feedback of user in google sheets
    Create new user if it does not exist
    Save in table id, name, phone type and team

    Args:
        user_obj: User object - (id, type, phone, name, pass, team, credits, avatar)
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

    token = '/home/ubuntu/iHSE_web/backend/token.pickle'
    id_ = '1pRvEClStcVUe9TG3hRgBTJ-43zqbESOPDZvgdhRgPlI'
    position = get(token, id_, "Projects", "A1")[0][0]

    values = [[project_data['title'], project_data['type'], str(project_data['name']), project_data['desc'], project_data['anno']]]
    write_response = post(token,
                                  id_,
                                  "Projects",
                                  "A" + position + ":E" + position,
                                  values)
    # print('{0} cells updated.'.format(write_response.get('updatedCells')))

    # updating next writing position
    update_response = post(token,
                                   id_,
                                   "Projects",
                                   "A1",
                                   [[int(position) + 1]])
    # print('{0} cells updated.'.format(update_response.get('updatedCells')))

    return True  # TODO: check GSheetsAPI how to track success


# TODO: Max save credits
def save_credits(user_obj, event_obj):
    """ Save credits for some event of user in google sheets
    Create new user if it does not exist

    Args:
        user_obj: User object - (id, type, phone, name, pass, team, credits, avatar)
        event_obj: Event object - (id, type, title, credits)

    Returns:
        state: Success or not - bool

    """

    pass


# TODO: Max update events
def update_events():
    """ Update events with description in google sheets
    Read and parse it from days sheets and save in 'Events' sheet
    And generate id

    Note:
        If exist such event with time, date and host - update other fields
        If no event - generate with unique id

    Args:

    Returns:
        None

    """

    pass


# TODO: Max get events - optimize
def get_events():
    """ Get events from google sheets

    Args:

    Returns:
        events: description of the events - list [ (id, event_type, title, credits, total), ....
                                                 ]
    """

    token = '/home/ubuntu/iHSE_web/backend/token.pickle'
    id_ = '1pRvEClStcVUe9TG3hRgBTJ-43zqbESOPDZvgdhRgPlI'

    position = get(token, id_, "Events", "A1")[0][0]
    read_values = get(token, id_, "Events", "A5:J" + position)

    events = []
    for event_raw in read_values:
        events.append( (event_raw[0], event_raw[7], event_raw[1], event_raw[8], event_raw[9]) )

    return events
    # return [(0, 'type1', 'event 1', 20, 20), (1, 'type2', 'others one ', 100, 40), (2, 'type1', 'And more one', 10, 10)]


# TODO: Max get event - optimize
def get_event(event_id):
    """ Get event with description from google sheets
    Return full description

    Args:
        event_id: Event id

    Returns:
        event: description of the event - (id, title, time, date, location, host, descriptiom, type, credits, total), ....

    """

    token = '/home/ubuntu/iHSE_web/backend/token.pickle'
    id_ = '1pRvEClStcVUe9TG3hRgBTJ-43zqbESOPDZvgdhRgPlI'

    position = get(token, id_, "Events", "A1")[0][0]
    read_values = get(token, id_, "Events", "A5:J" + position)

    for event_raw in read_values:  # Found event by id
        if event_raw[0] == event_id:
            return event_raw

    return None
    # return (32, "title", "time", "date", "location", "host", "descriptiom", "type", 300,  24)


# TODO: Max get credits chart - optimize
def get_credits(user_obj):
    """ Get credits data from google sheets

    Args:
        user_obj: User object - (id, type, phone, name, pass, team, credits, avatar)

    Returns:
        credits: credits data -  {'total': 123, 'data': [1, 2, 4, 3, ...]}

    """

    token = '/home/ubuntu/iHSE_web/backend/token.pickle'
    id_ = '1pRvEClStcVUe9TG3hRgBTJ-43zqbESOPDZvgdhRgPlI'

    position = get(token, id_, "Users", "A1")[0][0]
    read_values = get(token, id_, "Users", "A5:W" + position)

    for user_raw in read_values:  # Found user by id
        if user_raw[0] == user_obj[0]:
            print('Get credits for user: ', user_raw)

            data = {}
            data['total'] = user_raw[6]

            if user_raw[6] == 0:
                data['data'] = []
            else:
                data['data'] = user_raw[10:len(user_raw)]

            return data

    return None
    # return {'total': 122, 'data': [30, 41, 35, 51, 49, 62, 69, 83, 36, 84, 90, 20, 21]}

