"""Module for basic PostgreSQL interaction via psycopg2"""
import time
import typing as tp
import copy

import psycopg2

from utils.auxiliary import logger


""" ---===---==========================================---===--- """
"""         PostgreSQL database interaction via psycopg2         """
""" ---===---==========================================---===--- """


# TODO: cover all db-related try_catch with NAMES OF THE FUNCTIONS where they were triggered
# TODO: carefully check all db-related stuff against https://www.psycopg.org/docs/usage.html#transactions-control
# initializing connection to database
# TODO: plain text user & password, great
init_successful = False
conn = None
while not init_successful:
    try:
        conn = psycopg2.connect(dbname='ihse', user='postgres', password='root', host='database')
    except psycopg2.Error as error_:
        logger('sql', f'Initialization error: {error_}', type_='ERROR')
        init_successful = False
        logger('sql', 'Initialization waiting for 3 seconds', type_='LOG')
        time.sleep(3)
        continue
    init_successful = True
logger('sql', 'psycopg2.connect() initialized successfully', type_='LOG')


def checkpoint():
    # TODO: do we need checkpoint now? Maybe same flags should be set somehow in the PostgreSQL (need to check that)?
    # TODO: I dont f_ing know. Did you found where db file located?
    # TODO: yup, working on a container with automatic backup

    old_isolation_level = conn.isolation_level
    conn.set_isolation_level(0)
    with conn.cursor() as cursor_:
        try:
            cursor_.execute("VACUUM FULL;")  # Repack database file and re ANALYZE
        except psycopg2.Error as error_:
            logger('sql.checkpoint', f'VACUUM error; {error_}', type_='ERROR')
    conn.commit()
    conn.set_isolation_level(old_isolation_level)
    conn.commit()


checkpoint()


try:
    with conn.cursor() as cursor_:
        # Projects
        cursor_.execute("""
            create table if not exists projects (
                id serial not null primary key,
                title text default '',
                type text default '',
                def_type text default '',
                direction text default '',
                description text default '',
                annotation text default ''
            );
        """)

        # Users
        # TODO: rename user_type to type
        cursor_.execute("""
            create table if not exists users (
                id serial not null primary key unique,
                code text not null unique,
                user_type int default 0,
                phone text default '',
                name text default '',
                sex bool,
                pass int,
                team int default 0,
                project_id int default 0,
                foreign key (project_id) references projects(id),
                avatar text default ''
            );
        """)

        # Sessions
        cursor_.execute("""
            CREATE OR REPLACE FUNCTION random_bytea(bytea_length integer)
            RETURNS bytea AS $$
            SELECT decode(string_agg(lpad(to_hex(width_bucket(random(), 0, 1, 256)-1),2,'0') ,''), 'hex')
            FROM generate_series(1, $1);
            $$
            LANGUAGE 'sql';
        """)
        cursor_.execute("""
            create table if not exists sessions (
                id bytea not null primary key unique default random_bytea(16),
                user_id int,
                foreign key (user_id) references users(id),
                user_type int default 0,
                user_agent text default '',
                last_ip text default '',
                time text default ''
            );
        """)

        # Days
        cursor_.execute("""
            create table if not exists days (
                id serial not null primary key unique,
                date text default '',
                title text default '',
                feedback bool default false
            );
        """)

        # Top
        cursor_.execute("""
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

        # Events
        cursor_.execute("""
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

        # Feedback
        cursor_.execute("""
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

        # Classes
        cursor_.execute("""
            create table if not exists classes (
                id int primary key,
                foreign key (id) references events(id),
                total int default 0,
                annotation text default ''
            );
        """)

        # Enrolls
        cursor_.execute("""
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
        cursor_.execute("""
            create table if not exists credits (
                id serial not null primary key,
                user_id int,
                foreign key (user_id) references users(id),
                event_id int,
                foreign key (event_id) references events(id),
                validator_id int,
                foreign key (validator_id) references users(id),
                time text default '',
                value int default 0
            );
        """)

        # TODO: check if codes were created in a right way, just to make sure
        # Codes
        cursor_.execute("""
            create table if not exists codes (
                id serial not null primary key,
                code text,
                type int default 0,
                used bool default false
            );
        """)

        # Notifications
        cursor_.execute("""
            create table if not exists notifications (
                id serial not null primary key,
                user_id int,
                foreign key (user_id) references users(id),
                token text
            );
        """)

        # Vacations
        cursor_.execute("""
            create table if not exists vacations (
                id serial not null primary key unique,
                user_id int,
                foreign key (user_id) references users(id),
                date_from text default '',
                date_to text default '',
                time_from text default '',
                time_to text default '',
                accepted bool default FALSE
            );
        """)
except psycopg2.Error as error:
    logger('sql', f'Error encountered while startup-reinitializing the database: {error}', type_='ERROR')
    conn.rollback()
conn.commit()

TTableObject = tp.Dict[str, tp.Any]

table_fields: tp.Dict[str, tp.List[str]] = {
    'users': ['id', 'code', 'user_type', 'phone', 'name', 'sex', 'pass', 'team', 'project_id', 'avatar'],
    'sessions': ['id', 'user_id', 'user_type', 'user_agent', 'last_ip', 'time'],
    'credits': ['id', 'user_id', 'event_id', 'validator_id', 'time', 'value'],
    'codes': ['id', 'code', 'type', 'used'],
    'feedback': ['id', 'user_id', 'event_id', 'score', 'entertain', 'useful', 'understand', 'comment'],
    'top': ['id', 'user_id', 'day_id', 'chosen_1', 'chosen_2', 'chosen_3'],
    'projects': ['id', 'title', 'type', 'def_type', 'direction', 'description', 'annotation'],
    'events': ['id', 'type', 'title', 'description', 'host', 'place', 'time', 'day_id'],
    'classes': ['id', 'total', 'annotation'],
    'enrolls': ['id', 'class_id', 'user_id', 'time', 'attendance', 'bonus'],
    'days': ['id', 'date', 'title', 'feedback'],
    'notifications': ['id', 'user_id', 'token'],
    'vacations': ['id', 'user_id', 'date_from', 'date_to', 'time_from', 'time_to', 'accepted'],
}


""" ---===---==========================================---===--- """
"""           Auxiliary functions for sql interactions           """
""" ---===---==========================================---===--- """


def tuples_to_dicts(data_raw: tp.List[tp.Tuple[tp.Any]], table: str,
                    custom_fields: tp.Optional[tp.List[str]] = None) -> tp.List[TTableObject]:
    global table_fields

    data: tp.List[TTableObject] = []

    if custom_fields is None:
        for line in data_raw:
            data.append({table_fields[table][i]: line[i] for i, _ in enumerate(table_fields[table])})
    else:
        for line in data_raw:
            data.append({custom_fields[i]: line[i] for i, _ in enumerate(custom_fields)})

    return data


def dict_to_tuple(data_raw: TTableObject, table: str, ignore_id: bool = False,
                  empty_placeholder: tp.Optional[tp.Any] = None) -> tp.Tuple[tp.Any, ...]:  # noqa: C901
    global table_fields

    data: tp.List[tp.Any] = []

    for field in table_fields[table]:
        if field == 'id' and ignore_id:
            continue

        # Date fields
        if field == 'day_id':
            if 'day_id' in data_raw.keys():
                data.append(data_raw['day_id'])
                continue
            elif 'date' in data_raw.keys():
                try:
                    with conn.cursor() as cursor_:
                        cursor_.execute('select (id) from days where date = %s', (data_raw['date'],))
                        day_id_obj = cursor_.fetchone()
                        if day_id_obj is None:
                            data.append(empty_placeholder)
                        else:
                            data.append(day_id_obj[0])
                except psycopg2.Error as error_:
                    logger('sql.dict_to_tuple()', f'{error_}. Rolling back.', type_='ERROR')
                    conn.rollback()
                    data.append(empty_placeholder)  # in case of error
                conn.commit()
                continue
            else:
                data.append(empty_placeholder)
                continue

        # Common fields
        try:
            data.append(data_raw[field])
        except KeyError:
            data.append(empty_placeholder)  # if no field

    return tuple(data)


def tuple_to_dict(data_raw: tp.Tuple[tp.Any], table: str,
                  empty_placeholder: tp.Optional[tp.Any] = None) -> TTableObject:
    global table_fields

    data: tp.Dict[str, tp.Any] = {}

    for i, field in enumerate(table_fields[table]):
        try:
            data[field] = data_raw[i]
        except IndexError:
            data[field] = empty_placeholder

    return data


""" ---===---==========================================---===--- """
"""            Overall functions for sql interactions            """
""" ---===---==========================================---===--- """


# TODO: check for usage in main.py ad add there checks like True/False
def insert_to_table(data: TTableObject, table_name: str) -> tp.Optional[int]:
    """ Insert some object in some db table

    Args:
        data: dict witch should be insert (id=None)
        table_name: name of current table to insert

    Exceptions:
        raise

    Returns:
        id: return id of new element
    """

    if data is None:
        return None

    if table_name == 'events':
        # Class event
        if 'date' in data:
            # If several dates - split by ', '
            last_id = None
            for date in data['date'].split(', '):
                current_event = copy.copy(data)
                current_event['date'] = date

                last_id = insert_event(current_event)
            return last_id
        else:
            return insert_event(data)

    hundred: tp.Optional[tp.Tuple[int]]
    fields = ', '.join([field for field in table_fields[table_name] if field != 'id'])
    values_placeholder = ', '.join(['%s' for field in table_fields[table_name] if field != 'id'])

    sql_string = f"INSERT INTO {table_name} ({fields}) VALUES ({values_placeholder}) RETURNING id;"

    try:
        with conn.cursor() as cursor_:
            cursor_.execute(sql_string, dict_to_tuple(data, table_name, ignore_id=True))
            hundred = cursor_.fetchone()[0]
            conn.commit()
    except psycopg2.Error as error_:
        logger(f'sql.insert_to_table(\'{table_name}\')', f'{error_}. Rolling back.', type_='ERROR')
        conn.rollback()
        return None
    else:
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

    try:
        with conn.cursor() as cursor_:
            cursor_.execute(sql_string, dict_to_tuple(data, table_name))
    except psycopg2.Error as error_:
        logger(f'sql.update_in_table(\'{table_name}\')', f'{error_}. Rolling back.', type_='ERROR')
        conn.rollback()
    else:
        conn.commit()


def get_in_table(data_id: int, table_name: str) -> tp.Optional[TTableObject]:
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
    obj: tp.Optional[tp.Tuple] = None

    try:
        with conn.cursor() as cursor_:
            cursor_.execute(sql_string, (data_id,))
            obj = cursor_.fetchone()
    except psycopg2.Error as error_:
        logger(f'sql.get_in_table(\'{table_name}\')', f'{error_}. Rolling back.', type_='ERROR')
        conn.rollback()
        return None
    else:
        conn.commit()

    if obj is None:
        return None
    else:
        return tuple_to_dict(obj, table_name)


def remove_in_table(data_id: int, table_name: str) -> None:
    """ Remove some object from some db table

    Args:
        data_id: id coordinated from table obj
        table_name: name of current table to insert

    Exceptions:
        raise
    """

    if data_id == 0 or data_id == '0':
        return

    if table_name == 'projects':
        remove_project(data_id)
        return

    if table_name == 'events':
        remove_event(data_id)
        return

    if table_name == 'classes':
        remove_class(data_id)
        return

    if table_name == 'users':
        remove_user(data_id)
        return

    if table_name == 'sessions':
        remove_session(data_id)
        return

    if table_name == 'enrolls':
        remove_enroll(data_id)
        return

    try:
        with conn.cursor() as cursor_:
            cursor_.execute(f"DELETE FROM {table_name} where id = {data_id};")
    except psycopg2.Error as error_:
        logger('sql.remove_in_table()', f'{error_}. Rolling back.', type_='ERROR')
        conn.rollback()
    else:
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

    objects_list: tp.List[tp.Tuple] = []

    try:
        with conn.cursor() as cursor_:
            cursor_.execute(f'SELECT * FROM {table_name};')
            objects_list = cursor_.fetchall()
    except psycopg2.Error as error_:
        logger(f'sql.get_table(\'{table_name}\')', f'{error_}. Rolling back.', type_='ERROR')
        conn.rollback()
    else:
        conn.commit()

    return tuples_to_dicts(objects_list, table_name)


def clear_table(table_name: str):
    """ Remove all objects from sql table (EXCEPT id==0)

    Args:
        table_name: name of db table
    """

    if table_name == 'classes' or table_name == 'events':
        clear_events()

    if table_name == 'users':
        clear_users()

    try:
        with conn.cursor() as cursor_:
            cursor_.execute(f'DELETE FROM {table_name} WHERE id != 0;')
    except psycopg2.Error as error_:
        logger(f'sql.clear_table(\'{table_name}\')', f'{error_}. Rolling back.', type_='ERROR')
        conn.rollback()
    else:
        conn.commit()


""" ---===---==========================================---===--- """
"""            Special functions for sql interactions            """
""" ---===---==========================================---===--- """


# Projects
def remove_project(project_id: int) -> bool:
    """ Delete project by id

    Args:
        project_id: projects id from bd

    Returns:
        bool: success delete or not
    """

    try:
        with conn.cursor() as cursor_:
            cursor_.execute(f'update users set project_id = 0 where project_id = {project_id};')
            cursor_.execute(f'delete from projects where id = {project_id};')
    except psycopg2.Error as error_:
        logger('sql.remove_project()', f'{error_}. Rolling back.', type_='ERROR')
        conn.rollback()
        return False
    else:
        conn.commit()
        return True

# Days


# Vacations


# Users
def get_names() -> tp.List[TTableObject]:
    """ Get all users short list from sql table

    Args:

    Returns:
        user short objects: list of user objects - [(id, code, name, team, project_id), ...]
    """

    users_list: tp.Optional[tp.List[tp.Tuple]] = None

    try:
        with conn.cursor() as cursor_:
            cursor_.execute('SELECT id, name, team, project_id FROM users WHERE user_type = 0;')
            users_list = cursor_.fetchall()
    except psycopg2.Error as error_:
        logger('sql.get_names()', f'{error_}. Rolling back.', type_='ERROR')
        conn.rollback()
        return []
    else:
        return tuples_to_dicts(users_list, '', custom_fields=['id', 'name', 'team', 'project_id'])


def get_user_by_phone(phone: str) -> tp.Optional[TTableObject]:
    """ Get user obj by phone

    Args:
        phone: phone - str

    Returns:
        user_obj: (id, user_type, phone, name, pass, team, credits, avatar, project_id)
                     or None if there is no such user
    """

    user: tp.Optional[tp.Tuple] = None

    try:
        with conn.cursor() as cursor_:
            cursor_.execute("select * from users where phone = %s;", (phone,))
            user = cursor_.fetchone()
            if not user:
                return None
    except psycopg2.Error as error_:
        logger('sql.get_user_by_phone()', f'{error_}. Rolling back.', type_='ERROR')
        conn.rollback()
        return None
    else:
        return tuple_to_dict(user, 'users')


def get_user_by_id(user_id: int) -> tp.Optional[TTableObject]:
    """ Get user obj by id

    Args:
        user_id: user_id - int

    Returns:
        user_obj: (id, user_type, phone, name, pass, team, credits, avatar, project_id)
                     or None if there is no such user
    """

    user: tp.Optional[tp.Tuple] = None

    try:
        with conn.cursor() as cursor_:
            cursor_.execute("select * from users where id = %s;", (user_id,))
            user = cursor_.fetchone()
            if not user:
                return None
    except psycopg2.Error as error_:
        logger('sql.get_user_by_id()', f'{error_}. Rolling back.', type_='ERROR')
        conn.rollback()
        return None
    else:
        return tuple_to_dict(user, 'users')


def register(code: str, name: str, surname: str, phone: str, sex: bool, passw: str, team: int, type_: int = 0) -> bool:
    """ Register new user
    There is no verification - create anywhere

    Args:
        code: registration code - string
        name: User name
        surname: User surname
        phone: phone - string
        sex: Sex of user. [True=Male, False=Female]
        passw: Password hash - int
        team: number of group - int (0, main.NUM_OF_GROUPS]
        type_: User type - int  [0=USER, 1=MODERATOR, 2=ADMIN]

    Note:
        user id is automatically generated

    Returns:
        Success reg or not
    """

    try:
        # Check code
        with conn.cursor() as cursor_:
            cursor_.execute('SELECT * FROM codes WHERE code = %s AND used = false;', (code,))
            existing_user = cursor_.fetchone()
            if existing_user is None:
                return False

        # Check user exist
        with conn.cursor() as cursor_:
            cursor_.execute('SELECT * FROM users WHERE phone = %s AND pass = %s;', (phone, passw))
            existing_user = cursor_.fetchone()
            if existing_user is not None:
                return False

        # Update code
        with conn.cursor() as cursor_:
            cursor_.execute('UPDATE codes SET used = true WHERE code = %s;', (code,))

        # Create user
        with conn.cursor() as cursor_:
            sql_string = 'INSERT INTO users (code, user_type, phone, name, sex, pass, team) ' \
                         'VALUES (%s, %s, %s, %s, %s, %s, %s);'
            cursor_.execute(sql_string, (code, type_, phone, name + ' ' + surname, sex, passw, team))
    except psycopg2.Error as error_:
        logger('sql.register()', f'{error_}. Rolling back.', type_='ERROR')
        conn.rollback()
        return False
    else:
        conn.commit()
        return True


def checkin_by_event_id(event_id: int, checkin_obj: tp.List[TTableObject]):
    """ Checkin users in event
    Add user credits for the event

    Args:
        event_id: id of event to set credits
        checkin_obj: (id, type, title, credits, count, total, date)
    """
    pass


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


def remove_user(user_id: int) -> bool:
    """ Delete user by id

    Args:
        user_id: user id from db

    Returns:
        Successful delete or not
    """

    try:
        with conn.cursor() as cursor_:
            cursor_.execute(f'delete from sessions where user_id = {user_id};')
            cursor_.execute(f'delete from vacations where user_id = {user_id};')
            cursor_.execute(f'delete from feedback where user_id = {user_id};')
            cursor_.execute(f'delete from credits where user_id = {user_id};')
            cursor_.execute(f'delete from top where user_id = {user_id};')
            cursor_.execute(f'delete from enrolls where user_id = {user_id};')
            cursor_.execute(f'delete from users where id = {user_id};')
    except psycopg2.Error as error_:
        logger('sql.remove_user()', f'{error_}. Rolling back.', type_='ERROR')
        conn.rollback()
        return False
    else:
        conn.commit()
        return True


def clear_users() -> bool:
    """Clear all users from sql table"""

    # TODO: probably won't succeed due to ForeignKeyViolation error, see the method above
    try:
        with conn.cursor() as cursor_:
            cursor_.execute('delete from sessions;')
            cursor_.execute('delete from vacations;')
            cursor_.execute('delete from feedback;')
            cursor_.execute('delete from credits;')
            cursor_.execute('delete from top;')
            cursor_.execute('delete from enrolls;')
            cursor_.execute('delete from users;')
    except psycopg2.Error as error_:
        logger('sql.clear_users()', f'{error_}. Rolling back.', type_='ERROR')
        conn.rollback()
        return False
    else:
        conn.commit()
        return True


# Sessions
def get_sessions() -> tp.List[TTableObject]:
    """Get all sessions from sql table

    Returns:
        session objects: list of sess objects - [ (id, user_id, user_type, user_agent, last_ip, time), ...]
    """
    sessions_list: tp.Optional[tp.List[tp.Tuple]] = None

    try:
        with conn.cursor() as cursor_:
            cursor_.execute('select * from sessions;')
            sessions_list = cursor_.fetchall()
    except psycopg2.Error as error_:
        logger('sql.get_sessions()', f'{error_}. Rolling back.', type_='ERROR')
        conn.rollback()
        return []

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

    sess: tp.Optional[tp.Tuple] = None
    try:
        with conn.cursor() as cursor_:
            cursor_.execute(f"select * from sessions where id = bytea \'\\x{sess_id}\';")
            sess = cursor_.fetchone()
            if sess is None:
                return None
    except psycopg2.Error as error_:
        logger(f'sql.get_session({sess_id})', f'{error_}. Rolling back.', type_='ERROR')
        conn.rollback()
        return None
    else:
        conn.commit()

    return tuple_to_dict(sess, 'sessions')


def change_password(user_id: int, passw: int) -> bool:
    """ Change password for user

    Args:
        user_id: Id from table of user - int
        passw: Password hash - int

    Returns:
        bool - success or not
    """

    try:
        with conn.cursor() as cursor_:
            cursor_.execute('UPDATE users SET pass = %s WHERE id = %s;', (passw, user_id))
    except psycopg2.Error as error_:
        logger(f'sql.change_password({user_id}, )', f'{error_}. Rolling back.', type_='ERROR')
        conn.rollback()
        return False
    else:
        conn.commit()
        return True


# TODO: Update time in sessions
def login(phone: str, passw: str, agent: str, ip: str, time_: str = '0') -> tp.Optional[bytes]:
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
    user: tp.Optional[tp.Tuple] = None
    existing_session: tp.Optional[tp.Tuple] = None
    session_id: tp.Optional[tp.Tuple] = None

    # Check user with name and pass exist and got it
    logger('sql.login()', f'try to login user with phone={phone}, pass={passw}', type_='LOG')
    try:
        with conn.cursor() as cursor_:
            cursor_.execute(f"select * from users where phone = '{phone}' and pass = {passw};")
            user = cursor_.fetchone()
    except psycopg2.Error as error_:
        logger('sql.login()', f'Check user existence; {error_}. Rolling back.', type_='ERROR')
        conn.rollback()
        return None
    else:
        conn.commit()

    if user is None:  # No such user
        return None

    # Create new session if there is no session with user_id and user_agent
    try:
        with conn.cursor() as cursor_:
            cursor_.execute('SELECT * FROM sessions WHERE user_id = %s AND user_agent = %s;', (user[0], agent))
            existing_session = cursor_.fetchone()
    except psycopg2.Error as error_:
        logger('sql.login()', f'Create session; {error_}. Rolling back.', type_='ERROR')
        conn.rollback()
        return None
    else:
        conn.commit()

    # Return existing sessions
    if existing_session is not None:
        logger('sql.login()', f'session id got by login:{existing_session[0]}', type_='LOG')
        return existing_session[0]

    # Create new session
    sql_string = "INSERT INTO sessions (id, user_id, user_type, user_agent, last_ip, time) " \
                 "VALUES (default, %s, %s, %s, %s, %s) RETURNING id;"
    try:
        with conn.cursor() as cursor_:
            session_id = cursor_.execute(sql_string, (user[0], user[2], agent, ip, time_))
    except psycopg2.Error as error_:
        logger('sql.login()', f'Create session; {error_}. Rolling back.', type_='ERROR')
        conn.rollback()
        return None
    else:
        conn.commit()

    logger('sql.login()', f'created session with id:{session_id}', type_='LOG')
    return session_id


def remove_session(sess_id: int) -> bool:
    """ Remove session by id
    TODO: remove this function?
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

    try:
        with conn.cursor() as cursor_:
            cursor_.execute(f'delete from sessions where id = bytea \'\\x{sess_id}\';')
    except psycopg2.Error as error_:
        logger('sql.logout()', f'{error_}. Rolling back.', type_='ERROR')
        conn.rollback()
        return False
    else:
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
    day: tp.Optional[tp.Tuple] = None
    events_list: tp.Optional[tp.List[tp.Tuple]] = None

    try:
        with conn.cursor() as cursor_:
            cursor_.execute(f"select (id) from days where date = '{date}'")
            day = cursor_.fetchone()
    except psycopg2.Error as error_:
        logger(f'sql.get_day({date})', f'Select day; {error_}. Rolling back.', type_='ERROR')
        conn.rollback()
        return []
    else:
        conn.commit()

    if day is None:
        return []

    day_id = int(day[0])  # TODO: maybe [0] is not needed

    try:
        with conn.cursor() as cursor_:
            cursor_.execute(f'select * from events where day_id = {day_id};')
            events_list = cursor_.fetchall()
    except psycopg2.Error as error_:
        logger(f'sql.get_day({date})', f'Select events; {error_}. Rolling back.', type_='ERROR')
        conn.rollback()
        return []
    else:
        conn.commit()

    return tuples_to_dicts(events_list, 'events')


def get_event_with_date(event_id: int) -> tp.Optional[TTableObject]:
    """ Get event obj with date in dd.mm

    Args:
        event_id: id of events for selecting

    Returns:
        credits objects: l
    """
    event: tp.Optional[tp.Tuple] = None

    sql_string = 'SELECT e.id, e.type, d.date, e.time FROM events e JOIN days d ON e.day_id = d.id WHERE e.id = %s;'

    try:
        with conn.cursor() as cursor_:
            cursor_.execute(sql_string, (event_id, ))
            event = cursor_.fetchone()
    except psycopg2.Error as error_:
        logger(f'sql.get_event_with_date({event_id})', f'{error_}. Rolling back.', type_='ERROR')
        conn.rollback()
        return None
    else:
        conn.commit()

    return {'id': event[0], 'type': event[1], 'date': event[2], 'time': event[3]}


def insert_event(event_obj: TTableObject) -> tp.Optional[int]:
    """ Insert event

    Args:
        event_obj: event obj (None, type, title, description, host, place, time, date)

    Returns:
        id: id of the created event
    """

    day: tp.Optional[tp.Tuple[int]] = None

    try:
        with conn.cursor() as cursor_:
            cursor_.execute('select (id) from days where date = %s', (event_obj['date'],))
            day = cursor_.fetchone()
    except psycopg2.Error as error_:
        logger('sql.insert_event()', f'{error_}. Rolling back.', type_='ERROR')
        conn.rollback()
        return None
    else:
        conn.commit()

    if day is None:
        return None

    day_id = day[0]

    event_obj['day_id'] = day_id
    values_placeholder = ', '.join(['%s' for field in table_fields['events'] if field != 'id'])
    event_id: tp.Optional[tp.Tuple[int]] = None

    sql_string = f'INSERT INTO events (type, title, description, host, place, time, day_id) ' \
                 f'VALUES ({values_placeholder}) RETURNING id;'

    try:
        with conn.cursor() as cursor_:
            cursor_.execute(sql_string, dict_to_tuple(event_obj, 'events', ignore_id=True))
            event_id = cursor_.fetchone()[0]
    except psycopg2.Error as error_:
        # print(f"Error in sql.insert_event(): {error_}")
        logger('sql.insert_event()', f'{error_}. Rolling back.', type_='ERROR')
        conn.rollback()
        return None
    else:
        conn.commit()

    if int(event_obj['type']) == 1 or int(event_obj['type']) == 2:
        # master/lecture - add class in table
        try:
            with conn.cursor() as cursor_:
                cursor_.execute('INSERT INTO classes (id, total, annotation) VALUES (%s, %s, %s);', (event_id, 0, ''))
        except psycopg2.Error as error_:
            logger('sql.insert_event()', f'{error_}. Rolling back.', type_='ERROR')
            conn.rollback()
            return None
        else:
            conn.commit()
    else:
        # regular
        pass

    return event_id


def edit_event(event_obj: TTableObject) -> bool:
    """ Update event

    Args:
        event_obj: event obj (id, type, title, description, host, place, time, day_id)
    """

    if 'day_id' in event_obj.keys():
        day_id = event_obj['day_id']
    else:
        day: tp.Optional[tp.Tuple[int]] = None

        try:
            with conn.cursor() as cursor_:
                cursor_.execute('select (id) from days where date = %s', (event_obj['date'],))
                day = cursor_.fetchone()
        except psycopg2.Error as error_:
            logger('sql.edit_event()', f'Select day; {error_}. Rolling back.', type_='ERROR')
            conn.rollback()
            return None

        if day is None:
            return None

        day_id = day[0]

    try:
        # Check Changed type -> create or delete
        if int(event_obj['type']) == 1 or int(event_obj['type']) == 2:
            # Now it's class. Check class exist
            with conn.cursor() as cursor_:
                cursor_.execute(
                    'INSERT INTO classes (id, total, annotation) VALUES (%s, 0, \'\') ON CONFLICT DO NOTHING',
                    (event_obj['id'],))
        else:
            # Mb was a class. Remove
            with conn.cursor() as cursor_:
                cursor_.execute('delete FROM classes where id = %s', (event_obj['id'],))

        # Update events
        with conn.cursor() as cursor_:
            sql_string = 'update events set type = %s, title = %s, description = %s, host = %s, ' \
                         'place = %s, time = %s, day_id = %s where id = %s;'
            cursor_.execute(sql_string,
                            (event_obj['type'],
                             event_obj['title'],
                             event_obj['description'],
                             event_obj['host'],
                             event_obj['place'],
                             event_obj['time'],
                             day_id,
                             event_obj['id']))
    except psycopg2.Error as error_:
        logger('sql.edit_event()', f'Update events; {error_}. Rolling back.', type_='ERROR')
        conn.rollback()
        return False
    else:
        conn.commit()
        return True


def remove_event(event_id: int) -> bool:
    """ Delete event by id

    Args:
        event_id: event id from bd

    Returns:
        # Success delete or not

    """
    try:
        with conn.cursor() as cursor_:
            cursor_.execute('UPDATE credits SET event_id = 0 WHERE event_id = %s;', (event_id, ))
            cursor_.execute('DELETE FROM enrolls WHERE class_id = %s;', (event_id, ))
            cursor_.execute('DELETE FROM classes WHERE id = %s;', (event_id, ))
            cursor_.execute('DELETE FROM events WHERE id = %s;', (event_id, ))
    except psycopg2.Error as error_:
        logger(f'sql.remove_event({event_id})', f'{error_}. Rolling back.', type_='ERROR')
        conn.rollback()
        return False
    else:
        conn.commit()
        return True


def clear_events() -> bool:
    """ Clear all events from sql table """
    try:
        with conn.cursor() as cursor_:
            cursor_.execute('delete from classes where id != 0;')
            cursor_.execute('delete from events where id != 0;')
    except psycopg2.Error as error_:
        logger('sql.clear_events()', f'{error_}. Rolling back.', type_='ERROR')
        conn.rollback()
        return False
    else:
        conn.commit()
        return True


# Classes
def check_class(class_id: int) -> bool:
    """ Check class have empty places

    Args:
        class_id: class id (event id) from bd

    Returns:
        bool - True - has places
    """

    enrolled: tp.Optional[int] = None
    try:
        with conn.cursor() as cursor_:
            cursor_.execute('select count(*) from enrolls where class_id = %s;', (class_id,))
            enrolled = cursor_.fetchone()[0]
    except psycopg2.Error as error_:
        logger(f'sql.check_class({class_id})', f'Count enrolls; {error_}. Rolling back.', type_='ERROR')
        conn.rollback()
        return False
    else:
        conn.commit()

    class_obj: tp.Optional[tp.Tuple] = None
    try:
        with conn.cursor() as cursor_:
            cursor_.execute('select (total) from classes where id = %s;', (class_id,))
            class_obj = cursor_.fetchone()
    except psycopg2.Error as error_:
        logger(f'sql.check_class({class_id})', f'Check total; {error_}. Rolling back.', type_='ERROR')
        conn.rollback()
        return False
    else:
        conn.commit()

    if class_obj is None:
        return False

    return enrolled < class_obj[0]


def remove_class(class_id: int) -> bool:
    """ Delete class by id

    Args:
        class_id: class id from bd

    Returns:
        Success delete or not
    """

    try:
        with conn.cursor() as cursor_:
            cursor_.execute('DELETE FROM classes WHERE id = %s;', (class_id,))
            cursor_.execute('DELETE FROM enrolls WHERE class_id = %s;', (class_id,))
            cursor_.execute('UPDATE events SET type = 0 WHERE event_id = %s;', (class_id,))
    except psycopg2.Error as error_:
        logger(f'sql.remove_class({class_id})', f'{error_}. Rolling back.', type_='ERROR')
        conn.rollback()
        return False
    else:
        conn.commit()
        return True


def enroll_user(class_id: int, user_id: TTableObject, date: str, time_: str = '0') -> bool:  # TODO?
    """ Enroll user in event

    Args:
        class_id: class id (event id) from bd
        user_id: user id form db
        date: date in format dd.mm
        time_: time str

    Returns:
        True/False: Success or not
    """

    try:
        with conn.cursor() as cursor_:
            cursor_.execute('select ev.time from enrolls en join events ev on en.class_id = ev.id where '
                            'ev.day_id = (select day_id from days where date = %s) and en.user_id = %s;', (date, user_id,))
            enrolls_times = cursor_.fetchall()  # enrolls of user for this day

            # Check have no other enrolls
            if enrolls_times is not None:
                for time_str in enrolls_times:
                    time1, time2 = time_str[0].split('\n')
                    # if time1 == TODO: Check other times
    except psycopg2.Error as error_:
        logger(f'sql.enroll_user({class_id}, {user_id})', f'Check time; {error_}. Rolling back.', type_='ERROR')
        conn.rollback()
        return False
    else:
        conn.commit()

    class_: tp.Optional[tp.Tuple] = None
    enrolled: tp.Optional[int] = None
    try:
        # Select class
        with conn.cursor() as cursor_:
            cursor_.execute('select * from classes where id = %s;', (class_id,))
            class_ = cursor_.fetchone()

        # Count enrolls
        with conn.cursor() as cursor_:
            cursor_.execute('select count(*) from enrolls where class_id = %s;', (class_id,))
            enrolled = cursor_.fetchone()[0]
    except psycopg2.Error as error_:
        logger(f'sql.enroll_user({class_id}, {user_id})', f'{error_}. Rolling back.', type_='ERROR')
        conn.rollback()
        return False
    else:
        conn.commit()

    print('!!!!!! class_', class_)
    print('!!!!!! enrolled', enrolled)

    if class_ is None or enrolled is None or enrolled >= class_[1]:  # No such event or too many people
        print('!!!!!! No such event or too many people')
        return False

    sql_string = 'insert into enrolls (class_id, user_id, time, attendance, bonus) values (%s, %s, %s, false, 0);'

    try:
        with conn.cursor() as cursor_:
            cursor_.execute(sql_string, (class_id, user_id, time_))
    except psycopg2.Error as error_:
        logger(f'sql.enroll_user({class_id}, {user_id})', f'Insert enroll; {error_}. Rolling back.', type_='ERROR')
        conn.rollback()
        return False
    else:
        conn.commit()
        return True


# Enrolls
def get_enrolls_by_event_id(event_id: int) -> tp.List[TTableObject]:
    """ Get enrolls obj by event id

    Args:
        event_id: event id from bd

    Returns:
        enroll_objs: [(id, class_id, users_id, time, attendance), ...]
    """

    enrolls: tp.Optional[tp.List[tp.Tuple]] = None
    try:
        with conn.cursor() as cursor_:
            cursor_.execute('select * from enrolls where class_id = %s;', (event_id,))
            enrolls = cursor_.fetchall()
    except psycopg2.Error as error_:
        logger(f'sql.get_enrolls_by_event_id({event_id})', f'{error_}. Rolling back.', type_='ERROR')
        conn.rollback()
        return []
    else:
        conn.commit()

    if not enrolls:
        return []

    return tuples_to_dicts(enrolls, 'enrolls')


def get_enrolls_by_user_id(user_id: int) -> tp.List[TTableObject]:
    """ Get enrolls obj by user id

    Args:
        user_id: user id from bd

    Returns:
        enroll_objs: [(id, event_id, users_id, time, attendance), ...]
    """
    enrolls: tp.Optional[tp.List[tp.Tuple]] = None

    try:
        with conn.cursor() as cursor_:
            cursor_.execute('select * from enrolls where user_id = %s;', (user_id,))
            enrolls = cursor_.fetchall()
    except psycopg2.Error as error_:
        logger(f'sql.get_enrolls_by_user_id({user_id})', f'{error_}. Rolling back.', type_='ERROR')
        conn.rollback()
        return []
    else:
        conn.commit()

    if not enrolls:
        return []

    return tuples_to_dicts(enrolls, 'enrolls')


def remove_enroll(enroll_id: int) -> bool:
    """ Delete enroll by id

    Args:
        enroll_id: enroll id from bd

    Returns:
        Success delete or not
    """
    enroll: tp.Optional[tp.Tuple] = None

    try:
        with conn.cursor() as cursor_:
            cursor_.execute('select * from enrolls where id = %s;', (enroll_id,))
            enroll = cursor_.fetchone()
    except psycopg2.Error as error_:
        logger(f'sql.remove_enroll({enroll_id})', f'Select enroll; {error_}. Rolling back.', type_='ERROR')
        conn.rollback()
        return False
    else:
        conn.commit()

    if not enroll:
        return False

    try:
        with conn.cursor() as cursor_:
            cursor_.execute('delete from enrolls where id = %s;', (enroll_id,))
            cursor_.execute('delete from credits where user_id = %s and event_id = %s;', (enroll[2], enroll[1]))
    except psycopg2.Error as error_:
        logger(f'sql.remove_enroll({enroll_id})', f'Delete enroll and credits; {error_}. Rolling back.', type_='ERROR')
        conn.rollback()
        return False
    else:
        conn.commit()
        return True
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
    credits_list: tp.Optional[tp.List[tp.Tuple]] = None

    sql_string = 'SELECT cr.id, cr.user_id, cr.event_id, cr.value, e.type, e.title, e.day_id FROM credits cr ' \
                 'JOIN events e ON cr.event_id = e.id WHERE cr.user_id = %s;'

    try:
        with conn.cursor() as cursor_:
            cursor_.execute(sql_string, (user_id, ))
            credits_list = cursor_.fetchall()
    except psycopg2.Error as error_:
        logger(f'sql.get_credits_by_user_id({user_id})', f'{error_}. Rolling back.', type_='ERROR')
        conn.rollback()
        return []
    else:
        conn.commit()

    if not credits_list:
        return []

    return tuples_to_dicts(credits_list, '',
                           custom_fields=['id', 'user_id', 'event_id', 'value', 'type', 'title', 'day_id'])


def get_credits_short() -> tp.List[TTableObject]:
    """ Get all credits of user from sql table

    Returns:
        credits objects: list of credits objects - [ (id, user_id, event_id, date, value), ...]
    """

    credits_list: tp.Optional[tp.List[tp.Tuple]] = None

    sql_string = 'SELECT cr.id, cr.user_id, cr.event_id, cr.value, e.type, e.title, e.day_id FROM credits cr ' \
                 'JOIN events e ON cr.event_id = e.id;'

    try:
        with conn.cursor() as cursor_:
            cursor_.execute(sql_string)
            credits_list = cursor_.fetchall()
    except psycopg2.Error as error_:
        logger('sql.get_credits_short()', f'{error_}. Rolling back.', type_='ERROR')
        conn.rollback()
        return []
    else:
        conn.commit()

    return tuples_to_dicts(credits_list, '',
                           custom_fields=['id', 'user_id', 'event_id', 'value', 'type', 'title', 'day_id'])


def pay_credit(user_id: int, event_id: int, value: int = 0, time_: str = '0') -> bool:
    """ Insert credit for user

    Args:
        user_id: user id from db
        event_id: event id from db
        value: int number of credits
        time_: current time str
    """
    credits_: tp.Optional[tp.List[tp.Tuple]] = None

    try:
        with conn.cursor() as cursor_:
            cursor_.execute('SELECT * FROM credits WHERE event_id = %s AND user_id = %s;', (event_id, user_id))
            credits_ = cursor_.fetchall()
    except psycopg2.Error as error_:
        logger('sql.pay_credit()', f'Select credit; {error_}. Rolling back.', type_='ERROR')
        conn.rollback()
        return False
    else:
        conn.commit()

    sql_string = 'INSERT INTO credits (user_id, event_id, time, value) VALUES (%s, %s, %s, %s);'

    if not credits_:
        try:
            with conn.cursor() as cursor_:
                cursor_.execute(sql_string, (user_id, event_id, time_, value))
        except psycopg2.Error as error_:
            logger('sql.pay_credit()', f'Insert credit; {error_}. Rolling back.', type_='ERROR')
            conn.rollback()
            return False
        else:
            conn.commit()
    else:
        try:
            with conn.cursor() as cursor_:
                cursor_.execute('UPDATE credits SET VALUE = %s WHERE id = %s;', (value, credits_[0][0]))
        except psycopg2.Error as error_:
            logger('sql.pay_credit()', f'Update credit; {error_}. Rolling back.', type_='ERROR')
            conn.rollback()
            return False
        else:
            conn.commit()
    # TODO: Make execute params
    return True


# Codes
def load_codes(codes: tp.List[TTableObject]) -> bool:
    """ Cleat codes table and setup.sh from codes

    Args:
        codes: codes list - [(str, int), (str, int), ... ]

    Returns:
        bool: successful call to DB or not
    """
    sql_string = 'insert into codes (code, type, used) values (%s, %s, false);'

    try:
        with conn.cursor() as cursor_:
            # TODO: check docs for smth like batch executing
            for code in codes:
                cursor_.execute(sql_string, (code['code'], code['type']))
    except psycopg2.Error as error_:
        logger('sql.load_codes()', f'{error_}. Rolling back.', type_='ERROR')
        conn.rollback()
        return False
    else:
        conn.commit()
        return True


def use_code(code: str) -> bool:
    """ Set code used

    Args:
        code: code from bd

    Returns:
        Success delete or not

    """
    code: tp.Optional[tp.Tuple[bool]] = None

    try:
        with conn.cursor() as cursor_:
            cursor_.execute('select (used) from codes where code = %s;', (code,))
            code = cursor_.fetchone()
    except psycopg2.Error as error_:
        # print(f"Error in sql.use_code(): {error_}")
        logger(f'sql.use_code(\'{code}\')', f'Select code; {error_}. Rolling back.', type_='ERROR')
        conn.rollback()
        return False
    else:
        conn.commit()

    if not code or code[0]:
        return False

    try:
        with conn.cursor() as cursor_:
            cursor_.execute('update codes set used = true where code = %s;', (code,))
    except psycopg2.Error as error_:
        # print(f"Error in sql.use_code(): {error_}")
        logger(f'sql.use_code(\'{code}\')', f'Update code; {error_}. Rolling back.', type_='ERROR')
        conn.rollback()
        return False
    else:
        conn.commit()
        return True


# Projects
def save_project(project: tp.Dict[str, tp.Any]) -> bool:
    """ Create project
    Set for all users in project

    Args:
        project: code from bd

    Returns:
        Success creation or not
    """

    # Create new project
    project_id = insert_to_table(project, 'projects')
    if project_id:
        # Set this project for all users if there are no projects
        # TODO same stuff, batch
        try:
            with conn.cursor() as cursor_:
                for name in project['users']:
                    cursor_.execute('UPDATE users SET project_id = %s WHERE name = %s and project_id = 0;',
                                    (project_id, name))
        except psycopg2.Error as error_:
            logger('sql.save_project()', f'{error_}. Rolling back.', type_='ERROR')
            conn.rollback()
            return False
        else:
            conn.commit()
            return True
    else:
        return False


def enroll_project(user_id: int, project_id: int) -> bool:
    """ Enroll user in project

    Args:
        user_id: user id from bd
        project_id: project id from bd

    Returns:
        Success creation or not
    """
    try:
        with conn.cursor() as cursor_:
            cursor_.execute('UPDATE users SET project_id = %s WHERE id = %s;', (project_id, user_id))
    except psycopg2.Error as error_:
        logger('sql.enroll_project()', f'{error_}. Rolling back.', type_='ERROR')
        conn.rollback()
        return False
    else:
        conn.commit()
        return True


def deenroll_project(user_id: int) -> bool:
    return enroll_project(user_id, 0)


# Feedback

def get_top(user_id: int, date: str) -> tp.Optional[TTableObject]:
    """ Enroll user in project

    Args:
        user_id: user id from bd
        date: date from bd  # TODO: Check dd.mm of day_id

    Returns:
        Top object for current day
    """

    day: tp.Optional[tp.Tuple[int]]

    try:
        with conn.cursor() as cursor_:
            cursor_.execute('SELECT id FROM days WHERE date = %s;', (date,))
            day = cursor_.fetchone()
    except psycopg2.Error as error_:
        logger(f'sql.get_feedback({user_id}, {date})', f'Select day; {error_}. Rolling back.', type_='ERROR')
        conn.rollback()
        return None
    else:
        conn.commit()

    if day is None:
        return None

    day_id = day[0]

    top_obj = None  # type: tp.Optional[TTableObject]

    try:
        with conn.cursor() as cursor_:
            cursor_.execute('SELECT * FROM top WHERE user_id = %s AND day_id = %s', (user_id, day_id))
            top_ = cursor_.fetchone()
            if top_ is not None:
                top_obj = tuple_to_dict(top_, 'top')
    except psycopg2.Error as error_:
        logger(f'sql.get_top({user_id}, {date})', f'{error_}. Rolling back.', type_='ERROR')
        conn.rollback()
        return None
    else:
        conn.commit()
        return top_obj


def get_feedback(user_id: int, date: str) -> tp.Tuple[tp.List[TTableObject], tp.List[TTableObject]]:
    """ Enroll user in project

    Args:
        user_id: user id from bd
        date: date from bd  # TODO: Check dd.mm of day_id

    Returns:
        Feedback template - events list
        Feedback data - list of feedback (if any for template events)
    """
    day: tp.Optional[tp.Tuple[int]]

    try:
        with conn.cursor() as cursor_:
            cursor_.execute('SELECT id FROM days WHERE date = %s;', (date,))
            day = cursor_.fetchone()
    except psycopg2.Error as error_:
        logger(f'sql.get_feedback({user_id}, {date})', f'Select day; {error_}. Rolling back.', type_='ERROR')
        conn.rollback()
        return [], []
    else:
        conn.commit()

    if day is None:
        return [], []

    day_id = day[0]
    events_list: tp.Optional[tp.List[tp.Tuple]] = None

    try:
        with conn.cursor() as cursor_:
            sql_string = 'SELECT e.id, e.type, e.title, e.host, e.day_id FROM enrolls en ' \
                         'JOIN events e ON en.class_id = e.id ' \
                         'WHERE en.user_id = %s AND en.attendance = true AND e.day_id = %s;'
            cursor_.execute(sql_string, (user_id, day_id))
            events_list = cursor_.fetchall()
    except psycopg2.Error as error_:
        logger(f'sql.get_feedback({user_id}, {date})', f'Select visited events; {error_}. Rolling back.', type_='ERROR')
        conn.rollback()
        return [], []
    else:
        conn.commit()

    if not events_list:
        return [], []

    events_dicts = tuples_to_dicts(events_list, '', custom_fields=['id', 'type', 'title', 'host', 'day_id'])
    feedback_dicts: tp.List[tp.Dict] = []

    try:
        with conn.cursor() as cursor_:
            for event in events_dicts:
                cursor_.execute('SELECT * FROM feedback WHERE user_id = %s AND event_id = %s', (user_id, event['id']))
                feedback = cursor_.fetchone()
                if feedback is not None:
                    feedback_dicts.append(tuple_to_dict(feedback, 'feedback'))
    except psycopg2.Error as error_:
        logger(f'sql.get_feedback({user_id}, {date})', f'Select feedback; {error_}. Rolling back.', type_='ERROR')
        conn.rollback()
        return [], []
    else:
        conn.commit()
        return events_dicts, feedback_dicts


def post_feedback(user_id: int, feedback_list: tp.List[TTableObject]) -> None:
    """ Post feedbacks

    Args:
        user_id: user id from bd
        feedback_list: loist of feedback  # TODO: Check dd.mm of day_id

    Returns:
        None
    """
    # TODO: maybe batch will be faster here?
    for feedback in feedback_list:
        feedback['user_id'] = user_id
        insert_to_table(feedback, 'feedback')


def post_top(user_id: int, date: str, users_list: tp.List[str]) -> bool:
    """ Post top users

    Args:
        user_id: user id from bd
        date: dd.mm
        users_list: loist of feedback  # TODO: Check dd.mm of day_id

    Returns:
        None
    """
    day: tp.Optional[tp.Tuple[int]] = None
    print('!!!!!! date !!!!!!', date)

    try:
        with conn.cursor() as cursor_:
            cursor_.execute('SELECT (id) FROM days WHERE date = %s;', (date,))
            day = cursor_.fetchone()
    except psycopg2.Error as error_:
        logger(f'sql.post_top({user_id}, {date})', f'Select day; {error_}. Rolling back.', type_='ERROR')
        conn.rollback()
        return
    else:
        conn.commit()

    if day is None:
        return

    print('!!!!!! day !!!!!!', day)

    day_id = day[0]

    top_obj = {}  # type: TTableObject
    top_obj['user_id'] = user_id
    top_obj['day_id'] = day_id

    for i, name in enumerate(users_list):
        user = None  # type: tp.Optional[tp.Tuple[int]]
        try:
            with conn.cursor() as cursor_:
                cursor_.execute('SELECT (id) FROM users WHERE name = %s;', (name,))
                user = cursor_.fetchone()
        except psycopg2.Error as error_:
            logger(f'sql.post_top({user_id}, {date})', f'Select user; {error_}. Rolling back.', type_='ERROR')
            # TODO if you don't like losing all the looped stuff in case of rollback,
            conn.rollback()
            continue

            print('!!!!!! user !!!!!!' + str(i+1), user)

        if user is None:
            continue

        user_id = user[0]

        top_obj[f'chosen_{i+1}'] = user_id

    print('!!!! top_obj !!!!', top_obj)

    insert_to_table(top_obj, 'top')

    return True
