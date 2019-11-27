from functions.database import PgSQLConnection
from discord.ext.commands import Bot
from discord.ext import commands
from language.treatment_ru import *
from modueles.status import Status
from modueles.addchannels import AddChannels
from modueles.main_commands import MainCommands
from modueles.ban_system import Ban
import discord
import logging
import json
import os
import io
import functions.embeds

client = Bot(command_prefix='к!')

logger = logging.basicConfig(format="%(levelname)s: %(funcName)s (%(lineno)d): %(name)s:%(message)s", level=logging.INFO)
logger = logging.getLogger("main")
logger.setLevel(logging.INFO)


class Katherine(discord.Client):

    def __init__(self, client):
        self.client = client

        self.pgsql = PgSQLConnection()

        self.on_ready()
        self.events()

        self.client.add_cog(AddChannels(client))
        self.client.add_cog(MainCommands(client))
        self.client.add_cog(Status(client))
        self.client.add_cog(Ban(client))

    def on_ready(self):

        @self.client.event
        async def on_connect():
            logger.info('Bot {} ready on 50%.'.format(self.client.user.name))

        @self.client.event
        async def on_ready():
            logger.info('Bot {} now loaded for 100%.'.format(self.client.user.name))

    def events(self):
        @self.client.event
        async def on_guild_join(guild):
            conn, user = self.pgsql.connect()
            user.execute("SELECT info FROM info WHERE guild_id = %s", [guild.id])
            info = user.fetchone()
            if not info:
                information = {'main': 0, 'news': 0, 'logging': 0}
                user.execute("INSERT INTO info VALUES (%s, %s)", (guild.id, json.dumps(information),))
                conn.commit()

            logger.info('Someone added {} to guild "{}"'.format(self.client.user.name, guild.name))

            self.pgsql.close_conn(conn, user)
            channel = guild.system_channel
            await channel.send(embed=await functions.embeds.description(guild.name, thanks))
            await channel.send(embed=await functions.embeds.description(self.client.command_prefix, channels))

        @self.client.event
        async def on_guild_remove(guild):
            conn, user = self.pgsql.connect()
            try:
                user.execute("DELETE FROM info WHERE guild_id = {}".format(guild.id))
                conn.commit()
            except Exception as error:
                logger.error('Impossible to delete {}. This ID not in database.'.format(guild.id))
                logger.error(error)
            finally:
                logger.info('Bot removed from guild ({}) and info about this guild was delete'.format(guild.name))

            self.pgsql.close_conn(conn, user)

        @self.client.event
        async def on_member_join(member):
            guild_id = member.guild.id
            conn, user = self.pgsql.connect()

            user.execute("SELECT info FROM info WHERE guild_id = {}".format(guild_id))
            info = user.fetchone()[0]
            print(info)

            if info['logging']:
                channel = self.client.get_channel(info['logging'])

                await channel.send(embed=await functions.embeds.member_join(member))

            self.pgsql.close_conn(conn, user)

        @self.client.event
        async def on_member_remove(member):
            conn, user = self.pgsql.connect()

            guild_id = member.guild.id

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
                msg_changes = None
                embed = await functions.embeds.message_edit(msg_before, msg_after)

                try:
                    file = io.open("changelog.txt", "rb")
                    msg_changes = discord.File(file, filename="Message_changes.txt")
                    file.close()
                except Exception as error:
                    logging.error(error)

                if msg_changes:
                    await channel.send(embed=embed, file=msg_changes)
                    file.close()
                    try:
                        os.remove("changelog.txt")
                    except Exception as error:
                        logger.error(error)
                else:
                    await channel.send(embed=embed)

            self.pgsql.close_conn(conn, user)

        @self.client.event
        async def on_message_delete(message):
            conn, user = self.pgsql.connect()

            guild_id = message.guild.id

            user.execute("SELECT info FROM info WHERE guild_id = {}".format(guild_id))
            info = user.fetchone()[0]

            if info['logging'] != 0:
                channel = self.client.get_channel(info['logging'])

                await channel.send(embed=await functions.embeds.delete_message(message))
                logger.info("Message was delete.")

            self.pgsql.close_conn(conn, user)

        @self.client.event
        async def on_raw_message_delete(payload):
            if payload.cached_message:
                logger.info("Message was delete in cache.")
                return

            conn, user = self.pgsql.connect()
            guild_id = payload.guild_id
            user.execute("SELECT info FROM info WHERE guild_id = {}".format(guild_id))
            info = user.fetchone()[0]

            if info['logging'] != 0:
                channel_log = self.client.get_channel(info['logging'])
                channel = self.client.get_channel(payload.channel_id)

                await channel_log.send(embed=await functions.embeds.raw_delete_message(payload, channel))
                logger.info("Message was raw delete.")

            self.pgsql.close_conn(conn, user)

        @self.client.event
        async def on_raw_message_edit(payload):
            channel = self.client.get_channel(int(payload.data['channel_id']))
            message = await channel.fetch_message(payload.message_id)

            conn, user = self.pgsql.connect()
            guild_id = message.guild.id
            user.execute("SELECT info FROM info WHERE guild_id = {}".format(guild_id))
            info = user.fetchone()[0]

            if 'status' in info.keys():
                if channel.id == info['status']['channel']:
                    return

            if message.content == "" or payload.cached_message:
                logger.info("Message not exist.")
                return

            if info['logging']:
                channel_log = self.client.get_channel(info['logging'])
                await channel_log.send(embed=await functions.embeds.raw_edit_message(message))
                logger.info("Message was raw edit.")

            self.pgsql.close_conn(conn, user)

        @self.client.event
        async def on_message(message):
            if message.author.id == self.client.user.id:
                return

            await self.client.process_commands(message)


main = Katherine(client)

TOKEN = ""
with open("TOKEN", "r", encoding="utf8") as file:
    TOKEN = file.read().splitlines()[0]

client.run(TOKEN)
