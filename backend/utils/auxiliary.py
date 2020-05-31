import typing as tp
import random
import json
from datetime import datetime, timezone, timedelta


TIMEZONE_SHIFT = 3  # MST timezone
ENROLL_CLOSE_FOR = 15  # Minutes


""" ---===---==========================================---===--- """
"""                     DataTime functions                       """
""" ---===---==========================================---===--- """


def get_datetime_str() -> str:
    """ Return current time str. According to timezone

    Returns:
        time str in format yyyy-mm-dd hh:mm:ss
    """

    return datetime.now(timezone(timedelta(hours=TIMEZONE_SHIFT))).strftime('%Y-%m-%d %H:%M:%S') + ' MSK'


def get_datetime_str_utc() -> str:
    """ Return current time str. UTC """
    return datetime.now(timezone(timedelta(hours=TIMEZONE_SHIFT))).strftime('%Y-%m-%d %H:%M:%S') + ' UTC'


def get_time_str() -> str:
    """ Return current time str. According to timezone

    Returns:
        time str in format hh.mm
    """

    return datetime.now(timezone(timedelta(hours=TIMEZONE_SHIFT))).strftime('%H.%M')


def get_date_str() -> str:
    """ Return current time str. According to timezone

    Returns:
        time str in format dd.mm
    """

    return '07.06'  # TODO: DEBUG porp!
    return datetime.now(timezone(timedelta(hours=TIMEZONE_SHIFT))).strftime('%d.%m')


""" ---===---==========================================---===--- """
"""                          Logging                             """
""" ---===---==========================================---===--- """

def logger(function, message, type_='ERROR'):  # TODO: move function to separate file
    time_ = get_datetime_str_utc()

    print(f'*** {type_} in {function}; {time_} ***')
    print(f'*** {message} ***')


""" ---===---==========================================---===--- """
"""                         Auxiliary                            """
""" ---===---==========================================---===--- """


def check_enroll_time(date: str, time_: str, year: str = '2020') -> bool:
    """ Check appropriate time for enroll on event

    Returns:
        bool can enroll or deenroll on the event
    """

    can_enroll = datetime.now(timezone(timedelta(hours=TIMEZONE_SHIFT))) <= \
        datetime.strptime(f'{date}.{year} {time_}', '%d.%m.%Y %M.%H') - timedelta(minutes=ENROLL_CLOSE_FOR)

    current_day = get_date_str() == date

    return can_enroll and current_day


def generate_codes(num: int) -> tp.Set[str]:
    """ Generate registration 6-sign codes
    Arguments:
        num:

    Returns:
        time str in format dd.mm
    """

    # random.seed(0)
    symbols = "ABCDEFGHJKLMNPQRSTUVWXYZ" + "123456789" + "123456789" + "123456789"
    symbols = [i for i in symbols]

    codes = set({})  # type: tp.Set[str]
    for i in range(num):
        choose5 = ''.join(random.choices(symbols, k=5))
        control1 = symbols[hash(choose5) % len(symbols)]

        code = choose5 + control1
        codes.add(code)

    return codes


def check_code(code: str) -> bool:
    """ Check valid code
    Arguments:
        code: 6 chart string code

    Returns:
        valid code or not
    """

    symbols = "ABCDEFGHJKLMNPQRSTUVWXYZ" + "123456789" + "123456789" + "123456789"
    symbols = [i for i in symbols]
    control1 = symbols[hash(code[:5]) % len(symbols)]

    return control1 == code[5:]
