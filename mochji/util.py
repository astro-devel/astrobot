from typing import NoReturn

def help_menu() -> NoReturn:
    print("mochjiBot REPL commands:\n\
\"help\" -> print this menu\n\
\"quit\" -> quit the REPL\n\
\"start\" -> start the client service\n\
\"status\" -> get current status of client, if running\n\
\"stop\" -> stop the client service, if running")

def cleanup_and_quit(code: int) -> NoReturn:
    raise SystemExit(code)

def collect_to_string(_list: list | tuple) -> str:
    _str = ""
    for item in _list:
        _str += item + " "
    
    return _str