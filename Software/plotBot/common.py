from . import constants

old_print = print

def print(*args):
    global old_print
    if constants.ENABLE_PRINTING:
        old_print(*args)


def print_exception(*args):
    print('[EXCEPTION]:', *args)


def print_info(*args):
    print('[INFO]:', *args)
