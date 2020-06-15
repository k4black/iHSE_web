import typing as tp
import os
import shutil

import configparser

from utils.auxiliary import logger


CONFIG_PATH = '/var/conf/ihse/ihse.ini'
PLACES_PATH = '/var/conf/ihse/places.list'

DEFAULT_CONFIG_PATH = '/var/conf/ihse/default_ihse.ini'
DEFAULT_PLACES_PATH = '/var/conf/ihse/default_places.list'


""" ---===---==========================================---===--- """
"""                   Config file interactions                   """
""" ---===---==========================================---===--- """


CREDITS_TOTAL = 0
CREDITS_MASTER = 0
CREDITS_LECTURE = 0
CREDITS_ADDITIONAL = 0  # Maximum allowed additional credits
NUMBER_TEAMS = 0

PLACES = []  # type: tp.List[str]


def get_config() -> tp.Dict[str, int]:
    """ Get global config values """

    global CREDITS_TOTAL, CREDITS_MASTER, CREDITS_LECTURE, CREDITS_ADDITIONAL, NUMBER_TEAMS

    return {
        'CREDITS_TOTAL': CREDITS_TOTAL,
        'CREDITS_MASTER': CREDITS_MASTER,
        'CREDITS_LECTURE': CREDITS_LECTURE,
        'CREDITS_ADDITIONAL': CREDITS_ADDITIONAL,

        'NUMBER_TEAMS': NUMBER_TEAMS,
    }


def set_config(config_dict: tp.Dict[str, int]) -> None:
    """ Set global config values and save it to file """

    global CREDITS_TOTAL, CREDITS_MASTER, CREDITS_LECTURE, CREDITS_ADDITIONAL, NUMBER_TEAMS

    CREDITS_TOTAL = config_dict['CREDITS_TOTAL']
    CREDITS_MASTER = config_dict['CREDITS_MASTER']
    CREDITS_LECTURE = config_dict['CREDITS_LECTURE']
    CREDITS_ADDITIONAL = config_dict['CREDITS_ADDITIONAL']

    NUMBER_TEAMS = config_dict['NUMBER_TEAMS']

    write_config()


def read_config() -> None:
    """Read and save config file (`ihse.ini`) """

    logger('read_config()', '==== Read config file ====', type_='LOG')

    global CREDITS_TOTAL, CREDITS_MASTER, CREDITS_LECTURE, CREDITS_ADDITIONAL, NUMBER_TEAMS

    # Check file exist. or auto create
    with open(CONFIG_PATH, "a+") as f:
        pass

    try:
        config = configparser.ConfigParser()
        config.read(CONFIG_PATH)

        CREDITS_TOTAL = int(config['CREDITS']['total'])
        CREDITS_MASTER = int(config['CREDITS']['masterclass'])
        CREDITS_LECTURE = int(config['CREDITS']['lecture'])
        CREDITS_ADDITIONAL = int(config['CREDITS']['additional'])

        NUMBER_TEAMS = int(config['TEAMS']['number'])
    except (KeyError, configparser.MissingSectionHeaderError):
        logger('read_config()', 'No config file. Using default config file', type_='INFO')
        try:
            config = configparser.ConfigParser()
            config.read(DEFAULT_CONFIG_PATH)

            CREDITS_TOTAL = int(config['CREDITS']['total'])
            CREDITS_MASTER = int(config['CREDITS']['masterclass'])
            CREDITS_LECTURE = int(config['CREDITS']['lecture'])
            CREDITS_ADDITIONAL = int(config['CREDITS']['additional'])

            NUMBER_TEAMS = int(config['TEAMS']['number'])
            write_config()
        except (KeyError, configparser.MissingSectionHeaderError):
            logger('read_config()', 'No default config file. Using default values', type_='ERROR')
            CREDITS_TOTAL = 300
            CREDITS_MASTER = 15
            CREDITS_LECTURE = 15
            CREDITS_ADDITIONAL = 5
            NUMBER_TEAMS = 5
            write_config()

    logger('read_config()', '==== End config file reading ====', type_='LOG')


def write_config() -> None:
    """Write current configuration to config file (`ihse.ini`) """

    global CREDITS_TOTAL, CREDITS_MASTER, CREDITS_LECTURE, CREDITS_ADDITIONAL, NUMBER_TEAMS

    logger('write_config()', '==== Write config file ====', type_='LOG')
    config = configparser.ConfigParser()

    config['CREDITS'] = {
        'total': CREDITS_TOTAL,
        'masterclass': CREDITS_MASTER,
        'lecture': CREDITS_LECTURE,
        'additional': CREDITS_ADDITIONAL
    }

    config['TEAMS'] = {
        'number': NUMBER_TEAMS
    }

    with open(CONFIG_PATH, 'w') as configfile:
        config.write(configfile)

    logger('write_config()', '==== End config file writing ====', type_='LOG')


read_config()


def add_place(place: str) -> None:
    """ add place to PLACES and mb save it to file"""

    global PLACES

    logger('add_place()', f'Adding place = {place}', 'LOG')
    if place not in PLACES:
        PLACES.append(place)
        write_places()


def set_places(places: tp.List[str]) -> None:
    """ Set places and save to file """

    global PLACES

    PLACES = places
    write_places()


def get_places() -> tp.List[str]:
    """ Get places """
    global PLACES
    return PLACES



def read_places() -> tp.List[str]:
    """Read list of places from file (`places.list`) """

    global PLACES

    # Check file exist. or auto create
    if not os.path.exists(PLACES_PATH):
        logger('read_places()', 'No places file. Using default places file', type_='INFO')
        if os.path.exists(DEFAULT_PLACES_PATH):
            shutil.copy(DEFAULT_PLACES_PATH, PLACES_PATH)
        else:
            # Create empty
            logger('read_places()', 'No default places file. Using default values', type_='ERROR')
            with open(PLACES_PATH, "a+") as f:
                pass

    PLACES = []
    with open(PLACES_PATH, "r") as f:
        for place in sorted(f.readlines()):
            if place != '\n':
                PLACES.append(place[:-1] if place[-1] == '\n' else place)

    return list(PLACES)


def write_places() -> None:
    """Write list of places to file (`places.list`) """

    global PLACES

    with open(PLACES_PATH, 'w') as f:
        for place in sorted(PLACES):
            f.write(place + '\n')


read_places()
