"""Module for basic PostgreSQL interaction via psycopg2"""
import typing as tp

import psycopg2
from psycopg2 import IntegrityError, DataError, ProgrammingError, OperationalError

""" ---===---==========================================---===--- """
"""         PostgreSQL database interaction via psycopg2         """
""" ---===---==========================================---===--- """

# initializing connection to database
# TODO: plain text user & password, great
conn = psycopg2.connect('dbname=root user=root password=root')
cursor = conn.cursor()


def checkpoint():
    # TODO: do we need checkpoint now? Maybe same flags should be set somehow in the PostgreSQL (need to check that)?
    # TODO: I dont f_ing know. Did you found where db file located?
    # TODO: yup, working on a container with automatic backup

    pass
    # conn_sqlite.execute("PRAGMA wal_checkpoint(TRUNCATE)")  # WAL
    # conn_sqlite.execute("VACUUM;")  # Repack database file


checkpoint()

# Projects
cursor.execute("""
    create table if not exists projects (
        id serial not null primary key,
        title text default '',
        type int default 0,
        def_type int default 0,
        direction text default '',
        description text default '',
        annotation text default ''
    );
""")

# Users
cursor.execute("""
    create table if not exists users (
        id serial not null primary key unique,
        user_type int default 0,
        phone text default '',
        name text default '',
        pass int,
        team int default 0,
        project_id int default 0,
        foreign key (project_id) references projects(id),
        avatar text default ''
    );
""")

# Sessions
cursor.execute("""
    CREATE OR REPLACE FUNCTION random_bytea(bytea_length integer)
    RETURNS bytea AS $$
    SELECT decode(string_agg(lpad(to_hex(width_bucket(random(), 0, 1, 256)-1),2,'0') ,''), 'hex')
    FROM generate_series(1, $1);
    $$
    LANGUAGE 'sql';
""")
cursor.execute("""
    create table if not exists sessions (
        id bytea not null primary key unique default random_bytea(16),
        user_id int,
        foreign key (user_id) references users(id),
        user_type int,
        user_agent text default '',
        last_ip text default '',
        time text default ''
    );
""")

# Days
cursor.execute("""
    create table if not exists days (
        id serial not null primary key unique,
        date text default '',
        title text default '',
        feedback bool default false
    );
""")

# Top
cursor.execute("""
    create table if not exists top (
        id serial not null primary key unique,
        user_id int,
        foreign key (user_id) references users(id),
        day_id int,
        foreign key (day_id) references days(id),
        chosen_1 int,
        foreign key (chosen_1) references users(id),
        chosen_2 int,
        foreign key (chosen_2) references users(id),
        chosen_3 int,
        foreign key (chosen_3) references users(id)
    );
""")

# Feedback
cursor.execute("""
    create table if not exists feedback (
        id serial not null primary key,
        user_id int,
        foreign key (user_id) references users(id),
        event_id int,
        foreign key (event_id) references events(id),
        score int,
        entertain int, -- assuming
        useful int,
        understand int, -- accessibly
        comment text default ''
    );
""")

# Events
cursor.execute("""
    create table if not exists events (
        id serial not null primary key unique,
        type int,
        title text default '',
        description text default '',
        host text default '',
        place text default '',
        time text default '',
        day_id int,
        foreign key (day_id) references days(id)
    );
""")

# Classes
cursor.execute("""
    create table if not exists classes (
        id int primary key,
        foreign key (id) references events(id),
        total int default 0,
        annotation text default ''
    );
""")

# Enrolls
cursor.execute("""
    create table if not exists enrolls (
        id serial not null primary key,
        class_id int,
        foreign key (class_id) references classes(id),
        user_id int,
        foreign key (user_id) references users(id),
        time text default '',
        attendance bool default false,
        bonus int default 0
    );
""")

# Credits
cursor.execute("""
    create table if not exists credits (
        id serial not null primary key,
        user_id int,
        foreign key (user_id) references users(id),
        event_id int,
        foreign key (event_id) references events(id),
        time text default '',
        value int default 0
    );
""")

# TODO: check if codes were created in a right way, just to make sure
# Codes
cursor.execute("""
    create table if not exists codes (
        id serial not null primary key,
        code text,
        type int default 0,
        used bool default false
    );
""")

# Vacations
cursor.execute("""
    create table if not exists vacations (
        id serial not null primary key unique,
        user_id int,
        foreign key (user_id) references users(id),
        date_from text default '',
        date_to text default '',
        time_from text default '',
        time_to text default ''
    );
""")

# cursor.execute("""
#                     create table if not exists project_users (
#                         user_id serial,
#                         project_id serial,
#                         foreign key (user_id) references users(id)
#                         foreign key (project_id) references projects(id)
#                     );
#                     """)

conn.commit()

TTableObject = tp.Dict[str, tp.Any]

# TODO: Remove ?
TUser = tp.Dict[str, tp.Any]
TSession = tp.Dict[str, tp.Any]
TCredit = tp.Dict[str, tp.Any]
TCode = tp.Dict[str, tp.Any]
TFeedback = tp.Dict[str, tp.Any]
TTop = tp.Dict[str, tp.Any]
TProject = tp.Dict[str, tp.Any]
TEvent = tp.Dict[str, tp.Any]
TClass = tp.Dict[str, tp.Any]
TEnroll = tp.Dict[str, tp.Any]
TDay = tp.Dict[str, tp.Any]
TVacation = tp.Dict[str, tp.Any]

table_fields = {
    'users': ('id', 'user_type', 'phone', 'name', 'pass', 'team', 'project_id', 'avatar'),
    'sessions': ('id', 'user_id', 'user_type', 'user_agent', 'last_ip', 'time'),
    'credits': ('id', 'user_id', 'event_id', 'time', 'value'),
    'codes': ('code', 'type', 'used'),
    'feedback': ('id', 'user_id', 'event_id', 'score', 'entertain', 'useful', 'understand', 'comment'),
    'top': ('id', 'user_id', 'chosen_1', 'chosen_2', 'chosen_3', 'day_id'),
    'projects': ('id', 'title', 'type', 'def_type', 'direction', 'description', 'annotation'),
    'events': ('id', 'type', 'title', 'description', 'host', 'place', 'time', 'day_id'),
    'classes': ('id', 'total', 'annotation'),
    'enrolls': ('id', 'class_id', 'user_id', 'time', 'attendance', 'bonus'),
    'days': ('id', 'date', 'title', 'feedback'),
    'vacations': ('id', 'user_id', 'date_from', 'date_to', 'time_from', 'time_to'),
}

""" ---===---==========================================---===--- """
"""           Auxiliary functions for sql interactions           """
""" ---===---==========================================---===--- """


def tuples_to_dicts(data_raw: tp.List[tp.Tuple[tp.Any]], table: str) -> tp.List[TTableObject]:
    data = []

    for line in data_raw:
        data.append({table_fields[table][i]: line[i] for i in range(len(table_fields[table]))})

    return data


def dict_to_tuple(data_raw: TTableObject, table: str) -> tp.Tuple[tp.Any]:
    data: tp.List[tp.Any] = []

    for field in table_fields[table]:
        try:
            if field == 'id' and data_raw[field] == '':
                data.append(None)  # No id. Replace by None
            else:
                data.append(data_raw[field])
        except KeyError:
            if table == 'events':
                cursor.execute(f"select (id) from days where date = '{data_raw['date']}'")
                id_ = cursor.fetchone()[0]
                data.append(id_)
            else:
                data.append(None)  # if no field

    return tuple(data)


def tuple_to_dict(data_raw: tp.Tuple[tp.Any], table: str) -> TTableObject:
    data: tp.Dict[str, tp.Any] = {}

    for i in range(len(table_fields[table])):
        data[table_fields[table][i]] = data_raw[i]

    return data


""" ---===---==========================================---===--- """
"""            Overall functions for sql interactions            """
""" ---===---==========================================---===--- """


def insert_to_table(data: TTableObject, table_name: str) -> int:
    """ Insert some object in some db table

    Args:
        data: dict witch should be insert (id=None)
        table_name: name of current table to insert

    Exceptions:
        raise

    Returns:
        id: return id of new element
    """

    if table_name == 'events':
        # Class event
        return insert_event(data)

    fields = ', '.join(table_fields[table_name])
    values_placeholder = ', '.join(['%s' for _ in fields])

    sql_string = f"INSERT INTO {table_name} ({fields}) VALUES ({values_placeholder}) RETURNING id;"

    cursor.execute(sql_string, dict_to_tuple(data, table_name))  # TODO: try catch
    hundred = cursor.fetchone()[0]

    return hundred


def update_in_table(data: TTableObject, table_name: str) -> None:
    """ Update some object in some db table

    Args:
        data: dict witch should be insert (id!=None)
        table_name: name of current table to insert

    Exceptions:
        raise
    """

    if table_name == 'events':
        edit_event(data)
        return

    values_placeholder = ', '.join([f'{field} = %s' for field in table_fields[table_name]])

    sql_string = f"UPDATE {table_name} SET {values_placeholder} WHERE id={data['id']};"

    cursor.execute(sql_string, dict_to_tuple(data, table_name))  # TODO: try catch
    conn.commit()


def get_in_table(data_id: int, table_name: str) -> TTableObject:
    """ Get some db object from table by id

    Args:
        data_id: obj id from bd
        table_name: name of current table to insert

    Returns:
        obj dictionary
    """

    if table_name == 'sessions':
        return get_session(data_id)

    sql_string = f'select * from {table_name} where id = %s;'

    cursor.execute(sql_string, (data_id,))
    obj = cursor.fetchone()

    return tuple_to_dict(obj, table_name)


def remove_in_table(data_id: int, table_name: str) -> None:
    """ Remove some object from some db table

    Args:
        data_id: id coordinated from table obj
        table_name: name of current table to insert

    Exceptions:
        raise
    """

    if data_id == 0:
        return

    if table_name == 'projects':
        remove_project(data_id)
        return

    if table_name == 'events' or table_name == 'classes':
        remove_event(data_id)
        return

    if table_name == 'users':
        remove_user(data_id)
        return

    if table_name == 'session':
        remove_session(data_id)
        return

    if table_name == 'enrolls':
        remove_enroll(data_id)
        return

    cursor.execute(f"DELETE FROM {table_name} where id = {data_id};")  # TODO: try catch
    conn.commit()


def get_table(table_name: str) -> tp.List[TTableObject]:
    """ Get all objects from sql table

    Args:
        table_name: name of db table

    Returns:
        objects dicts fetched from sql table
    """

    if table_name == 'sessions':
        return get_sessions()

    cursor.execute(f'SELECT * FROM {table_name};')  # TODO: try catch
    objects_list = cursor.fetchall()

    return tuples_to_dicts(objects_list, table_name)


def clear_table(table_name: str) -> None:
    """ Remove all objects from sql table (EXCEPT id==0)

    Args:
        table_name: name of db table
    """

    if table_name == 'classes' or table_name == 'events':
        clear_events()

    if table_name == 'users':
        clear_users()

    cursor.execute(f'DELETE FROM {table_name} WHERE id != 0;')  # TODO: try catch
    conn.commit()


""" ---===---==========================================---===--- """
"""            Special functions for sql interactions            """
""" ---===---==========================================---===--- """


# Projects
def remove_project(project_id: int) -> None:
    """ Delete project by id

    Args:
        project_id: projects id from bd

    Returns:
        # Success delete or not
    """

    if project_id in (0, '0'):
        return

    cursor.execute(f'update users set project_id = 0 where project_id = {project_id};')
    cursor.execute(f'delete from projects where id = {project_id};')
    conn.commit()


# Days


# Vacations


# Users
def get_names() -> tp.List[TTableObject]:
    """ Get all users short list from sql table

    Args:

    Returns:
        user short objects: list of user objects - [(id, name, team, project_id), ...]
    """

    cursor.execute('select * from users;')
    users_list = cursor.fetchall()

    return [{'id': user[0], 'name': user[3], 'team': user[5], 'project_id': user[7]} for user in users_list]
    # TODO: only if type == 0


def get_user_by_phone(phone: str) -> tp.Optional[TTableObject]:
    """ Get user obj by phone

    Args:
        phone: phone - str

    Returns:
        user_obj: (id, user_type, phone, name, pass, team, credits, avatar, project_id)
                     or None if there is no such user
    """

    cursor.execute(f"select * from users where phone = '{phone}';")
    user = cursor.fetchone()
    return tuple_to_dict(user, 'users')


def register(name, passw, type_, phone, team) -> bool:
    """ Register new user
    There is no verification - create anywhere

    Args:
        name: User name - string
        passw: Password hash - int
        type_: User type - int  [0 - USER, 1 - HOST, 2 - ADMIN]
        phone: phone - string
        team: number of group - int

    Note:
        user id is automatically generated

    Returns:
        Sucsess reg or not
    """

    # TODO: change to PostgreSQL
    cursor.execute(f'select * from users where name = \'{name}\' and pass = {passw};')
    existing_users = cursor.fetchall()
    if len(existing_users) != 0:
        return False

    cursor.execute(f"""
        insert into users (user_type, phone, name, pass, team)
        values ({type_},
               '{phone}',
               '{name}',
                {passw},
                {team});
    """)
    conn.commit()
    return True


# TODO: ?
def checkin_user(user_obj: int, event_obj: int) -> None:
    """ Checkin user in event
    Add user credits for the event

    Args:
        user_obj: (id, user_type, phone, name, pass, team, credits, avatar, project_id)
        event_obj: (id, type, title, credits, count, total, date)
    """
    # TODO: ?
    pass
    # cursor.execute(f'update users set credits = {event_obj[3] + user_obj[6]} where id = {user_obj[0]};')
    # conn.commit()


def remove_user(user_id: int) -> bool:
    """ Delete user by id

    Args:
        user_id: user id from db

    Returns:
        Successful delete or not
    """

    try:
        cursor.execute(f'delete from sessions where user_id = {user_id};')
        cursor.execute(f'delete from feedback where user_id = {user_id};')
        cursor.execute(f'delete from credits where user_id = {user_id};')
        cursor.execute(f'delete from top where user_id = {user_id};')
        cursor.execute(f'delete from enrolls where user_id = {user_id};')
        cursor.execute(f'delete from users where id = {user_id};')
        conn.commit()
        return True
    except (IntegrityError, DataError, ProgrammingError, OperationalError) as err:
        print(f"Encountered error: {err}")
        return False


def clear_users() -> None:
    """Clear all users from sql table"""

    # TODO: probably won't succeed due to ForeignKeyViolation error, see the method above
    cursor.execute('delete from users;')
    conn.commit()


# Sessions
def get_sessions() -> tp.List[TTableObject]:
    """Get all sessions from sql table

    Returns:
        session objects: list of sess objects - [ (id, user_id, user_type, user_agent, last_ip, time), ...]
    """

    cursor.execute('select * from sessions;')
    sessions_list = cursor.fetchall()

    for index, element in enumerate(sessions_list):
        sessions_list[index] = ((element[0]).hex(), *element[1:])

    return tuples_to_dicts(sessions_list, 'sessions')


def get_session(sess_id: int) -> tp.Optional[TTableObject]:
    """ Get session obj by id

    Args:
        sess_id: session id from db

    Returns:
        session obj: (id, user_id, user_type, user_agent, last_ip, time)
                     or None if there is no such session
    """

    cursor.execute(f"select * from sessions where id = bytea \'\\x{sess_id}\';")
    sess = cursor.fetchone()

    return tuple_to_dict(sess, 'sessions')


# TODO: Update time in sessions
def login(phone: str, passw: str, agent: str, ip: str, time_: str = '0'):
    """ Login user
    Create new session if it does not exist and return sess id

    Args:
        phone: User phone - string
        passw: Password hash - int
        agent: User agent - string
        ip: ip - string
        time_: time of session creation

    Note:
        session id is automatically generated

    Returns:
        sess_id: session id - string of hex
                 b'\xbeE%-\x8c\x14y3\xd8\xe1ui\x03+D\xb8' -> be45252d8c147933d8e17569032b44b8
    """

    # Check user with name and pass exist and got it
    cursor.execute(f"select * from users where phone = '{phone}' and pass = {passw};")
    users = cursor.fetchall()

    if len(users) == 0:  # No such user
        return None

    user = users[0]

    # Create new session if there is no session with user_id and user_agent
    cursor.execute(f"select * from sessions where user_id = {user[0]} and user_agent = '{agent}';")
    existing_sessions = cursor.fetchall()
    if len(existing_sessions) == 0:
        cursor.execute(f"""
            insert into sessions (user_id, user_type, user_agent, last_ip, time)
            values ({user[0]}, {user[1]}, '{agent}', '{ip}', '{time_}');
        """)
        conn.commit()

    # Get session corresponding to user_id and user_agent
    cursor.execute(f"select * from sessions where user_id = {user[0]} and user_agent = '{agent}';")
    result = cursor.fetchone()

    print(f'session got by login:{result}')
    return result


def remove_session(sess_id: int) -> bool:
    """ Remove session by id

    See:
        logout
    """

    return logout(sess_id)


# TODO: both remove_session() and logout() needed?
def logout(sess_id: int) -> bool:
    """ Delete current session by sessid

    Args:
        sess_id: session id from bd

    Returns:
        Success delete or not
    """

    cursor.execute(f'select * from sessions where id = bytea \'\\x{sess_id}\';')
    sessions = cursor.fetchall()

    if len(sessions) == 0:  # No such session
        return False

    cursor.execute(f'delete from sessions where id = bytea \'\\x{sess_id}\';')
    conn.commit()
    return True


# Events
def get_day(date: str) -> tp.List[TTableObject]:
    """ Get all events for some day from sql table

    Args:
        date: dd.mm day for select data

    Returns:
        event objects: list of event objects - [ (id, type, title, description, host, place, time, date), ...]
    """

    cursor.execute(f"select (id) from days where date = '{date}'")
    # TODO: maybe [0] is not needed
    day_id = int(cursor.fetchone()[0])

    cursor.execute(f"select * from events where day_id = {day_id};")
    events_list = cursor.fetchall()

    return tuples_to_dicts(events_list, 'events')


def insert_event(event_obj: TTableObject) -> int:
    """ Insert event

    Args:
        event_obj: event obj (None, type, title, description, host, place, time, date)

    Returns:
        id: id of the created event
    """

    try:
        cursor.execute(f"select (id) from days where date = {event_obj['date']}")
        day_id = cursor.fetchone()
        event_obj['day_id'] = day_id
    except KeyError:
        pass

    values_placeholder = ', '.join(['%s' for _ in table_fields['events']])

    sql_string = f"INSERT INTO events (type, title, description, host, place, time, day_id) " \
                 f"VALUES ({values_placeholder}) RETURNING id;"

    cursor.execute(sql_string, dict_to_tuple(event_obj, 'events'))  # TODO: try catch
    event_id = cursor.fetchone()[0]

    if int(event_obj['type']) != 0:
        # class
        cursor.execute(f'INSERT INTO classes (id, total, annotation) VALUES ({event_id}, 0, '');')
    else:
        # regular
        pass

    conn.commit()
    return event_id


def edit_event(event_obj: TTableObject) -> None:
    """ Update event

    Args:
        event_obj: event obj (id, type, title, description, host, place, time, day_id)
    """

    # TODO: Check Changed type -> create or delete
    # TODO: Change values to exec
    cursor.execute(f"""
        update events set
            type = {event_obj['type']},
            title = '{event_obj['title']}',
            description = '{event_obj['description']}',
            host = '{event_obj['host']}',
            place = '{event_obj['place']}',
            time = '{event_obj['time']}',
            day_id = {event_obj['day_id']}
        where id = {event_obj['id']};
    """)
    conn.commit()


def remove_event(event_id: int) -> None:
    """ Delete event by id

    Args:
        event_id: event id from bd

    Returns:
        # Success delete or not

    """
    if event_id in (0, '0'):
        return

    try:
        cursor.execute(f'update credits set event_id = 0 where event_id = {event_id};')
        cursor.execute(f'delete from classes where id = {event_id};')
        cursor.execute(f'delete from events where id = {event_id};')
    except (IntegrityError, DataError, ProgrammingError, OperationalError) as error:
        print(error)
        cursor.execute('rollback;')
    conn.commit()


def clear_events() -> None:
    """ Clear all events from sql table """
    cursor.execute('delete from classes where id != 0;')
    cursor.execute('delete from events where id != 0;')
    conn.commit()


# Classes
def check_class(class_id: int) -> bool:
    """ Check class have empty places

    Args:
        class_id: class id (event id) from bd

    Returns:
        bool - True - has places
    """

    cursor.execute(f"select count(*) from enrolls where class_id = {class_id};")
    enrolled = cursor.fetchone()[0]

    cursor.execute(f'select * from classes where id = {class_id};')
    class_obj = cursor.fetchone()

    if class_obj is None:
        return False

    return enrolled < class_obj[1]


def enroll_user(class_id: int, user_obj: TTableObject, time_: str = '0') -> bool:  # TODO?
    """ Enroll user in event

    Args:
        class_id: class id (event id) from bd
        user_obj: (id, user_type, phone, name, pass, team, credits)
        time_: time str

    Returns:
        True/False: Success or not
    """

    cursor.execute(f'select * from class where id = {class_id};')
    class_ = cursor.fetchone()

    cursor.execute(f"select count(*) from enrolls where class_id = {class_id};")
    enrolled = cursor.fetchone()[0]

    if not class_ or enrolled >= class_[1]:  # No such event or too many people
        return False

    cursor.execute(
        f"insert into enrolls (class_id, user_id, time, attendance, bonus) "
        f"values ({class_id}, {user_obj[0]}, {time_}, false, 0);")
    conn.commit()
    return True


def remove_class(class_id: int) -> None:
    """ Delete class by id

    Args:
        class_id: class id (event id) from bd

    Returns:
        # Success delete or not
    """

    remove_event(class_id)


# Enrolls
def get_enrolls_by_event_id(event_id: int) -> tp.List[TTableObject]:
    """ Get enrolls obj by id

    Args:
        event_id: event id from bd

    Returns:
        enroll_objs: [(id, class_id, users_id, time, attendance), ...]
    """

    cursor.execute(f'select * from enrolls where class_id = {event_id};')
    enrolls = cursor.fetchall()

    if len(enrolls) == 0:  # No such enrolls
        return []

    return enrolls


def get_enrolls_by_user_id(user_id: int) -> tp.List[TTableObject]:
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

    return enrolls


def remove_enroll(enroll_id: int) -> None:
    """ Delete enroll by id

    Args:
        enroll_id: enroll id from bd

    Returns:
        # Success delete or not
    """

    cursor.execute(f'select * from enrolls where id = {enroll_id};')
    enroll = cursor.fetchone()

    # event_id = enroll[1]

    # cursor.execute(f'select * from classes where id = {event_id};')
    # event = cursor.fetchone()
    # cursor.execute(f'update classes set count = {event[2] - 1} where id = {event_id};')

    cursor.execute(f'delete from enrolls where id = {enroll_id};')
    cursor.execute(f"delete from credits where user_id = {enroll[2]} and class_id = {enroll[1]};")
    conn.commit()
    # TODO: Check (and think) if there are credits according this event. delete it
    # TODO: done, check it out


# Credits
def get_credits_by_user_id(user_id: int) -> tp.List[TTableObject]:
    """ Get all credits of user from sql table

    Args:
        user_id: id of user for selecting

    Returns:
        credits objects: list of credits objects - [ (id, user_id, event_id, date, value), ...]
    """

    cursor.execute(f'select * from credits where user_id = {user_id};')
    credits_list = cursor.fetchall()

    return credits_list


def pay_credit(user_id: int, event_id: int, value: int = 0, time_: str = '0') -> None:
    """ Insert credit for user

    Args:
        user_id: user id from db
        event_id: event id from db
        value: int number of credits
        time_: current time str
    """

    cursor.execute(f'select * from credits where event_id = {event_id} and user_id = {user_id};')
    credits_ = cursor.fetchall()
    if len(credits_) == 0:
        cursor.execute(f"insert into credits (id, user_id, event_id, time, value) "
                       f"values (default, {user_id}, {event_id}, '{time_}', {value});")
    else:
        cursor.execute(f"update credits set value = {value} where id = {credits_[0][0]};")
    # TODO: Make execute params
    conn.commit()


# Codes
def load_codes(codes: tp.List[TTableObject]) -> bool:
    """ Cleat codes table and setup from codes

    Args:
        codes: codes list - [(str, int), (str, int), ... ]

    Returns:
        bool: successful call to DB or not
    """
    try:
        for code in codes:
            cursor.execute(f"insert into codes (code, type, used) values ('{code[0]}', {code[1]}, false);")
        conn.commit()
        return True
    except (IntegrityError, DataError, ProgrammingError, OperationalError) as err:
        print(f"error: {err}")
        return False


def use_code(code: str) -> bool:
    """ Set code used

    Args:
        code: code from bd

    Returns:
        Success delete or not

    """
    cursor.execute(f"select * from codes where code = '{code}';")
    code = cursor.fetchone()

    if not code or code[2]:
        return False

    cursor.execute(f"update codes set used = true where code = '{code}';")
    conn.commit()
    return True
