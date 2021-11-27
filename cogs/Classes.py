from discord.ext import commands, tasks
from discord import Embed, message
import discord
import discord as d
from discord import channel
from discord import guild
from discord.ext.commands.core import command
from database_func import database_func
from datetime import datetime
import asyncio
import math


class Classes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.test = database_func.getInstance()


    @commands.Cog.listener()
    async def on_ready(self):
        self.add_members_to_meetings.start()
        self.check_meetings.start()

    @commands.command()
    async def meeting(self, ctx, title, begin_time: str, end_time: str, location, *description):
        try:
            today = datetime.now()
            start_time = datetime.strptime(begin_time, "%Y-%m-%d-%H:%M")
            finish_time = datetime.strptime(end_time, "%Y-%m-%d-%H:%M")
            if today >= start_time:
                await ctx.send("Your meeting time must be after now")
                return
            if today >= finish_time:
                await ctx.send("Your meeting finish time must be after now")
                return
            if finish_time < start_time:
                await ctx.send("Your meeting finish time must be after start time")
                return

        except Exception as e:
            await ctx.send(e)
        else:
            msg = ' '.join(description)
            embed = Embed(title="Meeting" + title,
                          description=msg,
                          colour=ctx.author.colour,
                          timestamp=datetime.utcnow())
            embed.set_author(name=ctx.author)
            embed.add_field(name="Start Time ", value=str(start_time), inline=False)
            embed.add_field(name="End Time ", value=str(finish_time), inline=False)
            embed.add_field(name="Location ", value=location, inline=False)
            message = await ctx.send(embed=embed)
            await message.pin()
            await message.add_reaction('👍')
            await message.add_reaction('👎')
            # today = datetime.now()
            # diff = (valid_time - today).total_seconds()
            # await ctx.send(title +" registration starts now and finishes at "+str(valid_until))
            # await asyncio.sleep(diff)
            self.test.add_meeting(message.id, message.channel.id, title, start_time, finish_time, location, msg,
                                  ctx.author.id)
            # await ctx.send("Registration finishes. "+title+ " will start at " + date)
            # today = datetime.now()
            # diff = (meettime - today).total_seconds()
            # if diff < 900:
            #     await ctx.send(title+ " is coming up within " +str(math.floor(diff/60)) +" minutes")
            #     await asyncio.sleep(diff)
            #     await ctx.send(title + " meeting time has come")
            # else:
            #     reminder_time = diff-900
            #     await asyncio.sleep(reminder_time)
            #     await ctx.send("15 Minutes until "+title)
            #     await asyncio.sleep(900)
            #     await ctx.send(title+ " meeting time has come")

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

    @tasks.loop(seconds=60)
    async def check_meetings(self):
        meetings = self.test.get_meetings()
        # a list of tuples related to meetings
        if meetings is None:
            # no current meetings
            return
        else:
            for meeting in meetings:
                meeting_id = meeting[0]
                channel_id = meeting[1]
                print(channel_id)
                title = meeting[2]
                print(title)
                begin = meeting[3]
                end = meeting[4]
                location = meeting[5]
                description = meeting[6]
                print(description)
                channel = self.bot.get_channel(channel_id)
                title = "Meeting time for " + title + " has arrived"
                embed = Embed(title=title,
                              description=description,
                              timestamp=datetime.utcnow())
                embed.add_field(name="Start Time ", value=str(begin), inline=False)
                embed.add_field(name="End Time ", value=str(end), inline=False)
                embed.add_field(name="Location ", value=location, inline=False)
                await channel.send(embed=embed)

    @tasks.loop(seconds=60)
    async def add_members_to_meetings(self):
        meetings = self.test.get_meetings_within_10minutes()
        if meetings is None:
            print("JERE")
            return
        else:
            print("NE HERE")
            print(meetings)
            for meeting in meetings:
                print("IN FOR")

                meeting_id = meeting[0]
                channel_id = meeting[1]
                title = meeting[2]
                begin = meeting[3]
                end = meeting[4]
                location = meeting[5]
                meeting_txt = await self.bot.get_channel(channel_id).fetch_message(meeting_id)
                channel = self.bot.get_channel(channel_id)
                lst_coming =[]
                lst_not_coming = []
                for reaction in meeting_txt.reactions:
                    if reaction.emoji == '👍':
                        async for user in reaction.users():
                            if not user.bot:
                                lst_coming.append(user.id)
                                self.test.add_participant_to_meetings(user.id, meeting_id)
                    elif reaction.emoji == '👎':
                        async for user in reaction.users():
                            if not user.bot:
                                lst_not_coming.append(user.name)
                embed = Embed(title=title,description="Meeting coming up within 10 minutes")
                embed.add_field(name="Start Time ", value=str(begin), inline=False)
                embed.add_field(name="End Time ", value=str(end), inline=False)
                embed.add_field(name="Location ", value=location, inline=False)
                await channel.send(embed = embed)
                await channel.send("The following member please remember to come")
                for ppl in lst_coming:
                    await channel.send(f"<@{ppl}>")
                await channel.send("The following member will not come")
                for ppl in lst_not_coming:
                    await channel.send(ppl)



    # @commands.command()
    # async def mand_meeting(self, ctx, title, date: str, location, *users:discord.Member):
    # #     this is used for mandaytory meetings
    #     try:
    #         today = datetime.now()
    #         meettime = datetime.strptime(date, "%Y-%m-%d-%H:%M")
    #         if today >= meettime:
    #             await ctx.send("Your meeting time must be after now")
    #             return
    #     except Exception as e:
    #         await ctx.send(e)
    #     else:
    #
    #         embed = Embed(title="Mandatory " +title,
    #                       colour=ctx.author.colour,
    #                       timestamp=datetime.utcnow())
    #         embed.set_author(name=ctx.author)
    #         embed.add_field(name="Date ", value=str(meettime), inline=False)
    #         embed.add_field(name="Location ", value=location, inline=False)
    #         await ctx.send(embed=embed)
    #         await ctx.send("The following people have to come")
    #
    #         for user in users:
    #             await ctx.send(user)
    #
    #
    #         today = datetime.now()
    #         diff = (meettime -today).total_seconds()
    #         if diff < 900:
    #             await ctx.send(title + " is coming up within " + str(math.floor(diff / 60)) + " minutes")
    #             await ctx.send("The following people need to show up")
    #             for user in users:
    #                 await ctx.send(user)
    #             await asyncio.sleep(diff)
    #             await ctx.send(title + " meeting time has come")
    #         else:
    #             reminder_time = diff - 900
    #             await asyncio.sleep(reminder_time)
    #             await ctx.send("15 Minutes until " + title)
    #             await ctx.send("The following people need to show up")
    #             for user in users:
    #                 await ctx.send(user)
    #             await asyncio.sleep(900)
    #             await ctx.send(title + " meeting time has come")

    
    @commands.command(name="addClass")# Create a new class
    @commands.has_permissions(manage_roles=True)
    async def add_class(self, ctx, class_name: str):
        guild = ctx.guild
        if ctx.author.guild_permissions.manage_channels:
            role = await guild.create_role(name=class_name, colour=discord.Colour(0xff0000))
            authour = ctx.message.author
            await authour.add_roles(role)
            newChannel = await guild.create_text_channel(name='{}'.format(class_name), )
            member = guild.default_role
            await newChannel.set_permissions(member, view_channel=False)
            await newChannel.set_permissions(role, view_channel=True, send_messages=True)
            channel_id = newChannel.id
            role_id = role.id
            message = await ctx.send(f'Class `{class_name}` has been created! \nUse !join`{class_name}` to join.')
            user_id = message.author.id
            # await message.add_reaction('👍')
        self.test.add_class(class_name,channel_id,role_id,user_id)
    
    @commands.command(name="join")
    async def join(self,ctx,class_name:str):
        guild = ctx.guild
        role = discord.utils.get(guild.roles,name=class_name)
        authour = ctx.message.author
        await authour.add_roles(role)
    
    @commands.command(name="leave")
    async def leave(self,ctx,class_name:str):
        guild = ctx.guild
        role = discord.utils.get(guild.roles,name=class_name)
        authour = ctx.message.author
        await authour.remove_roles(role)
        
    
    

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
    async def deleteClass(self, ctx, class_name: str):  # Take class_name input as string and then deletes class from table
        self.test.delete_class(class_name)
        mbed = d.Embed(
            tile='Success',
            description="{} has been successfully deleted.".format(class_name)
        )
        if ctx.author.guild_permissions.manage_channels:
            Dchannel = discord.utils.get(ctx.guild.channels,name = class_name)
            print(Dchannel.id)
            if Dchannel is not None:
                await ctx.send(embed=mbed)
                await Dchannel.delete()
            else:
                await ctx.send(f'No class named, "{class_name}", was found')
            
        
        role_object = discord.utils.get(ctx.message.guild.roles, name=class_name)
        await ctx.send("Deleted class: {}".format(class_name))
        await role_object.delete()

    @commands.command(name="getClasses")
    async def getClasses(self, ctx):
        await ctx.send("Current existing classes: {}".format(self.test.print_all_class()))


    #Parameters for add_task: task_id(The discord message id), user_id(the discord author id), channel_id(the discord channel id), task_name(the task name), task_description(the details of the task), difficulty(int 1-10),deadline(the deadline of the task)
    @commands.command()
    async def add_task(self, ctx, task_name, task_description, difficulty, deadline):
        self.test.add_task(ctx.message.id, ctx.message.author.id, ctx.channel.id, task_name, task_description, difficulty, deadline)
        await ctx.send("Task {} has been added".format(task_name))
    

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

    #uses database_func get_tasks_all based on user_id and days both are parameters. Gets all tasks for a user in the last x days 
    @commands.command()
    async def taskall(self, ctx, days):
        await ctx.send(self.test.get_tasks_user_all(ctx.message.author.id, days))
    
    #uses database_func get_tasks_channel_specific based on user_id and days both are parameters. Gets all tasks for a user in the last x days in a specific channel
    @commands.command()
    async def tasks(self, ctx, days):
        await ctx.send(self.test.get_tasks_channel_specific(ctx.channel.id, ctx.message.author.id, days))

def setup(bot):
    bot.add_cog(Classes(bot))
