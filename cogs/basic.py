import discord as d
from discord import channel
import discord
from discord import guild
from discord import client
from discord.ext import commands
from datetime import datetime, timedelta
from discord import Embed
from datetime import datetime, timedelta
import time
import mysql.connector
from mysql.connector import Error
from database_func import database_func
from datetime import datetime
import asyncio

class basic(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.test = database_func()


    @commands.command()
    async def testED (self, ctx):
        await ctx.send("Edward test")

    @commands.command()
    async def ping(self, ctx):

        latency = ctx.bot.latency
        # Latency is returned in milliseconds
        latency = latency * 1000
        # Latency is converted to a string
        latency = str(latency)
        # The latency is sent to the user
        await ctx.send(f'Pong! `{latency}ms`')

    # a polling feature that Edward is working on
    @commands.command()
    async def create_poll(self, ctx, hours: int, question: str, *options):
        if len(options) > 10:
            await ctx.send("You can only supply a maximum of 10 options.")

        else:
            numbers = ("1️⃣", "2⃣", "3⃣", "4⃣", "5⃣",
                       "6⃣", "7⃣", "8⃣", "9⃣", "🔟")
            embed = Embed(title="Poll",
                          description=question,
                          colour=ctx.author.colour,
                          timestamp=datetime.utcnow())

            fields = [("Options", "\n".join([f"{numbers[idx]} {option}" for idx, option in enumerate(options)]), False),
                      ("Instructions", "React to cast a vote!", False)]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            message = await ctx.send(embed=embed)

            for emoji in numbers[:len(options)]:
                await message.add_reaction(emoji)

    @commands.command(name="addClass")  # Create a new class
    @commands.has_permissions(manage_roles=True)
    async def add_class(self, ctx, class_name: str, server_name: str):
        self.test.add_class(class_name, server_name)
        guild = ctx.guild
        if ctx.author.guild_permissions.manage_channels:
            role = await guild.create_role(name = class_name,colour=discord.Colour(0xff0000))
            authour = ctx.message.author
            await authour.add_roles(role)
            newChannel = await guild.create_text_channel(name = '{}'.format(class_name),)
            member = guild.default_role
            await newChannel.set_permissions(member, view_channel = False)
            await newChannel.set_permissions(role, view_channel = True, send_messages=True)
            message = await ctx.send(f'Class `{class_name}` has been created! \nReact below to join.')
            reaction = await message.add_reaction('\N{WHITE HEAVY CHECK MARK}')
            user = set()
            await message.on_reaction_add(reaction, user, role)
                
            
    async def on_reaction_add(reaction, user, role):
        if reaction.emoji == '\N{WHITE HEAVY CHECK MARK}':
            roleS = discord.utils.get(reaction.message.guild.roles, name = role)
            if roleS not in user.roles:
                user.add_roles(roleS)
    @commands.command(name="getUsersInClass")  # Return all users that are in this class
    async def getUsersInClass(self,ctx, class_id):
        await ctx.send("Users in class {}: ".format(self.test.users_in_class(class_id)))

    @commands.command(name="addUser")  # Add a user to a server
    async def addUser(self, ctx, user_name, server_name, timezone):
        self.test.add_user(user_name, server_name, timezone)
        await ctx.send("User {} added to server {} on timezone {}".format(user_name, server_name, timezone))

    @commands.command(name="getUsers")  # Print all existing users
    async def getUsers(self, ctx):
        await ctx.send("Current existing users: {}".format(self.test.print_all_users()))

    @commands.command(name="deleteClass")
    async def deleteClass(self, ctx, class_name, channel: d.TextChannel):  # Take class_name input as string and then deletes class from table
        self.test.delete_class(class_name)
        role_object = discord.utils.get(ctx.message.guild.roles, name=class_name)
        await ctx.send("Deleted class: {}".format(class_name))
        await role_object.delete()
        mbed = d.Embed(
            tile = 'Success',
            description = "{} has been successfully deleted.".format(class_name)
        )
        if ctx.author.guild_permissions.manage_channels:
            await ctx.send(embed=mbed)
            await channel.delete()
            

    @commands.command(name="getClasses")
    async def getClasses(self, ctx):
        await ctx.send("Current existing classes: {}".format(self.test.print_all_class()))

    @commands.command(name="reminder")
    async def reminder(self, ctx, date: str, *message):
        reminder = datetime.strptime(date, "%Y-%m-%d-%H:%M")
        today = datetime.now()
        diff = (reminder - today).total_seconds()
        msg = " ".join(message)
        await ctx.send("a reminder is set up for " + date + " for " + msg)
        await asyncio.sleep(diff)
        await ctx.send("Reminder: " + msg)

    async def complete_poll(self, channel_id, message_id):
        message = await self.bot.get_channel(channel_id).fetch_message(message_id)

        most_voted = max(message.reactions, key=lambda r: r.count)

        await message.channel.send(
            f"The results are in and option {most_voted.emoji} was the most popular with {most_voted.count - 1:,} votes!")




def setup(bot):
    bot.add_cog(basic(bot))
