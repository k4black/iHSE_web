import time
import string
import typing as tp

import sqlite3
import psycopg2


""" ---===---==========================================---===--- """
"""                    SQLite database creation                  """
""" ---===---==========================================---===--- """

# initializing connection to database
# TODO: plain text user & password, great
conn = psycopg2.connect('dbname=root user=root password=root')
cursor = conn.cursor()


def checkpoint():
    # TODO: do we need checkpoint now? Maybe same flags should be set somehow in the PostgreSQL (need to check that)?
    # TODO: I dont f_ing know. Did you found where db file located?

    pass
    # conn_sqlite.execute("PRAGMA wal_checkpoint(TRUNCATE)")  # WAL
    # conn_sqlite.execute("VACUUM;")  # Repack database file


checkpoint()

# Projects
cursor.execute('''
                    create table if not exists projects (
                        id serial not null primary key unique,
                        title text,
                        type int,
                        def_type int,
                        direction text,
                        description text
                    ); 
                    ''')

# Users
cursor.execute('''
                    create table if not exists users (
                        id serial not null primary key unique,
                        user_type int,
                        phone text,
                        name text,
                        pass int,
                        team int,
                        credits int default 0,
                        avatar text default '',
                        project_id serial default 0,
                        foreign key (project_id) references projects(id)
                    ); 
                    ''')

# Sessions
cursor.execute("""CREATE OR REPLACE FUNCTION random_bytea(bytea_length integer)
                  RETURNS bytea AS $$
                  SELECT decode(string_agg(lpad(to_hex(width_bucket(random(), 0, 1, 256)-1),2,'0') ,''), 'hex')
                  FROM generate_series(1, $1);
                  $$
                  LANGUAGE 'sql';""")
cursor.execute('''create table if not exists sessions (
                        id bytea not null primary key unique default random_bytea(16),
                        user_id int,
                        user_type int,
                        user_agent text,
                        last_ip text,
                        time text,
                        foreign key (user_id) references users(id)
                    );
                    ''')

# Feedback
cursor.execute("""
                    create table if not exists feedback (
                        id serial not null primary key,
                        user_id serial,
                        data text,
                        time text default 'datetime(''now'', ''localtime'')',
                        main_message text,
                        main_score int,
                        foreign key (user_id) references users(id)
                    );
                    """)

# Events
cursor.execute('''
                    create table if not exists events (
                        id serial not null primary key unique,
                        type int,
                        title text,
                        description text,
                        host text,
                        place text,
                        time text,
                        date text
                    );
                    ''')

# Classes
cursor.execute('''
                    create table if not exists classes (
                        id serial not null primary key unique,
                        credits int,
                        count int default 0,
                        total int,
                        foreign key (id) references events(id)
                    );
                    ''')


# Enrolls
cursor.execute('''
                    create table if not exists enrolls (
                        id serial not null primary key unique,
                        event_id serial,
                        user_id serial,
                        time text default 'datetime(''now'', ''localtime'')',
                        attendance int default 0,
                        foreign key (user_id) references users(id),
                        foreign key (event_id) references classes(id)
                    );
                    ''')

# Credits
cursor.execute('''
                    create table if not exists credits (
                        id serial not null primary key unique,
                        user_id serial,
                        event_id serial,
                        date text,
                        value int default 0,
                        foreign key (user_id) references users(id),
                        foreign key (event_id) references classes(id)
                    ); 
                    ''')

# Codes
cursor.execute('''
                    create table if not exists codes (
                        code text,
                        type int default 0,
                        used int default 0
                    ); 
                    ''')

# cursor.execute('''
#                     create table if not exists project_users (
#                         user_id serial,
#                         project_id serial,
#                         foreign key (user_id) references users(id)
#                         foreign key (project_id) references projects(id)
#                     );
#                     ''')

conn.commit()


table_fields = {
    'projects': ('id', 'title', 'type', 'def_type', 'direction', 'description'),
    'users': ('id', 'user_type', 'phone', 'name', 'pass', 'team', 'credits', 'avatar', 'project_id'),
    'sessions': ('id', 'user_id', 'user_type', 'user_agent', 'last_ip', 'time'),
    'events': ('id', 'type', 'title', 'description', 'host', 'place', 'time', 'date'),
    'classes': ('id', 'credits', 'count', 'total'),
    'enrolls': ('id', 'event_id', 'user_id', 'time', 'attendance'),
    'credits': ('id', 'user_id', 'event_id', 'date', 'value'),
    'codes': ('code', 'type', 'used')
}


def process_sql(data_raw: tp.List[tp.Tuple[tp.Any]], table: str) -> tp.List[tp.Dict[str, tp.Any]]:
    data = []

    for line in data_raw:
        data.append({table_fields[table][i]: line[i] for i in range(len(table_fields[table]))})

    return data


def dict_to_tuple(data_raw: tp.Dict[str, tp.Any], table: str) -> tp.Tuple[tp.Any]:
    data = []  # type: tp.List[tp.Any]

    for field in table_fields[table]:
        try:
            if field == 'id' and data_raw[field] == '':
                data.append(None)  # No id. Replace by None
            else:
                data.append(data_raw[field])
        except KeyError:
            data.append(None)  # if no field

    return tuple(data)


def tuple_to_dict(data_raw: tp.Tuple[tp.Any], table: str) -> tp.Dict[str, tp.Any]:
    data = {}  # type: tp.Dict[str, tp.Any]

    for i in range(len(table_fields[table])):
        data[table_fields[table][i]] = data_raw[i]

    return data


""" ---===---==========================================---===--- """
"""           Auxiliary functions for sql interactions           """
""" ---===---==========================================---===--- """


# TODO: check SQL injections
def safety_injections(param):
    """ Check and remove sql injections

    Args:
        param: parameter - any type

    Returns:
        Safety param: parameter clear of injections

    """

    if type(param) == int:
        return param

    if type(param) == str:
        param.replace('"', '')
        param.replace('\'', '')
        param.replace(',', '')
        param.replace(';', '')

    return param


""" ---===---==========================================---===--- """
"""         PostgreSQL database interaction via psycopg2         """
""" ---===---==========================================---===--- """
# TODO: on the higher level we need to prompt admin before every remove_<smth>() is performed
# TODO: yep. I know. Temporary commented this code for checking and testing


# Projects
def get_projects():
    """ Get all projects from sql table

    Args:

    Returns:
        project objects: list of project objects - [ (id, title, type, def_type, direction, description), ...]

    """
    cursor.execute('select * from projects;')
    projects_list = cursor.fetchall()

    return projects_list


def insert_project(project_obj):
    """ Insert project

    Args:
        project_obj: project obj (None, title, type, def_type, direction, description)

    Returns:
        # TODO: Return id
    """
    cursor.execute(
        f'insert into projects (title, type, def_type, direction, description) values (\'{project_obj[1]}\', \'{project_obj[2]}\', \'{project_obj[3]}\', \'{project_obj[4]}\', \'{project_obj[5]}\'); ')
    conn.commit()


def edit_project(project_obj):
    """ Update project

    Args:
        project_obj: project obj (id, title, type, def_type, direction, description)

    Returns:
    """
    cursor.execute(f'''update projects set
                                title = \'{project_obj[1]}\',
                                type = \'{project_obj[2]}\',
                                def_type = \'{project_obj[3]}\',
                                direction = \'{project_obj[4]}\',
                                description = \'{project_obj[5]}\'
                            where id = {project_obj[0]};
                        ''')
    conn.commit()


def remove_project(project_id):
    """ Delete project by id

    Args:
        project_id: projects id from bd

    Returns:
        # Success delete or not
    """

    if project_id == 0 or project_id == '0':
        return

    cursor.execute(f'update users set project_id = 0 where project_id = {project_id};')
    cursor.execute(f'delete from projects where id = {project_id};')
    conn.commit()


def clear_projects():
    """ Clear all projects from sql table

    Args:
    Returns:
    """

    cursor.execute('delete from projects where id != 0;')
    conn.commit()


# Users
# TODO: delete  after migration ???
def load_users(users_list):
    """ Load all users to sql table
    Clear users table and sessions table and insert all users in users table

    Args:
        users_list: list of user objects - [(id, user_type, phone, name, pass, team, credits, avatar, project_id), ...]

    Returns:

    """

    # Clear user and sessions tables
    # cursor.execute("DELETE FROM sessions")
    cursor.execute("DELETE FROM users;")
    conn.commit()

    # Add users in bd
    for user_obj in users_list:
        if user_obj[7] is None:
            avatar = ""
        else:
            avatar = user_obj[7]

        cursor.execute("""INSERT INTO users(id, user_type, phone, name, pass, team, credits, avatar)
                          SELECT ?, ?, ?, ?, ?, ?, ?, ?
                          WHERE NOT EXISTS(SELECT 1 FROM users WHERE name=? AND pass=?)""",
                       (user_obj[0], user_obj[1], user_obj[2], user_obj[3], user_obj[4], user_obj[5], user_obj[6], avatar, user_obj[3], user_obj[4]))
    conn.commit()


def get_users():
    """ Get all users from sql table

    Args:

    Returns:
        user objects: list of user objects - [(id, user_type, phone, name, pass, team, credits, avatar, project_id), ...]
    """
    cursor.execute('select * from users;')
    users_list = cursor.fetchall()

    return users_list


def get_user(user_id):
    """ Get user obj by id

    Args:
        user_id: user id from bd

    Returns:
        user_obj: (id, user_type, phone, name, pass, team, credits, avatar, project_id)
                     or None if there is no such user

    """
    cursor.execute(f'select * from users where id = {user_id};')
    users = cursor.fetchall()
    # cursor.execute("SELECT * FROM users WHERE id=?", (user_id, ))
    # users = cursor.fetchall()

    if len(users) == 0:    # No such user
        return None
    else:
        return users[0]


def get_user_by_phone(phone):
    """ Get user obj by phone

    Args:
        phone: phone - str

    Returns:
        user_obj: (id, user_type, phone, name, pass, team, credits, avatar, project_id)
                     or None if there is no such user

    """
    cursor.execute(f'select * from users where phone = \'{phone}\';')
    users = cursor.fetchall()
    # cursor.execute("SELECT * FROM users WHERE phone=?", (phone, ))
    # users = cursor.fetchall()

    if len(users) == 0:    # No such user
        return None
    else:
        return users[0]


def insert_user(user_obj):
    """ Insert user

    Args:
        user_obj: user obj (None, user_type, phone, name, pass, team, credits, avatar, project_id)

    Returns:
    """
    cursor.execute(f'insert into users (user_type, phone, name, pass, team, credits, avatar, project_id) values ({user_obj[1]}, \'{user_obj[2]}\', \'{user_obj[3]}\', {user_obj[4]}, {user_obj[5]}, {user_obj[6]}, \'{user_obj[7]}\', {user_obj[8]}); ')
    conn.commit()


def edit_user(user_obj):
    """ Update user

    Args:
        user_obj: user obj (id, user_type, phone, name, pass, team, credits, avatar, project_id)

    Returns:
    """
    # test_cursor.execute(f'call CreateOrModifyUser({user_obj[0]}, {user_obj[1]}, {user_obj[2]}, {user_obj[3]}, {user_obj[4]}, {user_obj[5]}, {user_obj[6]});')
    cursor.execute(f'''update users set
                                user_type = {user_obj[1]},
                                phone = \'{user_obj[2]}\',
                                name = \'{user_obj[3]}\',
                                pass = {user_obj[4]},
                                team = {user_obj[5]},
                                credits = {user_obj[6]},
                                avatar = \'{user_obj[7]}\',
                                project_id = {user_obj[8]}
                            where id = {user_obj[0]};
                        ''')
    conn.commit()


def register(name, passw, type, phone, team):
    """ Register new user
    There is no verification - create anywhere

    Args:
        name: User name - string
        passw: Password hash - int
        type: User type - int  [0 - USER, 1 - HOST, 2 - ADMIN]
        phone: phone - string
        team: number of group - int

    Note:
        user id is automatically generated

    Returns:
    """
    # TODO: change to PostgreSQL
    cursor.execute(f'select * from users where name = \'{name}\' and pass = {passw};')
    existing_users = cursor.fetchall()
    if len(existing_users) == 0:
        cursor.execute(f'insert into users (user_type, phone, name, pass, team) values ({type}, \'{phone}\', \'{name}\', {passw}, {team});')
        conn.commit()
        # Register new user if there is no user with name and pass
        # cursor.execute("""INSERT INTO users(user_type, phone, name, pass, team)
        #                   SELECT ?, ?, ?, ?, ?
        #                   WHERE NOT EXISTS(SELECT 1 FROM users WHERE name=? AND pass=?)""",
        #                (type, phone, name, passw, team, name, passw))
        # conn.commit()


# TODO
def checkin_user(user_obj, event_obj):
    """ Checkin user in event
    Add user credits for the event

    Args:
        user_obj: (id, user_type, phone, name, pass, team, credits, avatar, project_id)
        event_obj: (id, type, title, credits, count, total, date)

    Returns:
    """
    cursor.execute(f'update users set credits = {event_obj[3] + user_obj[6]} where id = {user_obj[0]};')
    conn.commit()
    # cursor.execute("UPDATE users SET credits=? WHERE id=?", (user_obj[6] + event_obj[3], user_obj[0], ))
    # conn.commit()


def remove_user(user_id):
    """ Delete user by id

    Args:
        user_id: user id from db

    Returns:
        # Success delete or not

    """
    cursor.execute(f'delete from sessions where user_id = {user_id};')
    cursor.execute(f'delete from feedback where user_id = {user_id};')
    cursor.execute(f'delete from credits where user_id = {user_id};')
    cursor.execute(f'delete from users where id = {user_id};')
    conn.commit()
    # cursor.execute("DELETE FROM users WHERE id=?", (user_id, ))
    # conn.commit()


def clear_users():
    """ Clear all users from sql table

    Args:
    Returns:
    """
    cursor.execute('delete from users;')
    conn.commit()


# Sessions
def get_sessions():
    """ Get all sessions from sql table

    Args:

    Returns:
        session objects: list of sess objects - [ (id, user_id, user_type, user_agent, last_ip, time), ...]

    """
    cursor.execute('select * from sessions;')
    sessions_list = cursor.fetchall()
    # cursor.execute("SELECT * FROM sessions")
    # sessions_list = cursor.fetchall()

    for i in range(len(sessions_list)):
        sessions_list[i] = ((sessions_list[i][0]).hex(), *sessions_list[i][1:])

    return sessions_list


def get_session(sess_id):
    """ Get session obj by id

    Args:
        sess_id: session id from db

    Returns:
        session obj: (id, user_id, user_type, user_agent, last_ip, time)
                     or None if there is no such session

    """
    cursor.execute(f"select * from sessions where id = bytea \'\\x{sess_id}\';")
    sessions = cursor.fetchall()
    # cursor.execute("SELECT * FROM sessions WHERE id=?", (sess_id, ))
    # sessions = cursor.fetchall()

    if len(sessions) == 0:  # No such session
        return None
    else:
        return sessions[0]


def insert_session(sess_obj):
    """ Insert session

    Args:
        sess_obj: sess obj (None, user_id, user_type, user_agent, last_ip, time)

    Returns:
    """
    cursor.execute(f'insert into sessions (user_id, user_type, user_agent, last_ip, time) values ({sess_obj[1]}, {sess_obj[2]}, \'{sess_obj[3]}\', \'{sess_obj[4]}\', \'{sess_obj[5]}\');')
    conn.commit()


def edit_session(sess_obj):
    """ Update session

    Args:
        sess_obj: sess obj (id, user_id, user_type, user_agent, last_ip, time)

    Returns:
    """
    cursor.execute(f'''update sessions set
                                user_id = {sess_obj[1]},
                                user_type = {sess_obj[2]},
                                user_agent = \'{sess_obj[3]}\',
                                last_ip = \'{sess_obj[4]}\',
                                time = \'{sess_obj[5]}\'
                            where id = {sess_obj[0]};
                        ''')
    conn.commit()


# TODO: Update time in sessions
def login(phone, passw, agent, ip, time='0'):
    """ Login user
    Create new session if it does not exist and return sess id

    Args:
        phone: User phone - string
        passw: Password hash - int
        agent: User agent - string
        ip: ip - string
        time: time of session creation

    Note:
        session id is automatically generated

    Returns:
        sess_id: session id - string of hex
                 b'\xbeE%-\x8c\x14y3\xd8\xe1ui\x03+D\xb8' -> be45252d8c147933d8e17569032b44b8
    """

    # Check user with name and pass exist and got it
    cursor.execute(f'select * from users where phone = \'{phone}\' and pass = {passw};')
    users = cursor.fetchall()
    # cursor.execute("SELECT * FROM users WHERE phone=? AND pass=?", (phone, passw))
    # users = cursor.fetchall()

    if len(users) == 0:    # No such user
        return None

    user = users[0]

    # Create new session if there is no session with user_id and user_agent
    cursor.execute(f'select * from sessions where user_id = {user[0]} and user_agent = \'{agent}\';')
    existing_sessions = cursor.fetchall()
    if len(existing_sessions) == 0:
        cursor.execute(f"""
                            insert into sessions (user_id, user_type, user_agent, last_ip, time)
                                values ({user[0]}, {user[1]}, \'{agent}\', \'{ip}\', \'{time}\');             ;
                            """)
        conn.commit()
    # cursor.execute("""INSERT INTO sessions(user_id, user_type, user_agent, last_ip, time)
    #                   SELECT ?, ?, ?, ?, ?
    #                   WHERE NOT EXISTS(SELECT 1 FROM sessions WHERE user_id=? AND user_agent=?)""",
    #                (user[0], user[1], agent, ip, time, user[0], agent))
    # conn.commit()


    # Get session corresponding to user_id and user_agent
    cursor.execute(f'select * from sessions where user_id = {user[0]} and user_agent = \'{agent}\';')
    result = cursor.fetchone()
    # cursor.execute("SELECT * FROM sessions WHERE user_id=? AND user_agent=?", (user[0], agent))
    # result = cursor.fetchone()

    print(f'session got by login:{result}')
    return result


def remove_session(sess_id):
    """ Remove session by id

    See:
        logout
    """
    logout(sess_id)


# TODO: both remove_session() and logout() needed?
def logout(sess_id):
    """ Delete current session by sessid

    Args:
        sess_id: session id from bd

    Returns:
        Success delete or not

    """
    cursor.execute(f'select * from sessions where id = bytea \'\\x{sess_id}\';')
    sessions = cursor.fetchall()
    # cursor.execute("SELECT * FROM sessions WHERE id=?", (sess_id, ))
    # sessions = cursor.fetchall()

    if len(sessions) == 0:    # No such session
        return False

    cursor.execute(f'delete from sessions where id = bytea \'\\x{sess_id}\';')
    conn.commit()
    # cursor.execute("DELETE FROM sessions WHERE id=?", (sess_id, ))
    # conn.commit()
    return True


def clear_sessions():
    """ Clear all sessions from sql table

    Args:
    Returns:
    """
    cursor.execute('delete from sessions;')
    conn.commit()
    # cursor.execute("DELETE FROM sessions")
    # conn.commit()


# Feedback
# TODO: do we handle feedback at all!?
# TODO: Yeeeees. Somehow. Now i have some ideas, but you are welcome with any thoughts


# Events
def get_events():
    """ Get all events from sql table

    Args:

    Returns:
        event objects: list of event objects - [ (id, type, title, description, host, place, time, date), ...]

    """
    cursor.execute('select * from events;')
    events_list = cursor.fetchall()
    # cursor.execute("SELECT * FROM events")
    # events_list = cursor.fetchall()

    return events_list


def get_day(date: str):
    """ Get all events for some day from sql table

    Args:
        date: dd.mm day for select data

    Returns:
        event objects: list of event objects - [ (id, type, title, description, host, place, time, date), ...]

    """
    cursor.execute(f'select * from events where date = \'{date}\';')
    events_list = cursor.fetchall()

    return events_list


# TODO: Both het_events() and load_events() needed?
def load_events(events_list):
    """ Load all events to sql table
    Clear events and insert all events in events table

    Args:
        events_list: list of event objects - [ (id, type, title, description, host, place, time, date), ...]

    Returns:

    """

    # Safe update events - save count of people
    for event_obj in events_list:
        cursor.execute("""
                          INSERT OR IGNORE INTO events(id, type, title, credits, total, date)
                          VALUES (?, ?, ?, ?, ?, ?); 
                        """, (event_obj[0], event_obj[1], event_obj[2], event_obj[3], event_obj[4], event_obj[5],))
        cursor.execute("""
                          UPDATE events SET type=?, title=?, credits=?, total=? WHERE id=?; 
                        """, (event_obj[1], event_obj[2], event_obj[3], event_obj[4], event_obj[0]))
    conn.commit()

    return


def get_event(event_id):
    """ Get event obj by id

    Args:
        event_id: event id from bd

    Returns:
        event_obj: (id, type, title, description, host, place, time, date)
    """
    cursor.execute(f'select * from events where id = {event_id};')
    events = cursor.fetchall()

    if len(events) == 0:  # No such event
        return None
    else:
        return events[0]


def insert_event(event_obj):
    """ Insert event

    Args:
        event_obj: event obj (None, type, title, description, host, place, time, date)

    Returns:
    """

    cursor.execute(f'insert into events (id, type, title, description, host, place, time, date) values (default, {event_obj[1]}, \'{event_obj[2]}\', \'{event_obj[3]}\', \'{event_obj[4]}\', \'{event_obj[5]}\', \'{event_obj[6]}\', \'{event_obj[7]}\') RETURNING id;')
    id_of_new_event = cursor.fetchone()[0]
    print('Added event ID=', id_of_new_event, 'type', event_obj[1])

    if int(event_obj[1]) == 1:
        # class
        cursor.execute(f'insert into classes (id, credits, count, total) values ({id_of_new_event}, 100, 0, 10);')
    else:
        # regular
        pass

    conn.commit()


def edit_event(event_obj):
    """ Update event

    Args:
        event_obj: event obj (id, type, title, description, host, place, time, date)

    Returns:
    """
    cursor.execute(f'''update events set
                                type = {event_obj[1]},
                                title = \'{event_obj[2]}\',
                                description = \'{event_obj[3]}\',
                                host = \'{event_obj[4]}\',
                                place = \'{event_obj[5]}\',
                                time = \'{event_obj[6]}\',
                                date = \'{event_obj[7]}\'
                            where id = {event_obj[0]};
                        ''')
    conn.commit()


def remove_event(event_id):
    """ Delete event by id

    Args:
        event_id: event id from bd

    Returns:
        # Success delete or not

    """
    if event_id == 0 or event_id == '0':
        return

    try:
        cursor.execute(f'update credits set event_id = 0 where event_id = {event_id};')
        cursor.execute(f'delete from classes where id = {event_id};')
        cursor.execute(f'delete from events where id = {event_id};')
    except (psycopg2.InternalError, psycopg2.IntegrityError) as error:
        print(error)
        cursor.execute('rollback;')
    conn.commit()


def clear_events():
    """ Clear all events from sql table

    Args:
    Returns:
    """
    cursor.execute('delete from events where id != 0;;')
    conn.commit()


# Classes
def get_classes():
    """ Get all classes (events type) from sql table

    Args:

    Returns:
        class objects: list of event objects - [ (id, credits, count, total), ...]

    """
    cursor.execute('select * from classes;')
    classes_list = cursor.fetchall()

    return classes_list


def get_class(event_id):
    """ Get event obj by id

    Args:
        event_id: event id from bd

    Returns:
        class_obj: (id, credits, count, total)
    """

    cursor.execute(f'select * from classes where id = {event_id};')
    events = cursor.fetchall()

    if len(events) == 0:  # No such event
        return None
    else:
        return events[0]


def insert_class(class_obj):
    """ Insert project

    Args:
        class_obj: class obj (None, credits, count, total)

    Returns:
        # TODO: Return id
    """
    cursor.execute(f'insert into classes (credits, count, total) values ({class_obj[1]}, {class_obj[2]}, {class_obj[3]}); ')
    conn.commit()


def edit_class(class_obj):
    """ Update project

    Args:
        class_obj: class obj (id, credits, count, total)

    Returns:
    """
    cursor.execute(f'''update classes set
                                credits = {class_obj[1]},
                                count = {class_obj[2]},
                                total = {class_obj[3]}
                            where id = {class_obj[0]};
                        ''')
    conn.commit()


def enroll_user(class_id, user_obj):  # TODO
    """ Enroll user in event

    Args:
        class_id: class id (event id) from bd
        user_obj: (id, user_type, phone, name, pass, team, credits)

    Returns:
        True/False: Success or not
    """

    cursor.execute(f'select * from class where id = {class_id};')
    events = cursor.fetchall()
    # cursor.execute("SELECT * FROM events WHERE id=?", (event_id, ))
    # events = cursor.fetchall()

    if len(events) == 0 or events[0][4] >= events[0][5]:  # No such event or too many people
        return False

    event = events[0]

    cursor.execute(f'update class set count = {event[4] + 1} where id = {class_id};')
    conn.commit()

    return True


def remove_class(class_id):
    """ Delete class by id

    Args:
        class_id: class id (event id) from bd

    Returns:
        # Success delete or not

    """
    remove_event(class_id)


# Enrolls
def get_enrolls():
    """ Get all enrolls from sql table

    Args:

    Returns:
        enroll_obj: list of enroll objects - [ (id, event_id, user_id, time), ...]

    """
    cursor.execute('select * from enrolls;')
    enrolls_list = cursor.fetchall()

    return enrolls_list


def get_enroll(enroll_id):
    """ Get enrolls obj by id

    Args:
        enroll_id: enroll id from bd

    Returns:
        enroll_obj: (id, event_id, user_id, time, attendance)
    """

    cursor.execute(f'select * from enrolls where id = {enroll_id};')
    enrolls = cursor.fetchall()

    if len(enrolls) == 0:  # No such enrolls
        return None
    else:
        return enrolls[0]


def get_enrolls_by_event_id(event_id):
    """ Get enrolls obj by id

    Args:
        event_id: event id from bd

    Returns:
        enroll_objs: [(id, event_id, users_id, time, attendance), ...]
    """

    cursor.execute(f'select * from enrolls where event_id = {event_id};')
    enrolls = cursor.fetchall()

    if len(enrolls) == 0:  # No such enrolls
        return []
    else:
        return enrolls


def get_enrolls_by_user_id(user_id):
    """ Get enrolls obj by id

    Args:
        user_id: user id from bd

    Returns:
        enroll_objs: [(id, event_id, users_id, time, attendance), ...]
    """

    cursor.execute(f'select * from enrolls where user_id = {user_id};')
    enrolls = cursor.fetchall()

    if len(enrolls) == 0:  # No such enrolls
        return []
    else:
        return enrolls


def insert_enroll(enroll_obj):
    """ Insert enroll

    Args:
        enroll_obj: class obj (None, event_id, user_id, time, attendance)

    Returns:
        # TODO: Return id
    """

    cursor.execute(f'select * from classes where id = {enroll_obj[1]};')
    event = cursor.fetchone()
    cursor.execute(f'update classes set count = {event[2] + 1} where id = {event[0]};')

    cursor.execute(f'insert into enrolls (event_id, user_id, time, attendance) values ({enroll_obj[1]}, {enroll_obj[2]}, \'{enroll_obj[3]}\', {enroll_obj[4]});')
    conn.commit()


def edit_enroll(enroll_obj):
    """ Update enroll

    Args:
        enroll_obj: enroll obj (id, event_id, user_id, time, attendance)

    Returns:
    """

    cursor.execute(f'select * from enrolls where id = {enroll_obj[0]};')
    enroll = cursor.fetchone()

    if enroll[1] != enroll_obj[1]:
        # Change old event
        cursor.execute(f'select * from classes where id = {enroll[1]};')
        current_event = cursor.fetchone()
        cursor.execute(f'update classes set count = {current_event[2] - 1} where id = {current_event[0]};')

        # Change new event
        cursor.execute(f'select * from classes where id = {enroll_obj[1]};')
        new_event = cursor.fetchone()
        cursor.execute(f'update classes set count = {new_event[2] + 1} where id = {new_event[1]};')

    cursor.execute(f'''update enrolls set
                                event_id = {enroll_obj[1]},
                                user_id = {enroll_obj[2]},
                                time = \'{enroll_obj[3]}\',
                                attendance = {enroll_obj[4]}
                            where id = {enroll_obj[0]};
                        ''')
    conn.commit()


def remove_enroll(enroll_id):
    """ Delete enroll by id

    Args:
        enroll_id: enroll id from bd

    Returns:
        # Success delete or not
    """

    cursor.execute(f'select * from enrolls where id = {enroll_id};')
    enroll = cursor.fetchone()

    event_id = enroll[1]

    cursor.execute(f'select * from classes where id = {event_id};')
    event = cursor.fetchone()
    cursor.execute(f'update classes set count = {event[2] - 1} where id = {event_id};')

    cursor.execute(f'delete from enrolls where id = {enroll_id};')
    conn.commit()  # TODO: Check (and think) if theteare credtis according this event. delete it


# Credits
def get_credits():
    """ Get all credits from sql table

    Args:

    Returns:
        credits objects: list of credits objects - [ (id, user_id, event_id, date, value), ...]

    """
    cursor.execute('select * from credits;')
    credits_list = cursor.fetchall()

    return credits_list


def get_credits_by_id(user_id):  # TODO: Hm.. Rename to get_credits(user_id)
    """ Get all credits of user from sql table

    Args:
        user_id: id of user for selecting

    Returns:
        credits objects: list of credits objects - [ (id, user_id, event_id, date, value), ...]
    """

    cursor.execute(f'select * from credits where user_id = {user_id};')
    credits_list = cursor.fetchall()

    return credits_list


def insert_credit(credit_obj):
    """ Insert credit

    Args:
        credit_obj: credit obj (None, user_id, event_id, date, value)

    Returns:
    """
    cursor.execute(f'insert into credits (id, user_id, event_id, date, value) values (default, {credit_obj[1]}, {credit_obj[2]}, \'{credit_obj[3]}\', {credit_obj[4]}); ')
    conn.commit()


def edit_credit(credit_obj):
    """ Update credit

    Args:
        credit_obj: credit obj (id, user_id, event_id, date, value)

    Returns:
    """
    cursor.execute(f'''update credits set
                                user_id = {credit_obj[1]},
                                event_id = {credit_obj[2]},
                                date = \'{credit_obj[3]}\',
                                value = {credit_obj[4]}
                            where id = {credit_obj[0]};
                        ''')
    conn.commit()


def remove_credit(credit_id):
    """ Delete credit by id

    Args:
        credit_id: projects id from bd

    Returns:
        # Success delete or not

    """
    cursor.execute(f'delete from credits where id = {credit_id};')
    conn.commit()


def clear_credits():
    """ Clear all credits from sql table

    Args:
    Returns:
    """
    cursor.execute('delete from credits;')
    conn.commit()


# Codes
def get_codes():
    """ Get all codes from sql table

    Args:

    Returns:
        project objects: list of project objects - [ (code, type, used), ...]

    """
    cursor.execute('select * from code;')
    codes_list = cursor.fetchall()

    return codes_list


def load_codes(codes):
    """ Cleat codes table and setup from codes

    Args:
        codes: codes list - [(str, int), (str, int), ... ]

    Returns:

    """

    for code in codes:
        cursor.execute(f'insert into codes (code, type, used) values ({code[0]}, \'{code[1]}\', 0);')
    conn.commit()


def use_code(code):
    """ Set code used

    Args:
        code: code from bd

    Returns:
        Success delete or not

    """

    cursor.execute(f'select * from codes where code = {code};')
    codes_list = cursor.fetchall()

    if len(codes_list) == 0 or codes_list[0][2]:
        return False

    cursor.execute(f'update codes set used = {1} where code = {code};')
    conn.commit()


def clear_codes():
    """ Clear all codes from sql table

    Args:
    Returns:
    """
    cursor.execute('delete from codes;')
    conn.commit()
