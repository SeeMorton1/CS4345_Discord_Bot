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

# this file is responsible for basic functionalities like announcements, polls, and reminders
class basic(commands.Cog):
    # this file store basic commands
    def __init__(self, bot):
        self.bot = bot
        self.test = database_func.getInstance()
        #     get database singleton instance

        self.check_reminders.start()

    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot ready")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        # add all users to database on joining a new server
        for member in guild.members:
            if not member.bot:
                self.test.add_user(member.id, member.name)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # add new users to database
        if not member.bot:
            self.test.add_user(member.id, member.name)

    @commands.Cog.listener()
    async def on_member_leave(self,member):
        # delete left users
        self.test.delete_user(member.id)

    @commands.command()
    async def dm(self, ctx, user: discord.Member, *message):
        # dm someone
        msg = " ".join(message)
        embed = discord.Embed(title=msg)
        await user.send(embed=embed)


    @commands.command()
    async def help(self, ctx):
        # display all available commands
        author = ctx.message.author
        embed = Embed(title="Help",
                      colour=ctx.author.colour)

        embed.add_field(name="!ping", value="Pong", inline=False)
        embed.add_field(name="!test", value="Author test", inline=False)
        embed.add_field(name="!announcement title(str) *description(str)", value="Create an announcement", inline=False)
        embed.add_field(name="!create_poll hours question(string) *options(string)", value="Create a poll",
                        inline=False)
        embed.add_field(name="!reminder date(YYYY-MM-DD-HH:MM in 24 hour clock) title *text(str)", value="Make a reminder",
                        inline=False)
        embed.add_field(name="!status @[valid ping]", value="Check other's activity", inline=False)
        embed.add_field(name="!status_self", value="Check your time playing all video games", inline=False)
        embed.add_field(name="!meeting title(str) begintime(YYYY-MM-DD-HH:MM in 24 hour clock) endtime(YYYY-MM-DD-HH:MM in 24 hour clock) location(str) *description", value="Create your meetings ", inline=False)
        embed.add_field(name="!addClass classname(str)", value="Create a channel/class", inline=False)
        embed.add_field(name="!join classname(str)", value="Join a channel/class", inline=False)
        embed.add_field(name="!leave classname(str)", value="Leave a channel/class", inline=False)
        embed.add_field(name="!kick @[valid ping] classname(str)", value="Kick someone from a channel/class", inline=False)
        embed.add_field(name="!deleteClass classname(str)", value="Delete a channel/class",
                        inline=False)
        embed.add_field(name="!add_task taskname(str) description(str) difficulty(int) deadline(YYYY-MM-DD-HH:MM in 24 hour clock) ", value="Create a person task",
                        inline=False)
        embed.add_field(
            name="!assign_tasks task_name(str) task_description(str) difficulty (int) deadline(YYYY-MM-DD-HH:MM in 24 hour clock)",
            value="Assign tasks to everyone within the channel",
            inline=False)
        embed.add_field(name="!delete_task task_name(str)", value="Delete a task", inline=False)
        embed.add_field(name="!taskall day(int)", value="Get all tasks for a user in the server within given days", inline=False)
        embed.add_field(name="!task day(int)", value="Get all tasks for a user in the channel within given days", inline=False)
        embed.add_field(name="!change_playtime hours", value="Change your playtime limit ",
                        inline=False)

        embed.set_footer(text="* value can be multiple values, other can only accept one value")
        await ctx.send(author, embed=embed)

    @commands.command()
    async def test(self, ctx):
        await ctx.send(ctx.message.author.display_name + " test")

    @commands.command()
    async def announcement(self, ctx, title, *description):
        # create an announcement
        msg = ' '.join(description)
        embed = Embed(title=title,
                      description=msg,
                      colour=ctx.author.colour,
                      timestamp=datetime.utcnow())
        embed.set_author(name=ctx.author)

        message = await ctx.send(embed=embed)
        await message.pin()

    @announcement.error
    async def announcement_error(self, ctx: commands.Context, error: commands.CommandError):
        # announcement  error handling
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
        # await ctx.message.delete(delay=5)

    @commands.command()
    async def ping(self, ctx):
        # get latency
        latency = ctx.bot.latency
        # Latency is returned in milliseconds
        latency = latency * 1000
        # Latency is converted to a string
        latency = str(latency)
        # The latency is sent to the user
        await ctx.send(f'Pong! `{latency}ms`')
    #     test latency

    @commands.command()
    async def create_poll(self, ctx, hours: float, question: str, *options):
        # create a poll
        if len(options) > 10:
            await ctx.send("You can only supply a maximum of 10 options.")

        else:
            numbers = ("1️⃣", "2⃣", "3⃣", "4⃣", "5⃣",
                       "6⃣", "7⃣", "8⃣", "9⃣", "🔟")
            # reaction array
            embed = Embed(title="Poll",
                          description=question,
                          colour=ctx.author.colour,
                          timestamp=datetime.utcnow())
            # create a embed
            fields = [("Options", "\n".join([f"{numbers[idx]} {option}" for idx, option in enumerate(options)]), False),
                      ("Instructions", "React to cast a vote!", False)]
            # field prototype
            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)
            # configure and add fields
            poll = await ctx.send(embed=embed)
            # send poll

            for emoji in numbers[:len(options)]:
                await poll.add_reaction(emoji)
            #     add reaction
            await poll.pin()
            # pin polll

            await asyncio.sleep(hours*3600)
            # sleep for a designated time to wait for result

            message = await self.bot.get_channel(poll.channel.id).fetch_message(poll.id)

            most_voted = max(message.reactions, key=lambda r: r.count)
            # get the most voted reaction

            await message.channel.send(
                f"The results are in and option {most_voted.emoji} was the most popular with {most_voted.count - 1:,} votes!\n Poll is removed from pinned messages")

            await poll.unpin()

    #         conclude the result and unpin the poll

    @create_poll.error
    async def poll_error(self, ctx: commands.Context, error: commands.CommandError):
        # error handling for poll error
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
        # await ctx.message.delete(delay=5)

    @commands.command(name="reminder")
    async def reminder(self, ctx,date: str, title, *message):
        # reminder group feature
        try:
            reminder = datetime.strptime(date, "%Y-%m-%d-%H:%M")

        except Exception as e:
            await ctx.send(e)
        else:
            msg = " ".join(message)
            message_sent = await ctx.send("a reminder is set up for " + date + " for " + title)
            # await ctx.send(message_sent.channel.id)
            self.test.add_reminder(message_sent.id,message_sent.channel.id,ctx.author.id, reminder, title,msg)
            # message = await self.bot.get_channel(poll.channel.id).fetch_message(poll.id)




    @reminder.error
    async def reminder_error(self, ctx: commands.Context, error: commands.CommandError):
        # reminder error handling
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
        # await ctx.message.delete(delay=5)

    @tasks.loop(seconds=60)
    async def check_reminders(self):
        results = self.test.get_reminders()
    #     return a list of reminders on current time
        if results is None:
            return
        else:
            for reminder in results:
                channelid = reminder[0]
                title = reminder[1]
                description = reminder[2]
                channel = self.bot.get_channel(channelid)
                embed = Embed(
                    title = title,
                    description = description,
                    timestamp=datetime.utcnow()
                )
                await channel.send(embed = embed)
    
def setup(bot):
    bot.add_cog(basic(bot))
