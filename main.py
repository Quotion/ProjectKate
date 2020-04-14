# https://github.com/Quotion/ProjectKate

from functions.database import PgSQLConnection
from discord.ext.commands import Bot
from language.treatment_ru import *
from modueles.status import Status
from modueles.addchannels import AddChannels
from modueles.main_commands import MainCommands
from modueles.ban_system import Ban
from modueles.invests import Invests
from modueles.rprequest import RPrequest
from modueles.fun_gif import Fun_Gif
import discord
import logging
import json
import os
import io
import functions.embeds

client = Bot(command_prefix=['к!', 'К!', 'k!', 'K!'])

logging.basicConfig(format="%(levelname)s: %(funcName)s (%(lineno)d): %(name)s: %(message)s",
                    level=logging.INFO)
logger = logging.getLogger("main")
logger.setLevel(logging.INFO)


class Katherine(discord.Client):
    def __init__(self, user):
        self.client = user

        self.pgsql = PgSQLConnection()

        self.on_ready()
        self.events()

        self.client.add_cog(AddChannels(client))
        self.client.add_cog(MainCommands(client))
        self.client.add_cog(Status(client))
        self.client.add_cog(Ban(client))
        # self.client.add_cog(Invests(client))
        self.client.add_cog(RPrequest(client))
        self.client.add_cog(Fun_Gif(client))

    def on_ready(self):

        @self.client.event
        async def on_connect():
            logger.info('Bot {} ready on 50%.'.format(self.client.user.name))

        @self.client.event
        async def on_ready():
            logger.info('Bot {} now loaded for 100%.'.format(self.client.user.name))
            await self.client.change_presence(activity=discord.Game(name="{}help".format(self.client.command_prefix[0])))

    def events(self):
        @self.client.event
        async def on_guild_join(guild):
            conn, user = self.pgsql.connect()
            user.execute("SELECT info FROM info WHERE guild_id = %s", [guild.id])
            info = user.fetchone()
            if not info or info == "null":
                information = {'main': 0, 'news': 0, 'logging': 0}
                bank = {'name': f'"{guild.name}" банк', 'char_of_currency': 'ВС'}
                user.execute("INSERT INTO info (bank_info, guild_id, info, promocode) VALUES (%s, %s, %s, %s)",
                            (json.dumps(bank), guild.id, json.dumps(information), json.dumps({"amount":0, "code":0})))
                conn.commit()

            logger.info('Someone added {} to guild "{}"'.format(self.client.user.name, guild.name))

            self.pgsql.close_conn(conn, user)
            channel = guild.system_channel
            await channel.send(embed=await functions.embeds.description(guild.name, thanks))
            await channel.send(embed=await functions.embeds.description(self.client.command_prefix[0], channels))

        @self.client.event
        async def on_member_join(member):
            guild_id = member.guild.id
            conn, user = self.pgsql.connect()

            user.execute("SELECT info FROM info WHERE guild_id = {}".format(guild_id))
            info = user.fetchone()[0]

            user.execute("SELECT roles FROM users WHERE \"discordID\" = %s", [member.id])
            roles = None
            try:
                roles = user.fetchone()[0]
            except Exception:
                pass

            if info['logging']:
                channel = self.client.get_channel(info['logging'])

                await channel.send(embed=await functions.embeds.member_join(member))

            self.pgsql.close_conn(conn, user)

            try:
                roles[str(member.guild.id)]
            except KeyError:
                if not roles:
                    roles = {}
                roles[str(member.guild.id)] = {}
                return

            list_roles = list()

            for role in roles[str(member.guild.id)]:
                list_roles.append(member.guild.get_role(role))

            await member.edit(roles=list_roles)

        @self.client.event
        async def on_member_remove(member):
            if member.id == self.client.user.id:
                return

            conn, user = self.pgsql.connect()

            roles = None

            guild_id = member.guild.id

            try:
                user.execute("SELECT roles FROM users WHERE \"discordID\" = %s", [member.id])
                roles = user.fetchone()[0]
                roles[str(member.guild.id)]
            except KeyError:
                if not roles:
                    roles = {}
                roles[str(member.guild.id)] = {}

            roles[str(member.guild.id)] = [role.id for role in member.roles]

            user.execute("UPDATE users SET roles = %s WHERE \"discordID\" = %s", (json.dumps(roles), member.id))
            conn.commit()

            user.execute("SELECT info FROM info WHERE guild_id = {}".format(guild_id))
            info = user.fetchone()[0]

            if info['logging'] != 0:
                channel = self.client.get_channel(info['logging'])

                await channel.send(embed=await functions.embeds.member_exit(member))

                logger.info("Member remove from guild ({})".format(member.guild.name))

            self.pgsql.close_conn(conn, user)

        @self.client.event
        async def on_message_edit(msg_before, msg_after):
            if msg_after.content == msg_before.content or msg_before.author.id == self.client.user.id:
                return

            conn, user = self.pgsql.connect()

            guild_id = msg_before.guild.id

            user.execute("SELECT info FROM info WHERE guild_id = {}".format(guild_id))
            info = user.fetchone()[0]

            if info['logging'] != 0:
                channel = self.client.get_channel(info['logging'])
                embed = await functions.embeds.message_edit(msg_before, msg_after)
                msg_changes, plot = None, None

                try:
                    plot = io.open("changelog.txt", "rb")
                    msg_changes = discord.File(plot, filename="Message_changes.txt")
                    if msg_changes:
                        await channel.send(embed=embed, file=msg_changes)
                    else:
                        await channel.send(embed=embed)
                    os.remove("changelog.txt")
                    msg_changes.close()
                    plot.close()
                except Exception as error:
                    logging.error(error)

            self.pgsql.close_conn(conn, user)

        @self.client.event
        async def on_message_delete(message):
            conn, user = self.pgsql.connect()

            guild_id = message.guild.id

            user.execute("SELECT info FROM info WHERE guild_id = {}".format(guild_id))
            info = user.fetchone()[0]

            if info['logging'] != 0:
                if message.content:
                    channel = self.client.get_channel(info['logging'])
                    await channel.send(embed=await functions.embeds.delete_message(message))

            self.pgsql.close_conn(conn, user)

        @self.client.event
        async def on_raw_message_delete(payload):
            user_info = None
            if payload.cached_message:
                logger.info("Message was delete in cache.")
                return

            conn, user = self.pgsql.connect()
            guild_id = payload.guild_id
            user.execute("SELECT info FROM info WHERE guild_id = {}".format(guild_id))
            info = user.fetchone()[0]

            guild = self.client.get_guild(guild_id)
            try:
                audit_logs = await guild.audit_logs(limit=1).flatten()
                user_info = [info.user for info in audit_logs]
            except AttributeError as error:
                logger.error(error)

            if info['logging'] != 0:
                channel_log = self.client.get_channel(info['logging'])
                channel = self.client.get_channel(payload.channel_id)

                await channel_log.send(embed=await functions.embeds.raw_delete_message(user_info, channel,
                                                                                       payload.message_id))
                logger.info("Message was raw delete.")

            self.pgsql.close_conn(conn, user)

        # @self.client.event
        # async def on_raw_message_edit(payload):
        #     channel = self.client.get_channel(int(payload.data['channel_id']))
        #     message = await channel.fetch_message(payload.message_id)
        #
        #     conn, user = self.pgsql.connect()
        #     guild_id = message.guild.id
        #     user.execute("SELECT info FROM info WHERE guild_id = {}".format(guild_id))
        #     info = user.fetchone()[0]
        #
        #     if 'status' in info.keys():
        #         if channel.id == info['status']['channel']:
        #             return
        #
        #     if payload.cached_message:
        #         logger.info("Message not exist.")
        #         return
        #
        #     if info['logging']:
        #         channel_log = self.client.get_channel(info['logging'])
        #         await channel_log.send(embed=await functions.embeds.raw_edit_message(message))
        #         logger.info("Message was raw edit.")
        #
        #     self.pgsql.close_conn(conn, user)

        @self.client.event
        async def on_message(message):
            try:
                conn, user = self.pgsql.connect()

                for role in message.author.roles:
                    user.execute("SELECT * FROM botban WHERE id = %s", [role.id])
                    member = user.fetchall()
                    if member:
                        logger.info("User {} in banbot".format(message.author.name))
                        self.pgsql.close_conn(conn, user)
                        return

            except Exception as error:
                logger.error(error)
            finally:
                self.pgsql.close_conn(conn, user)

            if message.author.id == self.client.user.id:
                return
            elif ("коллекция" in message.content or "коллекцию" in message.content) and message.guild.id == 580768441279971338:
                await message.channel.send("https://steamcommunity.com/sharedfiles/filedetails/?id=1735486737")
            elif ("коллекция" in message.content or "коллекцию" in message.content) and message.guild.id == 683031919822110778:
                await message.channel.send("https://steamcommunity.com/sharedfiles/filedetails/?id=1726227848")
            else:
                await self.client.process_commands(message)


Katherine(client)


with open("TOKEN", "r", encoding="utf8") as file:
    client.run(file.read().splitlines()[0])
