import re
import time
import random
from typing import Optional
import discord
import asyncio
import sqlalchemy
from discord.ext import commands
from collections import namedtuple
from astrobot import __version__ as astrobot_version
from astrobot.user_sys.database import BugItem_DB
from astrobot.user_sys.database import session as db_session

bug_stack = []

#########
##      halys objects
#########


class BugPriority:
    def __init__(self) -> None:
        self.Priority = namedtuple("Priority", ["level", "description"])

    def init_from(self, level):
        if level == "LOW":
            return self.low()
        if level == "MEDIUM":
            return self.medium()
        if level == "HIGH":
            return self.high()
        if level == "CRUCIAL":
            return self.crucial()

    def low(self):
        return self.Priority(level="LOW", description="")

    def medium(self):
        return self.Priority(level="MEDIUM", description="")

    def high(self):
        return self.Priority(level="HIGH", description="")

    def crucial(self):
        return self.Priority(level="CRUCIAL", description="")


class BugStatus:
    def __init__(self) -> None:
        self.Status = namedtuple("Status", ["status", "desciption"])

    def init_from(self, status):
        if status == "NEW":
            return self.new()
        elif status == "ASSIGNED":
            return self.assigned()
        elif status == "TRIAGE":
            return self.triage()
        elif status == "OPEN":
            return self.open()
        elif status == "CLOSED":
            return self.closed()
        elif status == "PATCHED":
            return self.patched()
        else:
            return None

    def new(self):
        return self.Status(
            status="NEW",
            desciption="This is a fresh bug. No action has been taken yet.",
        )

    def assigned(self):
        return self.Status(
            status="ASSIGNED",
            desciption="This bug has been assigned to a maintainer. It should be triaged soon.",
        )

    def triage(self):
        return self.Status(
            status="TRIAGE",
            desciption="This bug is currently under review by the assigned individual.",
        )

    def open(self):
        return self.Status(
            status="OPEN",
            desciption="This bug has been triaged, prioritized accordingly, and is being fixed in order of it's priority.",
        )

    def closed(self):
        return self.Status(
            status="CLOSED",
            desciption="This bug has peen patched. The patch will be pushed to production with the next update.",
        )

    def patched(self):
        return self.Status(
            status="PATCHED",
            desciption="This bug's lifecyle is over. The patch has now been pushed to production and is considered patched.",
        )


class BugItem:

    __slots__ = (
        "timestamp",
        "reporter",
        "description",
        "reproduction_steps",
        "bot_version",
        "screenshot_url",
        "status",
        "assigned_to",
        "bug_id",
        "priority",
        "delete_at",
    )

    def __init__(self, **kwargs) -> None:
        self.timestamp = kwargs.get("timestamp", int(time.time()))
        self.reporter = kwargs["reporter"]
        self.description = kwargs["description"]
        self.reproduction_steps = kwargs.get("reproduction_steps")
        self.bot_version = kwargs["bot_version"]
        self.screenshot_url = kwargs.get("screenshot_url")
        self.status = kwargs.get("status", BugStatus().new())
        self.assigned_to = kwargs.get("assigned_to")
        self.bug_id = kwargs.get("bug_id", self.create_bug_id())
        self.priority = kwargs.get("priority", BugPriority().medium())
        self.delete_at = kwargs.get("delete_at")

    @staticmethod
    def create_bug_id():
        from os import urandom as random_bytes
        from hashlib import sha256 as hasher

        def _get_id():
            _id = hasher(random_bytes(24)).hexdigest()[4:12]
            while _id in bug_stack:
                _id = hasher(random_bytes(24)).hexdigest()[4:12]
            return _id

        bug_stack.append(_get_id())
        return bug_stack[-1]


#########
##      halys Cog
#########


class Halys(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: commands.Bot = bot
        self.bugs = {}
        self.commands = {
            "get_bugs": self.get_bugs,
            "status_info": self.status_info,
            "reprod": self.reprod,
            "track": self.track,
            "report": self.report,
        }
        self.technician_commands = {
            "assign": self.assign,
            "deassign": self.deassign,
            "delete": self.delete,
            "update_priority": self.update_priority,
            "update_status": self.update_status,
        }

    @staticmethod
    def _to_db_type(_bugitem: BugItem):
        return BugItem_DB(
            timestamp=str(_bugitem.timestamp),
            reporter=str(_bugitem.reporter.id),
            description=_bugitem.description,
            reproduction_steps=_bugitem.reproduction_steps,
            bot_version=_bugitem.bot_version,
            screenshot_url=_bugitem.screenshot_url,
            status=_bugitem.status.status,
            priority=str(_bugitem.priority.level),
            assigned_to=str(_bugitem.assigned_to) if _bugitem.assigned_to else "",
            bug_id=_bugitem.bug_id,
        )

    async def _from_db_type(self, _db_bugitem: BugItem_DB):
        return BugItem(
            timestamp=_db_bugitem.timestamp,
            reporter=await self.bot.fetch_user(int(_db_bugitem.reporter)),
            description=_db_bugitem.description,
            reproduction_steps=_db_bugitem.reproduction_steps,
            bot_version=_db_bugitem.bot_version,
            screenshot_url=_db_bugitem.screenshot_url,
            status=BugStatus().init_from(_db_bugitem.status),
            priority=BugPriority().init_from(_db_bugitem.priority),
            assigned_to=int(_db_bugitem.assigned_to)
            if _db_bugitem.assigned_to.isdecimal()
            else None,
            bug_id=_db_bugitem.bug_id,
        )

    def _add_to_db(self, _bug_item: BugItem):
        db_session.add(self._to_db_type(_bug_item))
        db_session.commit()

    def _flush_to_db(self, _bug_item: BugItem):
        _dbbugs = db_session.query(BugItem_DB)
        for item in _dbbugs:
            if item.bug_id == _bug_item.bug_id:
                _item = self._to_db_type(_bug_item)
                db_session.delete(item)
                db_session.add(_item)
                break
        db_session.commit()

    ###############################################################
    ##############      Technician Commands
    ###############################################################

    ########################################
    ########################################    -assign and -deassign

    async def assign(self, ctx, bug_id, assignee: discord.Member = None):
        _bug_item: BugItem = self.bugs.get(bug_id)

        if not _bug_item:
            await ctx.send(f"Bug '{bug_id}' can not be found.")
            return

        _tech_role: discord.Role = discord.utils.get(
            ctx.guild.roles, id=905942167963455498
        )
        if assignee and _tech_role not in assignee.roles:
            from astrobot.exceptions import HalysNotTechnician

            raise HalysNotTechnician("Can not assign a bug to a non-technician.")

        if not assignee:
            assignee = ctx.author

        _bug_item.status = BugStatus().assigned()
        _bug_item.assigned_to = assignee.id
        self._flush_to_db(_bug_item)
        await ctx.send(f"Assigned bug {bug_id} to {assignee.mention}.")

    async def deassign(self, ctx, bug_id):
        _bug_item: BugItem = self.bugs.get(bug_id)

        if not _bug_item:
            await ctx.send(f"Bug '{bug_id}'' can not be found.")
            return

        _bug_item.assigned_to = None
        self._flush_to_db(_bug_item)
        await ctx.send(f"Successfully removed assignment from bug {bug_id}")

    ########################################
    ########################################    -delete

    async def delete(self, ctx, _bug_id):
        if not self.bugs.get(_bug_id):
            await ctx.send(f"Bug ID '{_bug_id}' not found in database.")
            return
        await ctx.send(f"Are you sure you want to delete bug ID '{_bug_id}'? (yes/no)")

        def check(m):
            return m.channel == ctx.channel and m.author == ctx.author

        _res = await self.bot.wait_for("message", check=check)
        _res = _res.content
        if _res == "no":
            await ctx.send(f"Leaving '{_bug_id}' in tact... returning")
            return
        elif _res != "yes":
            await ctx.send("Unrecognized response... returning")
            return

        del self.bugs[_bug_id]  # delete report from running mem

        db_session.execute(
            sqlalchemy.delete(BugItem_DB)
            .where(BugItem_DB.bug_id == _bug_id)
            .execution_options(synchronize_session="fetch")
        )
        db_session.commit()
        await ctx.send(f"Successfully deleted '{_bug_id}'")

    ########################################
    ########################################    -update_priority

    async def update_priority(self, ctx, _bug_id: str, _new_priority: str = None):
        if not _new_priority:
            await ctx.send("Please provide a priority to update this bug to.")
            await ctx.send(
                "i.e. 'low', 'normal', 'medium', 'high', 'crucial', 'emergency'"
            )
            return

        _bug_item: BugItem = self.bugs.get(_bug_id)
        if not _bug_item:
            await ctx.send(f"Could not find bug ID {_bug_id}, sorry.")
            return

        if _new_priority.lower() == "low":
            _bug_item.priority = BugPriority().low()
        if _new_priority.lower() == "medium":
            _bug_item.priority = BugPriority().medium()
        if _new_priority.lower() == "high":
            _bug_item.priority = BugPriority().high()
        if _new_priority.lower() == "crucial":
            _bug_item.priority = BugPriority().crucial()
        else:
            return

        self._flush_to_db(_bug_item)

        await ctx.send(
            f"Successfully upated priority of '{_bug_id}' to '{_new_priority.upper()}'"
        )

    ########################################
    ########################################    -update_status

    async def update_status(self, ctx, _bug_id: str, _new_status: str = None):
        if not _new_status:
            await ctx.send("Please provide a status to update this bug to.")
            await ctx.send(
                "i.e. 'new', 'assigned', 'triage', 'open', 'closed', 'patched'"
            )
            return

        _bug_item: BugItem = self.bugs.get(_bug_id)
        if not _bug_item:
            await ctx.send(f"Could not find bug ID {_bug_id}, sorry.")
            return

        if _new_status.lower() == "new":
            _bug_item.status = BugStatus().new()
        elif _new_status.lower() == "assigned":
            if not _bug_item.assigned_to:
                await ctx.send(
                    "Bug needs to be assigned to someone first, use !bug assign [assignee]"
                )
                return
            _bug_item.status = BugStatus().assigned()
        elif _new_status.lower() == "triage":
            _bug_item.status = BugStatus().triage()
        elif _new_status.lower() == "open":
            _bug_item.status = BugStatus().open()
        elif _new_status.lower() == "closed":
            _bug_item.status = BugStatus().closed()
            _bug_item.assigned_to = None
        elif _new_status.lower() == "patched":
            _bug_item.status = BugStatus().patched()
            _bug_item.delete_at = int(time.time()) + 2592000  # delete after 30 days
        else:
            return

        self._flush_to_db(_bug_item)

        await ctx.send(
            f"Successfully upated status of '{_bug_id}' to '{_new_status.upper()}'"
        )

    ###############################################################
    ##############          User Commands
    ###############################################################

    ########################################
    ########################################    -status_info

    async def status_info(self, ctx, _status: str):
        if _status.lower() == "new":
            _r = BugStatus().new()
        elif _status.lower() == "assigned":
            _r = BugStatus().assigned()
        elif _status.lower() == "triage":
            _r = BugStatus().triage()
        elif _status.lower() == "open":
            _r = BugStatus().open()
        elif _status.lower() == "closed":
            _r = BugStatus().closed()
        elif _status.lower() == "patched":
            _r = BugStatus().patched()

        await ctx.send(f"{_r.status}: '{_r.desciption}'")

    ########################################
    ########################################    -get_bugs

    async def get_bugs(self, ctx, subcmd: str = None):
        # TODO: make embed into ID + short description + reported by if requester is tech
        _list = []
        _list_str = ""
        if subcmd == "new":
            for bug in self.bugs:
                if self.bugs[bug].status.status.lower() == "new":
                    _list.append(
                        f"{self.bugs[bug].bug_id} ({self.bugs[bug].description[0:25]})"
                    )
                    if len(_list) == 10:
                        break
            ctr = 1
            for _id in _list:
                _list_str += f"{ctr}. {_id}\n"
                ctr += 1
            embed = discord.Embed(title=f"**New Bugs**", description=f"**{_list_str}**")
            await ctx.send(embed=embed)
        elif subcmd == "assigned":
            _assignee = ctx.author

            for bug in self.bugs:
                if not self.bugs[bug].assigned_to:
                    continue
                if await self.bot.fetch_user(self.bugs[bug].assigned_to) == _assignee:
                    _list.append(
                        f"{self.bugs[bug].bug_id} ({self.bugs[bug].description[0:25]})"
                    )
            ctr = 1
            for _id in _list:
                _list_str += f"{ctr}. {_id}\n"
                ctr += 1
            embed = discord.Embed(
                title=f"**Bugs assigned to {_assignee}**",
                description=f"**{_list_str}**",
            )
            await ctx.send(embed=embed)
        elif subcmd:
            for bug in self.bugs:
                if self.bugs[bug].status.status.lower() == subcmd:
                    _list.append(
                        f"({self.bugs[bug].bug_id}) {self.bugs[bug].description[0:25]}"
                    )
            ctr = 1
            for _id in _list:
                _list_str += f"{ctr}. {_id}\n"
                ctr += 1
            embed = discord.Embed(
                title=f"**Bugs matching status: '{subcmd.upper()}'**",
                description=f"**{_list_str}**",
            )
            await ctx.send(embed=embed)
        else:
            _tech_role: discord.Role = discord.utils.get(
                ctx.guild.roles, id=905942167963455498
            )
            for bug in self.bugs:
                if _tech_role in ctx.author.roles:
                    _list.append(
                        f"{self.bugs[bug].bug_id} ({self.bugs[bug].description[0:25]})"
                    )
                elif self.bugs[bug].reporter == ctx.author:
                    _list.append(
                        f"{self.bugs[bug].bug_id} ({self.bugs[bug].description[0:25]})"
                    )
            ctr = 1
            for _id in _list:
                _list_str += f"{ctr}. {_id}\n"
                ctr += 1
            embed = discord.Embed(
                title=f"**Bugs reported by {ctx.author}**",
                description=f"**{_list_str}**",
            )
            await ctx.send(embed=embed)
        return

    ########################################
    ########################################    -reprod

    async def reprod(self, ctx, bug_id):
        _bug_item: BugItem = self.bugs.get(bug_id)
        if not _bug_item:
            # TODO: add db check
            await ctx.send(f"Could not find bug ID {bug_id}, sorry.")
            return

        embed = discord.Embed(
            title=f"Reproduction steps for bug '{bug_id}':",
            description=_bug_item.reproduction_steps,
        )

        await ctx.send(embed=embed)

    ########################################
    ########################################    -track

    async def track(self, ctx, bug_id):
        _bug_item: BugItem = self.bugs.get(bug_id)
        if not _bug_item:
            # TODO: add db check
            await ctx.send(f"Could not find bug ID {bug_id}, sorry.")
            return

        embed = (
            discord.Embed(title=f"Bug {bug_id}")
            .add_field(name="**Priority:**", value=_bug_item.priority.level)
            .add_field(name="**Status:**", value=_bug_item.status.status)
            .add_field(name="**Reported (epoch time):**", value=_bug_item.timestamp)
            .add_field(name="**Reported by:**", value=_bug_item.reporter.mention)
            .add_field(name="**Bot version:**", value=_bug_item.bot_version)
            .set_footer(
                text=f"To see reproduction steps for this bug, run '!bug reprod {bug_id}'"
            )
        )
        if len(_bug_item.description) > 97:
            embed.add_field(
                name="**Description**", value=f"{_bug_item.description[0:97]}..."
            )
        else:
            embed.add_field(name="**Description**", value=_bug_item.description)
        if _bug_item.screenshot_url:
            embed.add_field(name="**Screenshot:**", value=_bug_item.screenshot_url)
        if _bug_item.assigned_to:
            _uobj = await self.bot.fetch_user(_bug_item.assigned_to)
            embed.add_field(name="**Assigned to:**", value=_uobj.mention)
        await ctx.send(embed=embed)

    ###############################################################
    ##############          Report Command ( -report )
    ###############################################################

    async def is_dmable(self, ctx):
        try:
            await ctx.author.send(
                "Hello, I heard you want to report a bug! First, may I ask what version I was when this bug occured? If it's the current version, say 'current'."
            )
            return True
        except discord.errors.Forbidden:
            return False

    async def report(self, ctx):
        # TODO: make ambiguous function, i.e. (-report bug & -report ticket both valid)
        # implemet ticketing system, ask victor if details needed

        # TODO: implement logic to store unfinished report for certain time period
        _reporter: discord.Member = ctx.author
        _report_channel: discord.TextChannel = ctx.channel

        def is_same(m):
            return m.channel == _report_channel and m.author == _reporter

        _is_dmable = await self.is_dmable(ctx)

        if not isinstance(_report_channel, discord.DMChannel) and _is_dmable:
            # if request was invoked outside of DMChannel, create one and move to it
            _report_channel = await ctx.author.create_dm()
        if not _is_dmable:
            # TODO: implement check for if channel name already exists before creating
            _report_channel = await ctx.guild.create_text_channel(
                name=f"tmp-bug-{random.randint(1000, 9999)}",
                category=discord.utils.get(ctx.guild.categories, id=905946193924853801),
            )
            await _report_channel.send(
                "Hello, I heard you want to report a bug! First, may I ask what version I was when this bug occured? If it's the current version, say 'current'."
            )

        ##################### Get bug version
        try:
            _version = await self.bot.wait_for("message", timeout=300.0, check=is_same)
            if _version.content == "current":
                _version = astrobot_version
            else:
                _version = _version.content
        except asyncio.TimeoutError:
            await _report_channel.send(
                "Sorry, I've timed out. If you want still want to fill out this report, run '!bug report' again."
            )
            return

        ##################### Get issue description
        await _report_channel.send(
            "Thanks! Now, may I get a short description of the issue? (less than 1000 characters)"
        )

        try:
            _description = await self.bot.wait_for(
                "message", timeout=300.0, check=is_same
            )
        except asyncio.TimeoutError:
            await _report_channel.send(
                "Sorry, I've timed out. If you want still want to fill out this report, run '!bug report' again."
            )
            return

        _description = _description.content[
            0:1000
        ]  # truncate description if more than 1000 characters

        ##################### Get reproduction steps
        await _report_channel.send(
            'What are the steps than can be taken to reproduce this issue? (i.e. "1...2...3...")'
        )

        try:
            _steps_to_reproduce = await self.bot.wait_for(
                "message", timeout=300.0, check=is_same
            )
            _steps_to_reproduce = _steps_to_reproduce.content
        except asyncio.TimeoutError:
            await _report_channel.send(
                "Sorry, I've timed out. If you want still want to fill out this report, run '!bug report' again."
            )
            return

        ##################### Get screenshot
        await _report_channel.send(
            "Dope! Finally, do you have a screenshot of the issue? If so, just send them. If not, just say 'no'"
        )

        try:
            _screenshots = await self.bot.wait_for(
                "message", timeout=300.0, check=is_same
            )
        except asyncio.TimeoutError:
            await _report_channel.send(
                "Sorry, I've timed out. If you want still want to fill out this report, run '!bug report' again."
            )
            return

        if not _screenshots.content:
            _screenshots = _screenshots.attachments[0].url
        else:
            if _screenshots.content == "no":
                _screenshots = None
            else:
                attempts = 1
                while _screenshots.content != "no":
                    if attempts == 5:
                        await _report_channel.send(
                            "I'm sorry I'm not able to understand you right now. You can try running '!bug report' again, or if this is a repeated issue, you can file an issue at https://github.com/astro-devel/halys/issues/new, or send an email to my development team at 'astrobot.devel@gmail.com' with the subject '(HELENA REPORTING ISSUE)', with an attached screenshot of the issue, or message logs, if possible."
                        )
                        return
                    await _report_channel.send(
                        "Sorry, I didn't understand that. If you have a screenshot, simply send it as an attachment. If not, say 'no'"
                    )
                    try:
                        _screenshots = await self.bot.wait_for(
                            "message", timeout=300.0, check=is_same
                        )
                    except asyncio.TimeoutError:
                        await _report_channel.send(
                            "Sorry, I've timed out. If you want still want to fill out this report, run '!bug report' again."
                        )
                        return
                    attempts += 1

        if str(_screenshots) == "no":
            await _report_channel.send(
                "Ok, sounds good! Let me get this issue put in the system for you, and I'll be right back with your trackable Bug ID!"
            )
        else:
            await _report_channel.send(
                "Thanks! Let me get this issue put in the system for you, and I'll be right back with your trackable Bug ID!"
            )
        bug_item = BugItem(
            reporter=_reporter,
            description=_description,
            reproduction_steps=_steps_to_reproduce,
            bot_version=_version,
            screenshot_url=_screenshots,
        )

        ##################### Add bug to database and return bug ID
        self._add_to_db(bug_item)

        await _report_channel.send(
            f"Alright! Here is your trackable ID! To track the status of this bug, just use the command '!bug track [BUG_ID]'"
        )
        await _report_channel.send(bug_item.bug_id)
        self.bugs[bug_item.bug_id] = bug_item
        return

    async def _parse_args(self, ctx, args: str) -> tuple:
        args = args.split()
        # user commands
        if args[0] == "help":
            await ctx.send(
                """```
Halys bug reporter commands:
( commands with [ TECHNICIAN ] are only for use by bot technicians. )

-\thelp: show this message
-\tget: get all bugs reported by you
-\t[ TECHNICIAN ] get assigned: get all bugs assigned to you
-\tget [status]: get all bugs for a given status
-\twhatis status [status]: get info about a given status
-\ttrack [bug ID]: track a given bug by ID
-\treprod [bug ID]: get reproduction steps, if applicable, for a given bug
-\treport: report a new bug. astrobot will DM you for reporting details.
-\t[ TECHNICIAN ] assign: assign a bug to yourself
-\t[ TECHNICIAN ] assign [@user]: assign a bug to a given user, by mention
-\t[ TECHNICIAN ] deassign [bug ID]: remove assignment from a given bug
-\t[ TECHNICIAN ] delete [bug ID]: delete a given bug from the database
-\t[ TECHNICIAN ] status [bug ID] [status]: update status for a given bug```"""
            )
            return None, None
        elif args[0] == "get":
            return (self.commands["get_bugs"], [args[1]] if len(args) > 1 else [])
        elif args[0] == "whatis":
            if args[1] == "status":
                return (self.commands["status_info"], [args[2]])
            elif args[1] == "priority":
                pass  # FNI
        elif args[0] == "track":
            return (self.commands["track"], [args[1]])
        elif args[0] == "reprod":
            return (self.commands["reprod"], [args[1]])
        elif args[0] == "report":
            return (self.commands["report"], ())
        # technician commands
        elif args[0] == "assign":
            return (
                self.technician_commands["assign"],
                (args[1], await ctx.guild.fetch_member(re.sub("[<@!>]", "", args[2])))
                if len(args) > 2
                else [args[1]],
            )
        elif args[0] == "deassign":
            return (self.technician_commands["deassign"], [args[1]])
        elif args[0] == "delete":
            return (self.technician_commands["delete"], [args[1]])
        elif args[0] == "status":
            return (self.technician_commands["update_status"], (args[1], args[2]))

    async def _run(self, ctx, args) -> Optional[str]:
        cmd, cmd_args = await self._parse_args(ctx, args)
        if cmd:
            await cmd(ctx, *cmd_args)

    @commands.command()
    async def bug(self, ctx, *, args: str):
        await self._run(ctx, args)

    @commands.Cog.listener()
    async def on_ready(self):
        _dbbugs = db_session.query(BugItem_DB)
        for item in _dbbugs:
            self.bugs[item.bug_id] = await self._from_db_type(item)
