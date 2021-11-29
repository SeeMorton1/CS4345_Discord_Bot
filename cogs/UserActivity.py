from discord.ext import commands, tasks
from discord import Embed
import discord
import discord as d
from discord import channel
from discord import guild
from database_func import database_func
from datetime import datetime
import asyncio
import math


class UserActivity(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.test = database_func.getInstance()
        #     get database singleton instance
        self.playtime = {}

    @commands.Cog.listener()
    async def on_ready(self):
        print("READy")
        self.collect_play_time.start()
        # collecting users playtime
        self.show_play_time.start()
        # display playtime daily
        self.warn_play_time.start()
        # warn users for overplay
        self.change_warned_status.start()
        # change warning status daily
        self.clear_playtime.start()
    #     cleay previous day actvity

    @commands.command()
    async def change_playtime(self, ctx, time:float):
        # update playtme
        await ctx.send(ctx.author.name + " has updated his playtime limit to " + str(time)+" hours" )
        time = time * 3600
        # convert hours to seconds
        self.test.change_play_time_limit(ctx.author.id, time)
        return

    @commands.command()
    async def status(self, ctx, member: discord.Member):
        # get someone status
        # https://discordpy.readthedocs.io/en/stable/intents.html
        # https://stackoverflow.com/questions/67149879/how-to-get-user-activity-in-discord-py
        if member.activity is None:
            await ctx.send(member.display_name + " is not doing anything now")
        else:
            type = str(member.activity.type)
            if "ActivityType." in type:
                type = type.replace("ActivityType.", "")
                if "custom" not in type:
                    await ctx.send(member.name + " is " + type + " " + member.activity.name)
                else:
                    await ctx.send(member.name + " is doing " + member.activity.name)

        return

    @status.error
    async def status_error(self, ctx: commands.Context, error: commands.CommandError):
        # error handling for status error
        if isinstance(error, commands.CommandOnCooldown):
            message = f"This command is on cooldown. Please try again after {round(error.retry_after, 1)} seconds."
        elif isinstance(error, commands.MissingPermissions):
            message = "You are missing the required permissions to run this command!"
        elif isinstance(error, commands.MissingRequiredArgument):
            message = f"Missing a required argument: {error.param}"
        elif isinstance(error, commands.ConversionError):
            message = str(error)
        else:
            message = "Oh no! Something went wrong while running the command!"

        await ctx.send(message, delete_after=10)

    @commands.command()
    async def status_self(self, ctx):
        # get self play time
        msg = ctx.author.name + "\n"
        results_list = self.test.get_user_activities(ctx.author.id)
        # list of tuples where [0] is activity and [1] is time
        for activity in results_list:
            act_time = activity[1]
            act_hour = math.floor(act_time / 3600)
            act_time = act_time % 3600
            act_minute = math.floor(act_time / 60)
            act_seconds = act_time % 60
            msg = msg + activity[0] + " for " + str(act_hour) + " hours " + str(act_minute) + " minutes " + str(
                act_seconds) + " seconds\n"

        await ctx.send(msg)

    @tasks.loop(hours=24)
    async def clear_playtime(self):
        self.test.clear_activity()
        return

    @tasks.loop(seconds=10)
    async def collect_play_time(self):
        for guild in self.bot.guilds:
            # get all servers that bots are in
            for member in guild.members:
                # get all members in a server
                if not member.bot:
                    if member.activity is not None:
                        currActType = str(member.activity.type)
                        if "ActivityType." in currActType:
                            currActType = currActType.replace("ActivityType.", "")
                        currActname = member.activity.name
                        activity = currActType + " " + currActname
                        if self.test.activity_exist(member.id, activity):
                            # if the activity is recorded in db
                            self.test.update_activity(member.id, activity)
                        else:
                            # if not recorded
                            self.test.add_activity(member.id, activity)

                        # get activity with user id and member activity


    @tasks.loop(seconds=60)
    async def warn_play_time(self):
        for guild in self.bot.guilds:
            for member in guild.members:
                # get all members in a server
                if not member.bot:
                    status = self.test.get_playtime_limit_and_warning(member.id)
                    # return status info like playtime limit and is warned
                    result = self.test.sum_user_activities(member.id)
                    # return sum playtime
                    if status[1] == 0 and status[0] < result:
                        #  they have not been warned about play time
                        #  and have exceeded playtime
                        msg = member.name + "\n"
                        try:
                            msg = msg + "You have exceeded your planned play time, please make sure that you are actively doing work\n"
                            await member.send(msg)
                        except:
                            print("cannot send to this user")
                        self.test.is_warned(member.id)


    @tasks.loop(hours=24)
    async def change_warned_status(self):
        for guild in self.bot.guilds:
            for member in guild.members:
                # get all members in a server
                if not member.bot:
                    self.test.change_warned(member.id)

    @tasks.loop(hours=12)
    async def show_play_time(self):
        for guild in self.bot.guilds:
            for member in guild.members:
                # get all members in a server
                if not member.bot:
                    msg = member.name + "\n"
                    results_list = self.test.get_user_activities(member.id)
                    # list of tuples where [0] is activity and [1] is time
                    if len(results_list) > 0:
                        for activity in results_list:
                            act_time = activity[1]
                            act_hour = math.floor(act_time / 3600)
                            act_time = act_time % 3600
                            act_minute = math.floor(act_time / 60)
                            act_seconds = act_time % 60
                            msg = msg + activity[0] + " for " + str(act_hour) + " hours " + str(
                                act_minute) + " minutes " + str(
                                act_seconds) + " seconds\n"
                        try:
                            await member.send(msg)
                                # we got some activity recorded
                        except:
                            print("cannot send to this user")

def setup(bot):
    bot.add_cog(UserActivity(bot))
