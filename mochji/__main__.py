import os
import signal
from multiprocessing import Process
from discord import __version__ as discordpy_version
from mochji import __version__ as mochji_version
from mochji import util
from mochji.client import bot
from mochji.exceptions import MochjiEnvironmentVariableNotFound

global running_proc
running_proc: int | None = None

def _check_environ():
    '''Check that all necessary environment variables are defined'''
    required_environs = ["ROLE_CHANNEL_ID", "BOT_TOKEN"]
    environs_not_found = []
    for env in required_environs:
        try:
            os.environ[env]
        except KeyError:
            environs_not_found.append(env)

    if len(environs_not_found) > 0:
        err = "\nSome required variables were not detected in the current environment\n"
        err += "Please define the following environment variable(s) to proceed:\n"
        for env in environs_not_found:
            err += f"\t- {env} \n"
        raise MochjiEnvironmentVariableNotFound(err)


def kill_client():
    global running_proc
    os.kill(running_proc, signal.SIGTERM)
    running_proc = None

print(f"mochjiBot v{mochji_version} REPL (discord.py v{discordpy_version})")
while True:
    cmd = input("> ")
    match cmd:
        case "help":
            util.help_menu()
        case "start":
            _check_environ()
            bot_proc = Process(target=bot.start_client)
            bot_proc.start()
            running_proc = bot_proc.pid
        case "stop":
            if running_proc:
                kill_client()
            else:
                print("Nothing to kill, bot is already dead.")
        case "status":
            if running_proc:
                print("Bot is running...")
            else:
                print("Bot is not running...")
        case "bot_pid":
            if running_proc:
                print(f"Bot is running on PID: {running_proc}")
            else:
                print("Bot is not running...")
        case "purge_logs":
            for file in os.listdir("logs"):
                os.remove(f"logs/{file}")
        case "bye" | "quit" | 'q':
            if running_proc:
                kill_client()
            util.cleanup_and_quit(0)
        case _:
            print(f"Unrecognized command: '{cmd}'")