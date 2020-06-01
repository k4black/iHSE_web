import typing as tp

import configparser

from utils.auxiliary import logger


CONFIG_PATH = '/var/conf/ihse/ihse.ini'


""" ---===---==========================================---===--- """
"""                   Config file interactions                   """
""" ---===---==========================================---===--- """


CREDITS_TOTAL = 0
CREDITS_MASTER = 0
CREDITS_LECTURE = 0
CREDITS_ADDITIONAL = 0  # Maximum allowed additional credits
NUMBER_TEAMS = 0


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
    """ Set global config values """

    global CREDITS_TOTAL, CREDITS_MASTER, CREDITS_LECTURE, CREDITS_ADDITIONAL, NUMBER_TEAMS

    CREDITS_TOTAL = config_dict['CREDITS_TOTAL']
    CREDITS_MASTER = config_dict['CREDITS_MASTER']
    CREDITS_LECTURE = config_dict['CREDITS_LECTURE']
    CREDITS_ADDITIONAL = config_dict['CREDITS_ADDITIONAL']

    NUMBER_TEAMS = config_dict['NUMBER_TEAMS']


def read_config() -> None:
    """Read and save config file (`ihse.ini`) """

    # print('========= Read config file =========')
    logger('read_config()', '==== Read config file ====', type_='LOG')

    global CREDITS_TOTAL, CREDITS_MASTER, CREDITS_LECTURE, CREDITS_ADDITIONAL, NUMBER_TEAMS

    # Check file exist. or auto create
    with open(CONFIG_PATH, "w+") as f:
        pass

    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)

    try:
        CREDITS_TOTAL = int(config['CREDITS']['total'])
        CREDITS_MASTER = int(config['CREDITS']['masterclass'])
        CREDITS_LECTURE = int(config['CREDITS']['lecture'])
        CREDITS_ADDITIONAL = int(config['CREDITS']['additional'])

        NUMBER_TEAMS = int(config['TEAMS']['number'])
    except KeyError:
        logger('read_config()', 'No config file. Using default values', type_='ERROR')
        CREDITS_TOTAL = 300
        CREDITS_MASTER = 15
        CREDITS_LECTURE = 15
        CREDITS_ADDITIONAL = 5
        NUMBER_TEAMS = 5

    # print('===== End config file reading ======')
    logger('read_config()', '==== End config file reading ====', type_='LOG')


def write_config() -> None:
    """Write current configuration to config file (`ihse.ini`) """

    global CREDITS_TOTAL, CREDITS_MASTER, CREDITS_LECTURE, CREDITS_ADDITIONAL, NUMBER_TEAMS

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


read_config()
