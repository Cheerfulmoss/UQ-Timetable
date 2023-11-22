import discord
from discord.ext import commands
import logging
from datetime import datetime, timedelta
import json
import os
import re
from .api.timetable_api_calls import CourseTimetable, TTableInputs

log_format = "[%(asctime)s] [%(levelname)-8s] %(name)s: %(message)s"
logging.basicConfig(level=logging.INFO, format=log_format)
logger = logging.getLogger(__name__)


class BaseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cache_path = f"{os.getcwd()}/cogs/base-files/api-calls-cache.json"
        self.default_act_cats = [
            "activity", "day", "location", "start-time", "end-time",
            "department", "group",
        ]

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"{self.__class__.__name__} cog is ready.")

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
        chunked_keys = [list(course_activities.keys())[i:i + 9]
                        for i in range(0, len(course_activities.keys()), 9)]

        chunked_acts = []
        for chunk in chunked_keys:
            chunked_data = {
                key: course_activities[key]
                for key in chunk
            }
            chunked_acts.append(chunked_data)

        for index, chunk in enumerate(chunked_acts):
            activities_embed = discord.Embed(
                title=f"Activities for {course} - P{index}",
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

        if data.get(course) is not None:
            request_date = datetime.fromisoformat(data.get(course).get(
                "request-date"))
            now = datetime.now()

            date_difference = now - request_date
            if date_difference < timedelta(days=7):
                return data.get(course).get("course-activities")

        course_obj = self.get_course_obj(course, semester, campus)
        logger.info("API call made.")

        with open(self.cache_path, "r") as file:
            data = json.load(file)

            activities = course_obj.get_activities()
            fixed_activities = {" ".join(key): value
                                for key, value in activities.items()}

            data[course] = {
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
