import sqlite3
import time
import string
import psycopg2


""" ---===---==========================================---===--- """
"""                    SQLite database creation                  """
""" ---===---==========================================---===--- """

conn = psycopg2.connect('dbname=root user=root password=root')
cursor = conn.cursor()


conn_sqlite = sqlite3.connect("/home/ubuntu/db/main.sqlite", check_same_thread=False)
conn_sqlite.execute("PRAGMA journal_mode=WAL")  # https://www.sqlite.org/wal.html
conn_sqlite.execute("PRAGMA wal_autocheckpoint=100")
conn_sqlite.execute("PRAGMA busy_timeout=1000")
conn_sqlite.execute("PRAGMA synchronous=1")

cursor_sqlite = conn_sqlite.cursor()


def checkpoint():
    conn_sqlite.execute("PRAGMA wal_checkpoint(TRUNCATE)")  # WAL
    conn_sqlite.execute("VACUUM;")  # Repack database file


checkpoint()

# Users
cursor_sqlite.execute("""CREATE TABLE IF NOT EXISTS  "users" (
                    "id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                    "user_type"	INTEGER,
                    "phone"	TEXT,
                    "name"	TEXT,
                    "pass"	INTEGER,
                    "team"	INTEGER,
                    "credits"	INTEGER DEFAULT (0),
                    "avatar" TEXT  DEFAULT ('')
                  );
               """)
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

# Credits
cursor.execute('''
                    create table if not exists credits (
                        user_id serial,
                        event_id serial,
                        date text,
                        value int default 0,
                        foreign key (user_id) references users(id),
                        foreign key (event_id) references classes(id),
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

# Sessions
cursor_sqlite.execute("""CREATE TABLE IF NOT EXISTS  "sessions" (
                    "id"	BLOB NOT NULL PRIMARY KEY UNIQUE DEFAULT (randomblob(16)),
                    "user_id"	INTEGER,
                    "user_type"	INTEGER,
                    "user_agent"	TEXT,
                    "last_ip"	TEXT,
                    "time"	TEXT,
                    FOREIGN KEY("user_id") REFERENCES "users"("id")
                  );
               """)
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
cursor_sqlite.execute("""CREATE TABLE IF NOT EXISTS  "feedback" (
                    "user_id"	INTEGER NOT NULL PRIMARY KEY,
                    "days"	TEXT,
                    "time"	TEXT DEFAULT(datetime('now','localtime')),
                    FOREIGN KEY("user_id") REFERENCES "users"("id")
                  );
               """)
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
# cursor.execute('''
#                     create table if not exists project_users (
#                         user_id serial,
#                         project_id serial,
#                         foreign key (user_id) references users(id)
#                         foreign key (project_id) references projects(id)
#                     );
#                     ''')

# Events
cursor_sqlite.execute("""CREATE TABLE IF NOT EXISTS  "events" (
                    "id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                    "type"	INTEGER,
                    "title"	TEXT,
                    "credits"	INTEGER,
                    "count" INTEGER DEFAULT (0),
                    "total" INTEGER,
                    "date" TEXT
                  );
               """)
# cursor.execute('''
#                     create table if not exists events (
#                         id serial not null primary key unique,
#                         type int,
#                         title text,
#                         credits int,
#                         count int default 0,
#                         total int,
#                         date text
#                     );
#                     ''')
cursor.execute('''
                    create table if not exists events (
                        id serial not null primary key unique,
                        type int,
                        title text,
                        description text,
                        host text,
                        place text,
                        time, text,
                        date text
                    );
                    ''')
cursor.execute('''
                    create table if not exists classes (
                        id serial not null primary key unique,
                        credits int,
                        count int default 0,
                        total int,
                        foreign key (id) references events(id)
                    );
                    ''')

conn.commit()


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


# TODO: Safety sql (if db is busy)
# TODO: delete  after migration
def safety_request(sql):
    """ Try to run sql code event if db is busy

    Args:
        sql: sql code - string

    Returns:
        None

    """

    timeout = 10

    for x in range(0, timeout):
        try:
            with conn_sqlite:
                conn_sqlite.execute(sql)
                conn_sqlite.commit()
        except sqlite3.Warning:  # TODO?
            time.sleep(1)
            pass

        finally:
            break
    else:
        with conn_sqlite:
            conn_sqlite.execute(sql)
            conn_sqlite.commit()


""" ---===---==========================================---===--- """
"""           SQLite database interaction via sqlite3            """
""" ---===---==========================================---===--- """


def get_users():
    """ Get all users from sql table

    Args:

    Returns:
        user objects: list of user objects - [(id, user_type, phone, name, pass, team, credits, avatar, project_id), ...]
    """
    cursor.execute('select * from users;')
    users_list = cursor.fetchall()
    # cursor.execute("SELECT * FROM users")
    # users_list = cursor.fetchall()

    return users_list


def clear_users():
    """ Clear all users from sql table

    Args:
    Returns:
    """
    cursor.execute('delete from users;')
    conn.commit()
    # cursor.execute("DELETE FROM users")
    # conn.commit()


def remove_user(user_id):
    """ Delete user by id

    Args:
        user_id: user id from db

    Returns:
        # Success delete or not

    """
    cursor.execute(f'delete from users where id = {user_id};')
    conn.commit()
    # cursor.execute("DELETE FROM users WHERE id=?", (user_id, ))
    # conn.commit()


# TODO: delete  after migration
def load_users(users_list):
    """ Load all users to sql table
    Clear users table and sessions table and insert all users in users table

    Args:
        users_list: list of user objects - [(id, user_type, phone, name, pass, team, credits, avatar, project_id), ...]

    Returns:

    """

    # Clear user and sessions tables
    # cursor.execute("DELETE FROM sessions")
    cursor_sqlite.execute("DELETE FROM users")
    conn_sqlite.commit()

    # Add users in bd
    for user_obj in users_list:
        if user_obj[7] is None:
            avatar = ""
        else:
            avatar = user_obj[7]

        cursor_sqlite.execute("""INSERT INTO users(id, user_type, phone, name, pass, team, credits, avatar)
                          SELECT ?, ?, ?, ?, ?, ?, ?, ?
                          WHERE NOT EXISTS(SELECT 1 FROM users WHERE name=? AND pass=?)""",
                              (user_obj[0], user_obj[1], user_obj[2], user_obj[3], user_obj[4], user_obj[5], user_obj[6], avatar, user_obj[3], user_obj[4]))
        conn_sqlite.commit()


def get_credits():
    """ Get all credits from sql table

    Args:

    Returns:
        credits objects: list of credits objects - [ (user_id, event_id, date, value), ...]

    """
    cursor.execute('select * from credits;')
    credits_list = cursor.fetchall()

    return credits_list


def get_credits(user_id):
    """ Get all credits of user from sql table

    Args:
        user_id: id of user for selecting

    Returns:
        credits objects: list of credits objects - [ (user_id, event_id, date, value), ...]

    """
    cursor.execute(f'select * from credits  where user_id = {user_id};')
    credits_list = cursor.fetchall()

    return credits_list


def remove_projects(credits_id):
    """ Delete credits by id

    Args:
        credits_id: projects id from bd

    Returns:
        # Success delete or not

    """
    cursor.execute(f'delete from credits where id = {credits_id};')
    conn.commit()


def get_projects():
    """ Get all projects from sql table

    Args:

    Returns:
        project objects: list of project objects - [ (id, title, type, def_type, direction, description), ...]

    """
    cursor.execute('select * from projects;')
    projects_list = cursor.fetchall()

    return projects_list


def remove_projects(projects_id):
    """ Delete projects by id

    Args:
        projects_id: projects id from bd

    Returns:
        # Success delete or not

    """
    cursor.execute(f'delete from projects where id = {projects_id};')
    conn.commit()


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


def remove_event(event_id):
    """ Delete event by id

    Args:
        event_id: event id from bd

    Returns:
        # Success delete or not

    """
    cursor.execute(f'delete from events where id = {event_id};')
    conn.commit()
    # cursor.execute("DELETE FROM events WHERE id=?", (event_id, ))
    # conn.commit()


# TODO: gsheets loading
def load_events(events_list):
    """ Load all events to sql table
    Clear events and insert all events in events table

    Args:
        events_list: list of event objects - [ (id, type, title, description, host, place, time, date), ...]

    Returns:

    """

    # Safe update events - save count of people
    for event_obj in events_list:
        cursor_sqlite.execute("""
                          INSERT OR IGNORE INTO events(id, type, title, credits, total, date)
                          VALUES (?, ?, ?, ?, ?, ?); 
                        """, (event_obj[0], event_obj[1], event_obj[2], event_obj[3], event_obj[4], event_obj[5],))
        cursor_sqlite.execute("""
                          UPDATE events SET type=?, title=?, credits=?, total=? WHERE id=?; 
                        """, (event_obj[1], event_obj[2], event_obj[3], event_obj[4], event_obj[0]))
    conn_sqlite.commit()

    return


def get_classes():
    """ Get all classes (events type) from sql table

    Args:

    Returns:
        class objects: list of event objects - [ (id, credits, count, total), ...]

    """
    cursor.execute('select * from classes;')
    classes_list = cursor.fetchall()

    return classes_list


def remove_class(class_id):
    """ Delete class by id

    Args:
        class_id: class id (event id) from bd

    Returns:
        # Success delete or not

    """
    cursor.execute(f'delete from classes where id = {class_id};')
    conn.commit()
    # cursor.execute("DELETE FROM events WHERE id=?", (event_id, ))
    # conn.commit()


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
    return sessions_list


def clear_sessions():
    """ Clear all sessions from sql table

    Args:
    Returns:
    """
    cursor.execute('delete from sessions;')
    conn.commit()
    # cursor.execute("DELETE FROM sessions")
    # conn.commit()


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


def edit_user(user_obj):
    """ Update user

    Args:
        user_obj: user obj (id, user_type, phone, name, pass, team, credits, project_id)

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
                                project_id = {user_obj[7]},
                            where id = {user_obj[0]};
                        ''')
    conn.commit()


def insert_user(user_obj):
    """ Insert user

    Args:
        user_obj: user obj (None, user_type, phone, name, pass, team, credits, project_id)

    Returns:
    """
    # test_conn = psycopg2.connect('dbname=root user=root password=root')
    # test_cursor = test_conn.cursor()
    # test_cursor.execute(f'call CreateOrModifyUser({user_obj[0]}, {user_obj[1]}, {user_obj[2]}, {user_obj[3]}, {user_obj[4]}, {user_obj[5]}, {user_obj[6]});')
    cursor.execute(f'insert into users (user_type, phone, name, pass, team, credits, project_id) values ({user_obj[1]}, \'{user_obj[2]}\', \'{user_obj[3]}\', {user_obj[4]}, {user_obj[5]}, {user_obj[6]}, {user_obj[7]}); ')
    # cursor.execute("REPLACE INTO users (user_type, phone, name, pass, team, credits)", user_obj[1:])
    conn.commit()
    # conn.commit()


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


def clear_events():
    """ Clear all events from sql table

    Args:
    Returns:
    """
    cursor.execute('delete from events;')
    conn.commit()
    # cursor.execute("DELETE FROM events")
    # conn.commit()


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


def edit_event(event_obj):
    """ Update event

    Args:
        event_obj: event obj (id, type, title, description, host, place, time, date)

    Returns:
    """
    cursor.execute(f'''update events set
                                type = {event_obj[1]},
                                title = \'{event_obj[2]}\',
                                description = {event_obj[3]},
                                host = {event_obj[4]},
                                place = {event_obj[5]},
                                time = \'{event_obj[6]}\'
                                date = \'{event_obj[7]}\'
                            where id = {event_obj[0]};
                        ''')
    conn.commit()


def insert_event(event_obj):
    """ Insert event

    Args:
        event_obj: event obj (None, type, title, description, host, place, time, date)

    Returns:
    """
    cursor.execute(f'insert into events (type, title, description, host, place, time, date) values ({event_obj[1]}, \'{event_obj[2]}\', {event_obj[3]}, {event_obj[4]}, {event_obj[5]}, \'{event_obj[6]}\', \'{event_obj[7]}\');')
    conn.commit()
    # cursor.execute("REPLACE INTO events (id, type, title, credits, count, total, date)", event_obj)
    # conn.commit()


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
    # cursor.execute("REPLACE INTO sessions (id, user_id, user_type, user_agent, last_ip, time)", sess_obj)
    # conn.commit()


def insert_session(sess_obj):
    """ Insert session

    Args:
        sess_obj: sess obj (None, user_id, user_type, user_agent, last_ip, time)

    Returns:
    """
    cursor.execute(f'insert into sessions (user_id, user_type, user_agent, last_ip, time) values ({sess_obj[1]}, {sess_obj[2]}, \'{sess_obj[3]}\', \'{sess_obj[4]}\', \'{sess_obj[5]}\');')
    conn.commit()
    # cursor.execute("REPLACE INTO sessions (id, user_id, user_type, user_agent, last_ip, time)", sess_obj)
    # conn.commit()


def remove_session(sess_id):
    """ Remove session by id

    See:
        logout
    """
    logout(sess_id)
