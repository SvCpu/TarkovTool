from .is_runing import is_tarkov_running

def active()->bool:
    return is_tarkov_running()