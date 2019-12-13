import sqlite3
import time
import string
import psycopg2


""" ---===---==========================================---===--- """
"""                    SQLite database creation                  """
""" ---===---==========================================---===--- """

test_conn = psycopg2.connect('dbname=root user=root password=root')
test_cursor = test_conn.cursor()
conn = sqlite3.connect("/home/ubuntu/db/main.sqlite", check_same_thread=False)
conn.execute("PRAGMA journal_mode=WAL")  # https://www.sqlite.org/wal.html
conn.execute("PRAGMA wal_autocheckpoint=100")
conn.execute("PRAGMA busy_timeout=1000")
conn.execute("PRAGMA synchronous=1")

cursor = conn.cursor()


def checkpoint():
    conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")  # WAL
    conn.execute("VACUUM;")  # Repack database file

checkpoint()

# Users
cursor.execute("""CREATE TABLE IF NOT EXISTS  "users" (
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
test_cursor.execute('''
                    create table if not exists users (
                        id serial not null primary key unique,
                        user_type int,
                        phone text,
                        name text,
                        pass int,
                        team int,
                        credits int default 0,
                        avatar text default ''
                    ); 
                    ''')

# Sessions
cursor.execute("""CREATE TABLE IF NOT EXISTS  "sessions" (
                    "id"	BLOB NOT NULL PRIMARY KEY UNIQUE DEFAULT (randomblob(16)),
                    "user_id"	INTEGER,
                    "user_type"	INTEGER,
                    "user_agent"	TEXT,
                    "last_ip"	TEXT,
                    "time"	TEXT,
                    FOREIGN KEY("user_id") REFERENCES "users"("id")
                  );
               """)
test_cursor.execute('''
                    create table if not exists sessions (
                        id serial not null primary key unique,
                        user_id int,
                        user_type int,
                        user_agent text,
                        last_ip text,
                        time text,
                        foreign key (user_id) references users(id)
                    );
                    ''')


# Feedback: voted or not
cursor.execute("""CREATE TABLE IF NOT EXISTS  "feedback" (
                    "user_id"	INTEGER NOT NULL PRIMARY KEY,
                    "days"	TEXT,
                    "time"	TEXT DEFAULT(datetime('now','localtime')),
                    FOREIGN KEY("user_id") REFERENCES "users"("id")
                  );
               """)
test_cursor.execute("""
                    create table if not exists feedback (
                        user_id int not null primary key,
                        days text,
                        time text default 'datetime(''now'', ''localtime'')'
                    );
                    """)


# Events
cursor.execute("""CREATE TABLE IF NOT EXISTS  "events" (
                    "id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                    "type"	INTEGER,
                    "title"	TEXT,
                    "credits"	INTEGER,
                    "count" INTEGER DEFAULT (0),
                    "total" INTEGER,
                    "date" TEXT
                  );
               """)
test_cursor.execute('''
                    create table if not exists events (
                        id serial not null primary key unique,
                        type int,
                        title text,
                        credits int,
                        count int default 0,
                        total int,
                        date text
                    );
                    ''')
test_conn.commit()


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

    return param


# TODO: Safety sql (if db is busy)
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
            with conn:
                conn.execute(sql)
                conn.commit()
        except sqlite3.Warning:  # TODO?
            time.sleep(1)
            pass

        finally:
            break
    else:
        with conn:
            conn.execute(sql)
            conn.commit()


""" ---===---==========================================---===--- """
"""           SQLite database interaction via sqlite3            """
""" ---===---==========================================---===--- """


def get_users():
    """ Get all users from sql table

    Args:

    Returns:
        user objects: list of user objects - [(id, user_type, phone, name, pass, team, credits, avatar), ...]
    """
    test_cursor.execute('select * from users;')
    users_list = test_cursor.fetchall()
    # cursor.execute("SELECT * FROM users")
    # users_list = cursor.fetchall()

    return users_list


def clear_users():
    """ Clear all users from sql table

    Args:
    Returns:
    """
    test_cursor.execute('delete from users;')
    test_conn.commit()
    # cursor.execute("DELETE FROM users")
    # conn.commit()


def remove_user(user_id):
    """ Delete user by id

    Args:
        user_id: user id from db

    Returns:
        # Success delete or not

    """
    test_cursor.execute(f'delete from users where id = {user_id};')
    test_conn.commit()
    # cursor.execute("DELETE FROM users WHERE id=?", (user_id, ))
    # conn.commit()


# TODO: delete  after migration
def load_users(users_list):
    """ Load all users to sql table
    Clear users table and sessions table and insert all users in users table

    Args:
        users_list: list of user objects - [(id, user_type, phone, name, pass, team, credits, avatar), ...]

    Returns:

    """

    # Clear user and sessions tables
    # cursor.execute("DELETE FROM sessions")
    cursor.execute("DELETE FROM users")
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


def get_events():
    """ Get all events from sql table

    Args:

    Returns:
        event objects: list of event objects - [ (id, type, title, credits, total, date), ...]

    """
    test_cursor.execute('select * from events;')
    events_list = test_cursor.fetchall()
    # cursor.execute("SELECT * FROM events")
    # events_list = cursor.fetchall()

    return events_list


def remove_event(event_id):
    """ Delete user by id

    Args:
        event_id: event id from bd

    Returns:
        # Success delete or not

    """
    test_cursor.execute(f'delete from events where id = {event_id};')
    test_conn.commit()
    # cursor.execute("DELETE FROM events WHERE id=?", (event_id, ))
    # conn.commit()


# TODO: delete after migration
def load_events(events_list):
    """ Load all users to sql table
    Clear users table and sessions table and insert all users in users table

    Args:
        events_list: list of event objects - [ (id, type, title, credits, total, date), ...]

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

    # cursor.execute("DELETE FROM events")
    # conn.commit()
    #
    # for event_obj in events_list:
    #     cursor.execute("""INSERT INTO events(id, type, title, credits, total)
    #                       SELECT ?, ?, ?, ?, ?
    #                       WHERE NOT EXISTS(SELECT 1 FROM events WHERE title=?)""",
    #                    (event_obj[0], event_obj[1], event_obj[2], event_obj[3], event_obj[4], event_obj[2]))
    #     conn.commit()


def get_sessions():
    """ Get all sessions from sql table

    Args:

    Returns:
        session objects: list of sess objects - [ (id, user_id, user_type, user_agent, last_ip, time), ...]

    """
    test_cursor.execute('select * from sessions;')
    sessions_list = test_cursor.fetchall()
    # cursor.execute("SELECT * FROM sessions")
    # sessions_list = cursor.fetchall()
    return sessions_list


def clear_sessions():
    """ Clear all sessions from sql table

    Args:
    Returns:
    """
    test_cursor.execute('delete from sessions;')
    test_conn.commit()
    # cursor.execute("DELETE FROM sessions")
    # conn.commit()


def get_session(sess_id):
    """ Get session obj by id

    Args:
        sess_id: session id from bd

    Returns:
        session obj: (id, user_id, user_type, user_agent, last_ip, time)
                     or None if there is no such session

    """
    test_cursor.execute(f'select * from sessions where id = {sess_id};')
    sessions = test_cursor.fetchall()
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
    test_cursor.execute(f'select * from sessions where id = {sess_id};')
    sessions = test_cursor.fetchall()
    # cursor.execute("SELECT * FROM sessions WHERE id=?", (sess_id, ))
    # sessions = cursor.fetchall()

    if len(sessions) == 0:    # No such session
        return False

    test_cursor.execute(f'delete from sessions where id = {sess_id};')
    test_conn.commit()
    # cursor.execute("DELETE FROM sessions WHERE id=?", (sess_id, ))
    # conn.commit()
    return True


def get_user(user_id):
    """ Get user obj by id

    Args:
        user_id: user id from bd

    Returns:
        user_obj: (id, user_type, phone, name, pass, team, credits)
                     or None if there is no such user

    """
    test_cursor.execute(f'select * from users where id = {user_id};')
    users = test_cursor.fetchall()
    # cursor.execute("SELECT * FROM users WHERE id=?", (user_id, ))
    # users = cursor.fetchall()

    if len(users) == 0:    # No such user
        return None
    else:
        return users[0]


def edit_user(user_obj):
    """ Update user

    Args:
        user_obj: user obj (id, user_type, phone, name, pass, team, credits)

    Returns:
    """
    # test_cursor.execute(f'call CreateOrModifyUser({user_obj[0]}, {user_obj[1]}, {user_obj[2]}, {user_obj[3]}, {user_obj[4]}, {user_obj[5]}, {user_obj[6]});')
    test_cursor.execute(f'''update users set
                                user_type = {user_obj[1]},
                                phone = \'{user_obj[2]}\',
                                name = \'{user_obj[3]}\',
                                pass = {user_obj[4]},
                                team = {user_obj[5]},
                                credits = {user_obj[6]}
                            where id = {user_obj[0]};
                        ''')
    test_conn.commit()


def insert_user(user_obj):
    """ Insert user

    Args:
        user_obj: user obj (None, user_type, phone, name, pass, team, credits)

    Returns:
    """
    # test_conn = psycopg2.connect('dbname=root user=root password=root')
    # test_cursor = test_conn.cursor()
    # test_cursor.execute(f'call CreateOrModifyUser({user_obj[0]}, {user_obj[1]}, {user_obj[2]}, {user_obj[3]}, {user_obj[4]}, {user_obj[5]}, {user_obj[6]});')
    test_cursor.execute(f'insert into users (user_type, phone, name, pass, team, credits) values ({user_obj[1]}, \'{user_obj[2]}\', \'{user_obj[3]}\', {user_obj[4]}, {user_obj[5]}, {user_obj[6]}); ')
    # cursor.execute("REPLACE INTO users (user_type, phone, name, pass, team, credits)", user_obj[1:])
    test_conn.commit()
    # conn.commit()


def get_user_by_phone(phone):
    """ Get user obj by phone

    Args:
        phone: phone - str

    Returns:
        user_obj: (id, user_type, phone, name, pass, team, credits)
                     or None if there is no such user

    """
    test_cursor.execute(f'select * from users where phone = {phone};')
    users = test_cursor.fetchall()
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
    test_cursor.execute('delete from events;')
    test_conn.commit()
    # cursor.execute("DELETE FROM events")
    # conn.commit()


def get_event(event_id):
    """ Get event obj by id

    Args:
        event_id: event id from bd

    Returns:
        event_obj: (id, type, title, credits, count, total, date)
    """
    test_cursor.execute(f'select * from events where id = {event_id};')
    events = test_cursor.fetchall()
    # cursor.execute("SELECT * FROM events WHERE id=?", (event_id, ))
    # events = cursor.fetchall()

    if len(events) == 0:  # No such event
        return None
    else:
        return events[0]


def edit_event(event_obj):
    """ Update event

    Args:
        event_obj: event obj (id, type, title, credits, count, total, date)

    Returns:
    """
    test_cursor.execute(f'''update events set
                                type = {event_obj[1]},
                                title = \'{event_obj[2]}\',
                                credits = {event_obj[3]},
                                count = {event_obj[4]},
                                total = {event_obj[5]},
                                date = \'{event_obj[6]}\'
                            where id = {event_obj[0]};
                        ''')
    test_conn.commit()
    # cursor.execute("REPLACE INTO events (id, type, title, credits, count, total, date)", event_obj)
    # conn.commit()


def insert_event(event_obj):
    """ Insert event

    Args:
        event_obj: event obj (None, type, title, credits, count, total, date)

    Returns:
    """
    test_cursor.execute(f'insert into events (type, title, credits, count, total, date) values ({event_obj[1]}, \'{event_obj[2]}\', {event_obj[3]}, {event_obj[4]}, {event_obj[5]}, \'{event_obj[6]}\');')
    test_conn.commit()
    # cursor.execute("REPLACE INTO events (id, type, title, credits, count, total, date)", event_obj)
    # conn.commit()


def enroll_user(event_id, user_obj):
    """ Enroll user in event

    Args:
        event_id: event id from bd
        user_obj: (id, user_type, phone, name, pass, team, credits)

    Returns:
        True/False: Success or not
    """

    test_cursor.execute(f'select * from events where id = {event_id};')
    events = test_cursor.fetchall()
    # cursor.execute("SELECT * FROM events WHERE id=?", (event_id, ))
    # events = cursor.fetchall()

    if len(events) == 0 or events[0][4] >= events[0][5]:  # No such event or too many people
        return False

    test_cursor.execute(f'update events set count = {events[0][4] + 1} where id = {event_id};')
    test_conn.commit()
    # cursor.execute("UPDATE events SET count=? WHERE id=?", (events[0][4] + 1, event_id, ))
    # conn.commit()
    return True


def checkin_user(user_obj, event_obj):
    """ Checkin user in event
    Add user credits for the event

    Args:
        user_obj: (id, user_type, phone, name, pass, team, credits)
        event_obj: (id, type, title, credits, count, total, date)

    Returns:
    """
    test_cursor.execute(f'update users set credits = {event_obj[3] + user_obj[6]} where id = {user_obj[0]};')
    test_conn.commit()
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
    # Register new user if there is no user with name and pass
    cursor.execute("""INSERT INTO users(user_type, phone, name, pass, team)
                      SELECT ?, ?, ?, ?, ?
                      WHERE NOT EXISTS(SELECT 1 FROM users WHERE name=? AND pass=?)""",
                   (type, phone, name, passw, team, name, passw))
    conn.commit()


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
    # TODO: change to PostgreSQL
    # Check user with name and pass exist and got it
    cursor.execute("SELECT * FROM users WHERE phone=? AND pass=?", (phone, passw))
    users = cursor.fetchall()

    if len(users) == 0:    # No such user
        return None

    user = users[0]

    # Create new session if there is no session with user_id and user_agent
    cursor.execute("""INSERT INTO sessions(user_id, user_type, user_agent, last_ip, time)
                      SELECT ?, ?, ?, ?, ?
                      WHERE NOT EXISTS(SELECT 1 FROM sessions WHERE user_id=? AND user_agent=?)""",
                   (user[0], user[1], agent, ip, time, user[0], agent))
    conn.commit()


    # Get session corresponding to user_id and user_agent
    cursor.execute("SELECT * FROM sessions WHERE user_id=? AND user_agent=?", (user[0], agent))
    result = cursor.fetchone()

    return result


def edit_session(sess_obj):
    """ Update session

    Args:
        sess_obj: sess obj (id, user_id, user_type, user_agent, last_ip, time)

    Returns:
    """
    test_cursor.execute(f'''update sessions set
                                user_id = {sess_obj[1]},
                                user_type = {sess_obj[2]},
                                user_agent = \'{sess_obj[3]}\',
                                last_ip = \'{sess_obj[4]}\',
                                time = \'{sess_obj[5]}\'
                            where id = {sess_obj[0]};
                        ''')
    test_conn.commit()
    # cursor.execute("REPLACE INTO sessions (id, user_id, user_type, user_agent, last_ip, time)", sess_obj)
    # conn.commit()


def insert_session(sess_obj):
    """ Insert session

    Args:
        sess_obj: sess obj (None, user_id, user_type, user_agent, last_ip, time)

    Returns:
    """
    test_cursor.execute(f'insert into sessions (user_id, user_type, user_agent, last_ip, time) values ({sess_obj[1]}, {sess_obj[2]}, \'{sess_obj[3]}\', \'{sess_obj[4]}\', \'{sess_obj[5]}\');')
    test_conn.commit()
    # cursor.execute("REPLACE INTO sessions (id, user_id, user_type, user_agent, last_ip, time)", sess_obj)
    # conn.commit()


def remove_session(sess_id):
    """ Remove session by id

    See:
        logout
    """
    logout(sess_id)







""" TEST """
# sql.register('user', 6445723, 0, '+7 915', 0)
# sql.register('Hasd Trra', 23344112, 0, '+7 512', 0)
# sql.register('ddds Ddsa', 33232455, 0, '+7 333', 1)
# sql.register('aiuy Ddsa', 44542234, 0, '+7 234', 1)
# sql.register('AArruyaa Ddsa', 345455, 1, '+7 745', 1)
# sql.register('AAaa ryui', 23344234523112, 0, '+7 624', 0)
# sql.register('AAruiria', 563563265, 0, '+7 146', 0)
#
#
# print( sql.login('Name', 22222331, 'Gggg', '0:0:0:0') )
# a = sql.login('user', 6445723, 'AgentUserAgent', '0:0:0:0')
# print(a[0])
# print(a[0].hex() )
# print( sql.login('AAaa ryui', 23344234523112, 'Agent', '0:0:0:0') )

