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

class Classes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.test = database_func.getInstance()

    @commands.command()
    async def meeting(self,ctx, title, date:str, valid_until:str, location, *description):
        try:
            today = datetime.now()
            meettime = datetime.strptime(date, "%Y-%m-%d-%H:%M")
            valid_time = datetime.strptime(valid_until, "%Y-%m-%d-%H:%M")
            if today >= meettime:
                await ctx.send("Your meeting time must be after now")
                return
            if today >= valid_time:
                await ctx.send("Your valid registration time must be after now")
                return

        except Exception as e:
            await ctx.send(e)
        else:
            msg = ' '.join(description)
            embed = Embed(title=title,
                          description=msg,
                          colour=ctx.author.colour,
                          timestamp=datetime.utcnow())
            embed.set_author(name=ctx.author)
            embed.add_field(name="Date ", value= str(meettime), inline=False)
            embed.add_field(name="Location ", value= location, inline=False)
            message = await ctx.send(embed=embed)
            await message.pin()
            await message.add_reaction('👍')
            await message.add_reaction('👎')
            today = datetime.now()
            diff = (valid_time - today).total_seconds()
            await ctx.send(title +" registration starts now and finishes at "+str(valid_until))
            await asyncio.sleep(diff)
            meeting_txt = await self.bot.get_channel(message.channel.id).fetch_message(message.id)
            for reaction in meeting_txt.reactions:
                if reaction.emoji =='👍':
                    async for user in reaction.users():
                        if not user.bot:
                            await ctx.send(user.name +" is coming ")
                elif reaction.emoji =='👎':
                    async for user in reaction.users():
                        if not user.bot:
                            await ctx.send(user.name +" is not coming ")
            await ctx.send("Registration finishes. "+title+ " will start at " + date)
            today = datetime.now()
            diff = (meettime - today).total_seconds()
            if diff < 900:
                await ctx.send(title+ " is coming up within " +str(math.floor(diff/60)) +" minutes")
                await asyncio.sleep(diff)
                await ctx.send(title + " meeting time has come")
            else:
                reminder_time = diff-900
                await asyncio.sleep(reminder_time)
                await ctx.send("15 Minutes until "+title)
                await asyncio.sleep(900)
                await ctx.send(title+ " meeting time has come")

    @meeting.error
    async def meeting_error(self, ctx: commands.Context, error: commands.CommandError):
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

    @commands.command()
    async def mand_meeting(self, ctx, title, date: str, location, *users:discord.Member):
    #     this is used for mandaytory meetings
        try:
            today = datetime.now()
            meettime = datetime.strptime(date, "%Y-%m-%d-%H:%M")
            if today >= meettime:
                await ctx.send("Your meeting time must be after now")
                return
        except Exception as e:
            await ctx.send(e)
        else:

            embed = Embed(title="Mandatory " +title,
                          colour=ctx.author.colour,
                          timestamp=datetime.utcnow())
            embed.set_author(name=ctx.author)
            embed.add_field(name="Date ", value=str(meettime), inline=False)
            embed.add_field(name="Location ", value=location, inline=False)
            await ctx.send(embed=embed)
            await ctx.send("The following people have to come")

            for user in users:
                await ctx.send(user)


            today = datetime.now()
            diff = (meettime -today).total_seconds()
            if diff < 900:
                await ctx.send(title + " is coming up within " + str(math.floor(diff / 60)) + " minutes")
                await ctx.send("The following people need to show up")
                for user in users:
                    await ctx.send(user)
                await asyncio.sleep(diff)
                await ctx.send(title + " meeting time has come")
            else:
                reminder_time = diff - 900
                await asyncio.sleep(reminder_time)
                await ctx.send("15 Minutes until " + title)
                await ctx.send("The following people need to show up")
                for user in users:
                    await ctx.send(user)
                await asyncio.sleep(900)
                await ctx.send(title + " meeting time has come")

    @commands.command(name="addClass")  # Create a new class
    @commands.has_permissions(manage_roles=True)
    async def add_class(self, ctx, class_name: str, server_name: str):
        self.test.add_class(class_name, server_name)
        guild = ctx.guild
        if ctx.author.guild_permissions.manage_channels:
            role = await guild.create_role(name=class_name, colour=discord.Colour(0xff0000))
            authour = ctx.message.author
            await authour.add_roles(role)
            newChannel = await guild.create_text_channel(name='{}'.format(class_name), )
            member = guild.default_role
            await newChannel.set_permissions(member, view_channel=False)
            await newChannel.set_permissions(role, view_channel=True, send_messages=True)
            message = await ctx.send(f'Class `{class_name}` has been created! \nReact below to join.')
            reaction = await message.add_reaction('\N{WHITE HEAVY CHECK MARK}')

    @commands.command(name="getUsersInClass")  # Return all users that are in this class
    async def getUsersInClass(self, ctx, class_id):
        await ctx.send("Users in class {}: ".format(self.test.users_in_class(class_id)))

    @commands.command(name="addUser")  # Add a user to a server
    async def addUser(self, ctx, user_name, server_name, timezone):
        self.test.add_user(user_name, server_name, timezone)
        await ctx.send("User {} added to server {} on timezone {}".format(user_name, server_name, timezone))

    @commands.command(name="getUsers")  # Print all existing users
    async def getUsers(self, ctx):
        await ctx.send("Current existing users: {}".format(self.test.print_all_users()))

    @commands.command(name="deleteClass")
    async def deleteClass(self, ctx, class_name,
                          channel: d.TextChannel):  # Take class_name input as string and then deletes class from table
        self.test.delete_class(class_name)
        role_object = discord.utils.get(ctx.message.guild.roles, name=class_name)
        await ctx.send("Deleted class: {}".format(class_name))
        await role_object.delete()
        mbed = d.Embed(
            tile='Success',
            description="{} has been successfully deleted.".format(class_name)
        )
        if ctx.author.guild_permissions.manage_channels:
            await ctx.send(embed=mbed)
            await channel.delete()

    @commands.command(name="getClasses")
    async def getClasses(self, ctx):
        await ctx.send("Current existing classes: {}".format(self.test.print_all_class()))

    @commands.command()
    async def add_task(self, ctx, title, difficulty, deadline, class_name):
        format_deadline = '%Y-%m-%d-%H:%M'
        try:
            user_id = ctx.message.author.id
            user_id = int(user_id / 100000000)
            title = title
            difficulty = int(difficulty)
            deadline = datetime.strptime(deadline, format_deadline)


        except Exception as e:
            await ctx.send(e)
        else:
            self.test.add_task(user_id, title, difficulty, deadline, class_name)
            await ctx.send("Task added")

    @add_task.error
    async def add_task_error(self, ctx: commands.context, error: commands.CommandError):
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

    @commands.command(name="deleteClass")
    async def deleteClass(self, ctx, class_name,
                          channel: d.TextChannel):  # Take class_name input as string and then deletes class from table
        self.test.delete_class(class_name)
        role_object = discord.utils.get(ctx.message.guild.roles, name=class_name)
        await ctx.send("Deleted class: {}".format(class_name))
        await role_object.delete()
        mbed = d.Embed(
            tile='Success',
            description="{} has been successfully deleted.".format(class_name)
        )
        if ctx.author.guild_permissions.manage_channels:
            await ctx.send(embed=mbed)
            await channel.delete()

    @commands.command()
    async def delete_task(self, ctx, task_name):
        self.test.delete_task(task_name)
        await ctx.send("Task deleted")

    @tasks.loop(minutes=1)
    async def remove_expired_tasks(self):
        self.test.remove_expired_tasks()

    @delete_task.error
    async def delete_task_error(self, ctx: commands.context, error: commands.CommandError):
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
    async def taskm(self, ctx):
        user_id = int(ctx.message.author.id / 100000000)
        x = self.test.get_tasks_month(user_id)
        tasks_as_user = [a for a in x if a[1] == user_id]
        await ctx.send("There are {} tasks due in the next month".format(len(tasks_as_user)))
        for i in x:
            if i[1] == user_id:
                s = "{} is due on {} with difficulty {} and for class {}".format(i[2], i[4], i[3], i[5])
                await ctx.send(s)
        # await ctx.send("List of tasks due the next thirty days: {}".format(self.test.get_tasks_month(int(ctx.message.author.id)/100000000)))

    @commands.command()
    async def taskw(self, ctx):
        user_id = int(ctx.message.author.id / 100000000)
        x = self.test.get_tasks_week(user_id)
        tasks_as_user = [a for a in x if a[1] == user_id]
        await ctx.send("There are {} tasks due in the next week".format(len(tasks_as_user)))
        for i in x:
            if i[1] == user_id:
                s = "{} is due on {} with difficulty {} and for class {}".format(i[2], i[4], i[3], i[5])
                await ctx.send(s)
        # await ctx.send("List of tasks due the next thirty days: {}".format(self.test.get_tasks_month(int(ctx.message.author.id)/100000000)))



def setup(bot):
    bot.add_cog(Classes(bot))