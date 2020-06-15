import typing as tp
import random
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

    print(f'[{time_}]:{type_}:{function}:{message}')


""" ---===---==========================================---===--- """
"""                         Auxiliary                            """
""" ---===---==========================================---===--- """


CODE_SYMBOLS = "ABCDEFGHJKLMNPQRSTUVWXYZ" + "123456789" + "123456789" + "123456789"


def check_enroll_time(date: str, time_: str, year: str = '2020') -> bool:
    """ Check appropriate time for enroll on event

    Returns:
        bool can enroll or deenroll on the event
    """

    time_ = time_.split('\n')[0]
    start_time = datetime.strptime(f'{date}.{year} {time_}', '%d.%m.%Y %H.%M')

    # print('STR LINE: ', f"{date}.{year} {time_}")
    #
    # now_time = datetime.now(timezone(timedelta(hours=TIMEZONE_SHIFT))).replace(tzinfo=None)
    #
    # can_enroll = now_time <= start_time - timedelta(minutes=ENROLL_CLOSE_FOR)

    current_time = datetime.now(timezone(timedelta(hours=TIMEZONE_SHIFT))).strftime('%H.%M')
    now_time = datetime.strptime(f'{get_date_str()}.{year} {current_time}', '%d.%m.%Y %H.%M')

    can_enroll = now_time <= start_time - timedelta(minutes=ENROLL_CLOSE_FOR)

    print(f"{now_time} <= {start_time} - 15")

    is_current_day = get_date_str() == date

    logger('check_enroll_time()', f'can_enroll = {can_enroll} and is_current_day = {is_current_day}', 'LOG')


    return can_enroll and is_current_day


def generate_codes(num: int) -> tp.Set[str]:
    """ Generate registration 6-sign codes
    Arguments:
        num:

    Returns:
        time str in format dd.mm
    """

    codes = set({})  # type: tp.Set[str]
    for i in range(num):
        choose5 = ''.join(random.choices(CODE_SYMBOLS, k=5))
        control1 = CODE_SYMBOLS[hash(choose5) % len(CODE_SYMBOLS)]

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

    control1 = CODE_SYMBOLS[hash(code[:5]) % len(CODE_SYMBOLS)]

    return control1 == code[5:]
