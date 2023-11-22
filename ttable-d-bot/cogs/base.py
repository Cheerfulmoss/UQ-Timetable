import discord
import logging
import json
import os
import re

from time import perf_counter_ns
from discord.ext import commands, tasks
from datetime import datetime, timedelta
from .api.timetable_api_calls import CourseTimetable, TTableInputs

log_format = "[%(asctime)s] [%(levelname)-8s] %(name)s: %(message)s"
logging.basicConfig(level=logging.INFO, format=log_format)
logger = logging.getLogger(__name__)

allowed_accounts = [398437778788188163]


def is_allowed_account(ctx):
    return ctx.author.id in allowed_accounts


class BaseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cache_path = f"{os.getcwd()}/cogs/base-files/api-calls-cache.json"
        self.admin_path = f"{os.getcwd()}/cogs/base-files/admin.json"
        self.default_act_cats = [
            "activity", "day", "location", "start-time", "end-time",
            "department", "group",
        ]

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"{self.__class__.__name__} cog is ready.")
        self.check_cache.start()

    @commands.Cog.listener()
    async def on_shutdown(self):
        logger.info(f"{self.__class__.__name__} cog shutting down. Stopping "
                    f"periodic tasks.")
        self.check_cache.stop()

    @commands.command(name="ping", help="Ping the bot")
    async def ping(self, ctx):
        await ctx.send("Pong!")

    @commands.command(name="display-course-activities",
                      help="Get all activities for a course")
    async def display_activities(self, ctx):
        args = ctx.message.content.removeprefix(
            f"{self.bot.command_prefix}{ctx.command.name}"
        ).strip()

        pattern = r'-\w+\s+([^\s]+)|--(\w+)'
        matches = re.findall(pattern, args)

        optional = ""
        if len(matches) < 3:
            await ctx.send(embed=self.display_activities_command_error(ctx))
            return
        if len(matches) == 3:
            course, semester, campus = (match[0] or match[1]
                                        for match in matches)
        else:
            course, semester, campus, *optional = (match[0] or match[1]
                                                   for match in matches)
        try:
            course_activities = self.get_course_activities(course, semester,
                                                           campus)
        except ValueError:
            await ctx.send(embed=self.display_activities_command_error(ctx))
            return

        # https://stackoverflow.com/questions/312443/how-do-i-split-a-list-into-equally-sized-chunks
        chunked_keys = [list(course_activities.keys())[i:i + 9] for i in
                        range(0, len(course_activities.keys()), 9)]
        chunked_acts = [dict((key, course_activities[key]) for key in chunk) for
                        chunk in chunked_keys]

        course_key = f"{course}-{semester}-{campus}"

        for index, chunk in enumerate(chunked_acts):
            activities_embed = discord.Embed(
                title=f"Activities for {course_key} - P{index}",
                description="Activities are lectures, tutorials, practicals, "
                            "etc.",
                colour=discord.Colour.dark_magenta()
            )
            for activity, data in chunk.items():
                activities_embed.add_field(
                    name=activity,
                    value=self.format_activity_data(data, optional)
                )
            await ctx.send(embed=activities_embed)

    @commands.command(name="clear-cache",
                      help="Clear the cache")
    @commands.check(is_allowed_account)
    async def clear_cache(self, ctx):
        with open(self.cache_path, "w") as file:
            json.dump({}, file)

        await ctx.send("Cache cleared")

    @tasks.loop(hours=2)
    async def check_cache(self):
        with open(self.admin_path, "r") as file:
            admin_data = json.load(file)

        if ("last-check-date" not in admin_data or
                datetime.now() - datetime.fromisoformat(admin_data.get(
                    "last-check-date")) >= timedelta(
                    days=1)):
            logger.info("Checking cache...")
            with open(self.admin_path, "r") as file:
                cache_data = json.load(file)

            for key, value in cache_data.items():
                if ("request-date" not in value or
                        datetime.now() - datetime.fromisoformat(value.get(
                            "request-date")) >= timedelta(
                            days=7)):
                    logger.info(f"Cache data for {key} removed.")
                    cache_data.pop(key)

            with open(self.admin_path, "w") as file:
                json.dump(cache_data, file)

            with open(self.admin_path, "w") as file:
                admin_data["last-check-date"] = datetime.now().isoformat()
                json.dump(admin_data, file)
        logger.info("Cache check complete.")

    def format_activity_data(self, data, optional):
        message = []

        chosen_cats = self.default_act_cats[::1]
        chosen_cats.extend(set(optional))

        for key in chosen_cats:
            cat_data = data[key]

            if not cat_data:
                continue

            if key == "schedule":
                cat_data = ", ".join(cat_data)
            if key == "group":
                cat_data = ", ".join(" ".join(paired_act)
                                     for paired_act in cat_data)
            if key == "department":
                cat_data = cat_data.removesuffix("SCHL")
            message.append(
                f"- {key.title()}: {cat_data}"
            )
        return "\n".join(message)

    def display_activities_command_error(self, ctx):
        message = ("")
        embed = discord.Embed(
            title=f"Command ERROR - {ctx.command.name}",
            description=message,
            colour=discord.Colour.red())
        return embed

    def get_course_activities(self, course: str, semester: str, campus: str):
        with open(self.cache_path, "r") as file:
            data = json.load(file)

        course_key = f"{course}-{semester}-{campus}"

        if course_key in data and "request-date" in data[course_key]:
            request_date = datetime.fromisoformat(
                data[course_key]["request-date"]
            )
            now = datetime.now()

            date_difference = now - request_date
            if date_difference < timedelta(days=7):
                return data[course_key]["course-activities"]

        start = perf_counter_ns()
        course_obj = self.get_course_obj(course, semester, campus)
        duration = round((perf_counter_ns() - start) / 1000000, 5)
        logger.info(f"API call made, {duration} ms")

        with open(self.cache_path, "r") as file:
            data = json.load(file)

            activities = course_obj.get_activities()
            fixed_activities = {" ".join(key): value
                                for key, value in activities.items()}

            data[course_key] = {
                "course-activities": fixed_activities,
                "request-date": datetime.now().isoformat()
            }
        with open(self.cache_path, "w") as file:
            json.dump(data, file)
        return fixed_activities

    @staticmethod
    def get_course_obj(course: str, semester: str, campus: str):
        (semester, campus, form) = (
            TTableInputs.convert(semester),
            TTableInputs.convert(campus),
            TTableInputs.Form.IN
        )
        course_obj = CourseTimetable(course, semester=semester,
                                     campus_id=campus, form_type=form)

        return course_obj


async def setup(bot):
    await bot.add_cog(BaseCog(bot))
    return bot
