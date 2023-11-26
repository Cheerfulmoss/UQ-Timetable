import discord
import logging
import json
import os
import re

from time import perf_counter_ns
from discord.ext import commands, tasks
from datetime import datetime, timedelta

from api.timetable_api_calls import CourseTimetable
from api.TTableInputs import TTableInputs

from json_h.read import JsonReader as jr
from json_h.write import JsonWriter as jw

log_format = "[%(asctime)s] [%(levelname)-8s] %(name)s: %(message)s"
logging.basicConfig(level=logging.INFO, format=log_format)
logger = logging.getLogger(__name__)

allowed_accounts = [398437778788188163]


def is_allowed_account(ctx):
    return ctx.author.id in allowed_accounts


class BaseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        cache_path = f"{os.getcwd()}/base-files/api-calls-cache.json"
        admin_path = f"{os.getcwd()}/base-files/admin.json"

        self.paths = {"cache": cache_path,
                      "admin": admin_path}

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
        except ValueError as e:
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

    def display_activities_command_error(self, ctx):
        message = ("Given inputs are invalid!\n"
                   f"`{self.bot.command_prefix}"
                   f"{self.display_activities.name} "
                   "-cs <course code> -s <semester> -c <campus> "
                   "[--schedule]`\n"
                   "Order does **_not_** matter")
        embed = discord.Embed(
            title=f"Command ERROR - {ctx.command.name}",
            description=message,
            colour=discord.Colour.red())
        embed.add_field(
            name="**<course code>**",
            value="As an example, CSSE2010"
        )
        embed.add_field(
            name="**<semester>**",
            value="\n".join(f"- {semester}"
                            for semester in
                            TTableInputs.Semester.__members__.values())
        )
        embed.add_field(
            name="**<campus>**",
            value="\n".join(f"- {campus}"
                            for campus in
                            TTableInputs.Campus.__members__.values())
        )
        return embed

    @commands.command(name="clear-cache",
                      help="Clear the cache")
    @commands.check(is_allowed_account)
    async def clear_cache_command(self, ctx):
        jw().clear_json(self.paths["cache"], logger=logger)
        await ctx.send(f"`{os.path.basename(self.paths["cache"])}` cleared")

    # 1 MINUTE FOR TESTING - 24 HOURS FOR FINAL (as a minimum)
    @tasks.loop(minutes=1)
    async def check_cache(self):
        admin_data = jr().extract_from_json_cache(self.paths["admin"],
                                                  logger=logger)

        if ("last-check-date" not in admin_data or
                datetime.now() - datetime.fromisoformat(admin_data.get(
                    "last-check-date")) >= timedelta(
                    days=1)):
            logger.info("Checking cache...")
            cache_data = jr().extract_from_json_cache(self.paths["cache"],
                                                      logger=logger)

            for key, value in cache_data.items():
                if ("request-date" not in value or
                        datetime.now() - datetime.fromisoformat(value.get(
                            "request-date")) >= timedelta(
                            days=7)):
                    logger.info(f"Cache data for {key} removed.")
                    cache_data.pop(key)

            jw().write(self.paths["cache"], cache_data, logger=logger)

            admin_data["last-check-date"] = datetime.now().isoformat()
            jw().write(self.paths["admin"], admin_data, logger=logger)

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

    def get_course_activities(self, course: str, semester: str, campus: str):
        cache_data = jr().extract_from_json_cache(self.paths["cache"],
                                                  logger=logger)

        course_key = f"{course}-{semester}-{campus}"

        if (course_key in cache_data and
                "request-date" in cache_data[course_key]):
            request_date = datetime.fromisoformat(
                cache_data[course_key]["request-date"]
            )
            now = datetime.now()

            date_difference = now - request_date
            if date_difference < timedelta(days=7):
                return cache_data[course_key]["course-activities"]

        start = perf_counter_ns()
        course_obj = self.get_course_obj(course, semester, campus)
        duration = round((perf_counter_ns() - start) / 1000000, 5)
        logger.info(f"API call made, {duration} ms.")

        activities = course_obj.get_activities()
        fixed_activities = {" ".join(key): value
                            for key, value in activities.items()}

        cache_data[course_key] = {
            "course-activities": fixed_activities,
            "request-date": datetime.now().isoformat()
        }

        jw().write(self.paths["cache"], cache_data, logger=logger)
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
