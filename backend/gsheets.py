import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json
import random


cached_data = {}  # global variable for storing parsed Spreadsheet lists
test_data = {}

# days_list = ['05.06', '06.06', '07.06', '08.06', '09.06', '10.06', '11.06',
#              '12.06', '13.06', '14.06', '15.06', '16.06', '17.06', '18.06']
days_list = ['05.06', '06.06']
# TODO: modify when Feedback List will be done by Serova

""" ---===---============================================---===--- """
"""               Functions for updating cached data               """
"""                      and local backing up                      """
""" ---===---============================================---===--- """


def update():
    """Update all cached version of Spreadsheet from online

    """

    global cached_data
    test_data['Events'] = "TEST"

    # TODO: what about reg codes?

    # for i in ['05.06', '06.06', '07.06', '08.06', '09.06', '10.06', '11.06',
    #           '12.06', '13.06', '14.06', '15.06', '16.06', '17.06', '18.06',
    #           'Events', 'Feedback', 'Projects', 'Users']:
    #     update_list(i)

    # cached_data = gcache

    for i in ['Template', 'Events', 'Feedback', 'Projects', 'Users']:
        update_cache(i)


def update_cache(name: str):
    """Update cached version of exact Spreadsheet list from online

    Args:
        name: name of list in Spreadsheet

    """

    global cached_data
    global test_data

    # if name[2] == '.':  # TODO: on release
    if name == 'Template':
        cached_data[name] = gsheets_get_day(name)

    elif name == 'Projects':
        cached_data[name] = gsheets_get_projects(None)  # TODO
        test_data[name] = 'TESTING'

    elif name == 'Feedback':
        cached_data[name] = gsheets_get_feedback()

    elif name == 'Events':
        cached_data[name] = gsheets_get_events()

    elif name == 'Users':
        cached_data[name] = gsheets_get_users()


def backup_cache(list_name: str):
    """Backing up GSheets lists as text files on disk

    Args: 
        list_name: name of Spreadsheet list to backup
    """
    spread_cache = open('/home/ubuntu/iHSE_web/backend/' + list_name + '.txt', 'w')
    spread_id = '1pRvEClStcVUe9TG3hRgBTJ-43zqbESOPDZvgdhRgPlI'
    token_file = open('/home/ubuntu/iHSE_web/backend/token.pickle', 'rb')
    creds = pickle.load(token_file)
    service = build('sheets', 'v4', credentials=creds)
    spread_request = service.spreadsheets().get(spreadsheetId=spread_id,
                                                includeGridData=True,
                                                ranges=list_name)
    spread = spread_request.execute()
    spread_cache.write(json.dumps(spread))
    spread_cache.close()


# TODO: Check post by position - if 2 write in one time


""" ---===---===========================================---===--- """
"""           Generic functions for GSheets interaction           """
""" ---===---===========================================---===--- """


def get(token_path: str, sheet_id: str, list_name: str, list_range: str) -> list:
    """Generic function for getting values from Google Sheets

    Args:
        token_path - absolute path to token file
        sheet_id - id of Google Spreadsheet
        list_name - name of list of Google Spreadsheet
        list_range - range of values requested, in format RR or RR:RR
        
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
        list_range - range of values requested, in format RR or RR:RR
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


""" ---===---===========================================---===--- """
"""             Cache updating via generic GSheetsAPI             """
""" ---===---===========================================---===--- """


def gsheets_get_day(day: str) -> list:
    """Get timetable from Spreadsheet and return parsed

    Args:
        day: name of Spreadsheet list containing needed day, in format DD.MM
        
    Return:
        timetable: timetable of the corresponding day in pseudo-json
    """

    eventtypes = {
        'regular': {'blue': 1, 'green': 1, 'red': 1},
        'lecture': {'blue': 0.56078434, 'green': 0.7490196, 'red': 0.98039216},
        'master': {'blue': 0.60784316, 'green': 0.8392157, 'red': 0.7607843},
        'science': {'blue': 0.9098039, 'green': 0.5254902, 'red': 0.2901961},
        'enter': {'green': 1, 'red': 1},
        'oblig': {'blue': 0.7176471, 'green': 0.7176471, 'red': 0.7176471}
    }

    day = 'Template'  # TODO comment on release

    spread_id = '1pRvEClStcVUe9TG3hRgBTJ-43zqbESOPDZvgdhRgPlI'
    token_file = open('/home/ubuntu/iHSE_web/backend/token.pickle', 'rb')
    creds = pickle.load(token_file)
    service = build('sheets', 'v4', credentials=creds)
    spread_request = service.spreadsheets().get(spreadsheetId=spread_id,
                                                includeGridData=True,
                                                ranges=day)
    spread = spread_request.execute()
    # spreadsheet = json.loads(spread_cache.read())
    sheet_data = spread['sheets'][0]['data'][0]
    timetable = []
    nextstep = True
    row = 2

    while nextstep:
        # if current event is one-line and not last
        if 'effectiveValue' in sheet_data['rowData'][row + 1]['values'][0]:
            timetable.append({})
            timetable[-1]['time'] = sheet_data['rowData'][row]['values'][0]['effectiveValue']['stringValue']
            timetable[-1]['events'] = []
            inner_step = True
            col = 1
            while inner_step:
                timetable[-1]['events'].append({})
                timetable[-1]['events'][-1]['title'] = sheet_data['rowData'][row]['values'][col]['effectiveValue']['stringValue']
                col += 1
                while 'effectiveValue' not in sheet_data['rowData'][row]['values'][col]:
                    col += 1
                if sheet_data['rowData'][row]['values'][col]['effectiveValue']['stringValue'] == '.':
                    inner_step = False
            row += 1
        # if current event is multiline and not last
        elif 'effectiveValue' not in sheet_data['rowData'][row + 1]['values'][0] and 'effectiveValue' in sheet_data['rowData'][row + 4]['values'][0]:
            timetable.append({})
            timetable[-1]['time'] = sheet_data['rowData'][row]['values'][0]['effectiveValue']['stringValue']
            timetable[-1]['events'] = []
            inner_step = True
            col = 1
            while inner_step:
                timetable[-1]['events'].append({})
                # title
                timetable[-1]['events'][-1]['title'] = sheet_data['rowData'][row]['values'][col]['effectiveValue']['stringValue']
                # description
                if 'effectiveValue' in sheet_data['rowData'][row + 1]['values'][col]:
                    timetable[-1]['events'][-1]['desc'] = sheet_data['rowData'][row + 1]['values'][col]['effectiveValue']['stringValue']
                else:
                    timetable[-1]['events'][-1]['desc'] = ''
                # host
                if 'effectiveValue' in sheet_data['rowData'][row + 2]['values'][col]:
                    timetable[-1]['events'][-1]['host'] = sheet_data['rowData'][row + 2]['values'][col]['effectiveValue']['stringValue']
                else:
                    timetable[-1]['events'][-1]['host'] = ''
                # location
                if 'effectiveValue' in sheet_data['rowData'][row + 3]['values'][col]:
                    timetable[-1]['events'][-1]['loc'] = sheet_data['rowData'][row + 3]['values'][col]['effectiveValue']['stringValue']
                else:
                    timetable[-1]['events'][-1]['loc'] = ''
                # type
                back = sheet_data['rowData'][row]['values'][col]['effectiveFormat']['backgroundColor']
                for type_ in eventtypes.keys():
                    if eventtypes[type_] == back:
                        timetable[-1]['events'][-1]['type'] = type_
                        break
                # TODO: id
                col += 1
                while 'effectiveValue' not in sheet_data['rowData'][row]['values'][col]:
                    col += 1
                if sheet_data['rowData'][row]['values'][col]['effectiveValue']['stringValue'] == '.':
                    inner_step = False
            row += 4
        # if event is last (and it is automatically one-line
        elif 'effectiveValue' not in sheet_data['rowData'][row + 1]['values'][0] and \
                'effectiveValue' not in sheet_data['rowData'][row + 4]['values'][0]:
            # last event is always for-all one-line event
            timetable.append({})
            timetable[-1]['time'] = sheet_data['rowData'][row]['values'][0]['effectiveValue']['stringValue']
            timetable[-1]['events'] = [{'title': sheet_data['rowData'][row]['values'][1]['effectiveValue']['stringValue']}]
            nextstep = False

    return timetable


def gsheets_get_projects(filter_obj) -> list:
    """Updating cached projects without applying any filters

    project = (title, type, name, desc, annotation)

    Args: 
         filter_obj:
    Returns: 
        : list of projects satisfying filter condition
    """
    token = '/home/ubuntu/iHSE_web/backend/token.pickle'
    id_ = '1pRvEClStcVUe9TG3hRgBTJ-43zqbESOPDZvgdhRgPlI'
    position = str(int(get(token, id_, "Projects", "A1")[0][0]) - 1)
    read_values = get(token, id_, "Projects", "A4:E" + position)

    projects = []
    for project in read_values:
        projects.append({})
        projects[-1]['title'] = project[0]
        projects[-1]['type'] = project[1]
        projects[-1]['name'] = project[2]
        projects[-1]['desc'] = project[3]
        projects[-1]['anno'] = project[4]

    return projects


def gsheets_get_feedback() -> dict:
    """Get description of day for feedback in Spreadsheet
    Create new user if it does not exist  # TODO what?
    Save in table id, name, phone type and team  # TODO what?

    Returns:
        {'DD.MM': (title, [event1, event2, event3]), ...}  # TODO later: return None if already done

    """

    token = '/home/ubuntu/iHSE_web/backend/token.pickle'
    id_ = '1pRvEClStcVUe9TG3hRgBTJ-43zqbESOPDZvgdhRgPlI'
    values = get(token, id_, 'Feedback', 'A3:M5')  # TODO: update M for all days

    col = 3
    day_number = 0
    feedback = {}

    while col < len(values[1])-1:
        if values[1][col] != '':
            title = values[0][col]
            pos = 3 + 5 * day_number
            events = [values[2][pos+2], values[2][pos+3], values[2][pos+4]]
            feedback[values[1][col]] = (title, events)
            day_number += 1
        col += 1

    return feedback


def gsheets_get_events():
    """Get events from Spreadsheet

    Args:

    Returns:
        events: description of the events - list [ (id, type, title, credits, total, date, loc, host, desc, time), ... ]
    """

    token = '/home/ubuntu/iHSE_web/backend/token.pickle'
    id_ = '1pRvEClStcVUe9TG3hRgBTJ-43zqbESOPDZvgdhRgPlI'
    position = str(int(get(token, id_, "Events", "A1")[0][0]) - 1)
    read_values = get(token, id_, "Events", "A5:J" + position)

    events = []
    for event_raw in read_values:
        events.append((int(event_raw[0]),
                       event_raw[7],
                       event_raw[1],
                       int(event_raw[8]),
                       int(event_raw[9]),
                       event_raw[3],
                       event_raw[4],
                       event_raw[5],
                       event_raw[6],
                       event_raw[2]))
    return events


def gsheets_get_users():
    """Get list of users from Spreadsheet

    Returns:
        state: Read users
    """

    iHSE_length = 14

    token = '/home/ubuntu/iHSE_web/backend/token.pickle'
    id_ = '1pRvEClStcVUe9TG3hRgBTJ-43zqbESOPDZvgdhRgPlI'
    position = str(int(get(token, id_, "Users", "A1")[0][0]) - 1)
    read_values = get(token, id_, "Users", "A5:W" + position)
    users = []
    for row in read_values:
        users.append({})
        users[-1]['id'] = int(row[0])
        users[-1]['type'] = int(row[1])
        users[-1]['phone'] = row[2]
        users[-1]['name'] = row[3]
        users[-1]['pass'] = row[4]
        users[-1]['team'] = int(row[5])
        users[-1]['credits'] = int(row[6])
        users[-1]['avatar'] = row[7]
        users[-1]['credits_list'] = []
        if len(row) == 8:
            pres_creds_len = 0
        else:
            pres_creds_len = len(row) - 9
        tmp = 9
        for i in range(pres_creds_len):
            users[-1]['credits_list'].append(int(row[tmp]))
            tmp += 1
        for i in range(iHSE_length - pres_creds_len):
            users[-1]['credits_list'].append(None)
    return users


# TODO: Max update events
def update_events():
    """Update events with description in Spreadsheet and then their local copy
    Read and parse it from days sheets and save in 'Events' sheet
    And generate id
    # TODO: modify for not only initial parsing
    Note:
        If exist such event with time, date and host - update other fields
        If no event - generate with unique id

    Args:

    Returns:
        None

    """

    days = ['Template']

    for day in days:
        pass
    pass


""" ---===---==========================================---===--- """
"""         High-level functions for getting needed data         """
""" ---===---==========================================---===--- """


def get_day(day: str) -> list:
    """Return cached copy of needed day

    Args: 
         day: name of the day requested
    Returns: 
        : parsed timetable for the needed day
    """

    day = 'Template'  # TODO: comment on release

    return cached_data[day]


def get_events() -> list:
    """Return cached copy of all events

    Returns: 
        : list of parsed events
    """
    return cached_data['Events']


def get_event(event_id: int):
    """Get event with full description from Spreadsheet

    Args:
        event_id: Event id

    Returns:
        event: description of the event - (id, title, time, date, location, host, description, type, credits, total), ....
    """

    for event in cached_data['Events']:
        if event[0] == event_id:
            total_event = (event[0],
                           event[2],
                           event[9],
                           event[5],
                           event[6],
                           event[7],
                           event[8],
                           event[1],
                           event[3],
                           event[4])
            return total_event

    return None


def get_projects() -> list:
    """Get list of projects from Spreadsheet and return parsed
    Create new user if it does not exist
    Save in table id, name, phone type and team

    Args:
        filter_obj: filter what we should return - (title, type, name)   # TODO later

    Returns:
        List of projects obj:
              [ {
                 "title": string,
                 "name": string,
                 "type": string,
                 "desc": string,
                 "anno": string
                 }, .........  ]
    """
    global cached_data

    print(test_data)
    return cached_data['Projects']


def get_credits(user_obj) -> list:
    """Get credits data from google sheets

    Args:
        user_obj: User object - (id, type, phone, name, pass, team, credits, avatar)

    Returns:
        credits: credits data -  {'total': 123, 'data': [1, 2, 4, 3, ...]}

    """

    for user in cached_data['Users']:
        if user['id'] == user_obj[0]:
            return user['credits_list']


def get_users() -> list:
    """Return cached copy of all users

    Returns:
        : list of all users, user represented as LIST according to Spreadsheet
    """

    users_list = []
    for user in cached_data['Users']:
        users_list.append((user['id'],
                           user['type'],
                           user['phone'],
                           user['name'],
                           user['pass'],
                           user['team'],
                           user['credits'],
                           user['avatar']))
    return users_list


def get_feedback(day: str):
    """Get description of day for feedback in Spreadsheet
    Create new user if it does not exist  # TODO what?
    Save in table id, name, phone type and team  # TODO what?

    Args:
        day: num of the day - 'DD.MM'

    Returns:
        (title, [event1, event2, event3])  # TODO later: return None if already done

    """
    return cached_data['Feedback'][day]

""" ---===---==========================================---===--- """
"""         High-level functions for posting needed data         """
""" ---===---==========================================---===--- """


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

    update_cache('Feedback')
    return True


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
        write_response = post(token, id_, "Users", "A" + str(5+i) + ":I" + str(5+i), data)

    response = post(token, id_, "Users", "A1", [[int(position) + len(users_list)]])





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
    write_response = post(token, id_, "Projects", "A" + position + ":E" + position, values)
    update_response = post(token, id_, "Projects", "A1", [[int(position) + 1]])

    return True  # TODO: check GSheetsAPI how to track success


# TODO: Max save credits
def save_credits(user_obj, event_obj):
    """ Save credits for some event of user in google sheets
    Create new user if it does not exist

    Args:
        user_obj: User object - (id, type, phone, name, pass, team, credits, avatar)
        event_obj: Event object - (id, type, title, credits, date)

    Returns:
        state: Success or not - bool

    """
    token = '/home/ubuntu/iHSE_web/backend/token.pickle'
    id_ = '1pRvEClStcVUe9TG3hRgBTJ-43zqbESOPDZvgdhRgPlI'
    pos = str(int(get(token, id_, 'Users', 'A1')[0][0]) - 1)
    curr_data = get(token, id_, 'Users', 'A4:W' + pos)
    target_grow, target_gcol = 0, 0
    user_id = str(user_obj[0])
    for index, row in enumerate(curr_data, start=4):
        if row[0] == user_id:
            target_grow = index
            break
    for index, col in enumerate(curr_data[0]):
        if col == event_obj[4]:
            target_gcol = index
    target_gcol = chr(ord('A') + target_gcol)
    curr_val = int(get(token, id_, 'Users', target_gcol + str(target_grow))[0][0])
    curr_val += event_obj[3]
    post(token, id_, 'Users', target_gcol + str(target_grow), [[str(curr_val)]])


""" ---===---===========================================---===--- """
"""           Functions for managing registration codes           """
""" ---===---===========================================---===--- """


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


def generate_registration_codes(num, type_=0):
    """ Generate registration codes by number
    Each code is a 6-characters-number-letter code

    Args:
        num: Number of codes
        type_: Type of user [0, 1, 2, 3]

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
        code = symbols[random.randint(0, size - 1)] + \
               symbols[random.randint(0, size - 1)] + \
               symbols[i // size] + \
               symbols[i % size] + \
               symbols[i * i % size] + \
               symbols[(type_ % (size // 5) + 1) * random.randint(0, size // 5)]

        rez.append(code)

    return rez


def check_code(code: str):
    """ Check registration code in Google Sheets
    Get user type according this code

    Args:
        code: special code hash which will be responsible for
                    the user type and permission to register


    Return:
        type: type of user, int or None if registration rejected

    """
    # TODO: maybe it has to happen on cache too?
    token = '/home/ubuntu/iHSE_web/backend/token.pickle'
    id_ = '1pRvEClStcVUe9TG3hRgBTJ-43zqbESOPDZvgdhRgPlI'
    read_values = get(token, id_, "Codes", "A5:C9")

    reg_allowed = False
    user_type = -1
    for index, code_line in enumerate(read_values, start=5):
        if code_line[0] == code and code_line[2] == '0':
            user_type = int(code_line[1])

            update_response = post(token, id_, "Codes", "C" + str(index), [[1]])
            reg_allowed = True
            break

    if reg_allowed:
        return user_type
    else:
        return None
