import os
import signal
from multiprocessing import Process
from discord import __version__ as discordpy_version
from mochji import __version__ as mochji_version
from mochji import util
from mochji.client import bot

global running_proc
running_proc: int | None = None

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
        case "purge_logs":
            for file in os.listdir("logs"):
                os.remove(f"logs/{file}")
        case "bye" | "quit" | 'q':
            if running_proc:
                kill_client()
            util.cleanup_and_quit(0)
        case _:
            print(f"Unrecognized command: '{cmd}'")