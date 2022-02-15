import os
import time
import logging
from typing import Optional, Tuple
import discord
from discord.ext import commands, pages as pagination
from astrobot.types import FlushingString


class Logging(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.LOG_DIR = os.environ["LOG_DIR"]
        http_logger_init = self.init_discord_http_logger()
        if not os.path.exists(f"{self.LOG_DIR}/commands/"):
            os.mkdir(f"{self.LOG_DIR}/commands/")
        if not http_logger_init[0]:
            SystemExit(http_logger_init[1])

    def init_discord_http_logger(self) -> Tuple[bool, Optional[str]]:
        """Initialize pycord's logger for the Discord API HTTP/WebSocket connection

        Returns:
        - *tuple
            - *bool: whether or not initialization executed successfully
            - *Optional[str]: the error that was raised if initialization failed"""
        try:
            if not os.path.exists(f"{self.LOG_DIR}/http/"):
                os.mkdir(f"{self.LOG_DIR}/http/")
            log_time = int(time.time())
            logger = logging.getLogger("discord")
            logger.setLevel(logging.DEBUG)
            handler = logging.FileHandler(
                filename=f"{self.LOG_DIR}/http/{log_time}.log",
                encoding="utf-8",
                mode="w",
            )
            handler.setFormatter(
                logging.Formatter(
                    "[%(asctime)s][ %(levelname)s ] %(name)s: %(message)s"
                )
            )
            logger.addHandler(handler)
        except Exception as err:
            return (False, err)

        return (True, None)

    def astro_log_cmd(
        self, ctx: commands.Context, member: discord.Member
    ) -> Tuple[bool, Optional[str]]:
        """Log a command

        Returns:
        - *tuple
            - *bool: whether or not logging executed successfully
            - *Optional[str]: the error that was raised if logging failed"""
        try:
            _time = int(time.time())
            with open(f"{self.LOG_DIR}/commands/{member.name}.log", "a") as log:
                log.write(
                    f"{_time}::{ctx.command}::{', '.join([a.__str__() for a in ctx.args[1:] if not isinstance(a, commands.Context)])}::{', '.join([k.__str__() for k in ctx.kwargs.values()])}\n"
                )
        except Exception as err:
            return (False, err)

        return (True, None)

    @commands.command()
    async def get_logs(self, ctx, member: Optional[discord.Member], page_limit=15):
        if not member:
            member = ctx.author
        if not os.path.exists(f"{self.LOG_DIR}/commands/{member.name}.log"):
            await ctx.send(f"Logfile not found for '{member}'...")
            return

        def append_vals(l: list, v: str):
            l.append(
                discord.Embed(
                    title=f"Recent commands for user '{member}'", description=v
                )
            )

        pages = list()
        with open(f"{self.LOG_DIR}/commands/{member.name}.log", "r") as log:
            logs = log.readlines()
            logs.reverse()
            val = FlushingString()
            max_len = 14
            for x in range(len(logs)):
                _time, command, args, kwargs = logs[x].strip().split("::")
                val += f"[ **!{command} {args} {kwargs}** ]\a\a\a\a<t:{_time}:f>\n".replace(
                    "None", ""
                )
                if x == max_len:
                    append_vals(pages, val.flush())
                    max_len += 15
                    if len(pages) == page_limit:
                        break
            if val:
                append_vals(pages, val)

        paginator = pagination.Paginator(pages=pages)
        await paginator.send(ctx)

    @commands.Cog.listener()
    async def on_command(self, ctx):
        _log_success, _log_err = self.astro_log_cmd(ctx, ctx.author)
        if not _log_success:
            print(f"ERROR during command logging: {_log_err}")
        return
