# https://github.com/Quotion/ProjectKate

from functions.database import PgSQLConnection
from discord.ext.commands import Bot
from modueles.status import Status
from modueles.main_commands import MainCommands
from modueles.ban_system import Ban
from modueles.invests import Invests
from modueles.rprequest import RPrequest
from modueles.orders import Orders
import functions.embeds
import datetime
import discord
import logging
import json
import os
import io

client = Bot(command_prefix=['к!', 'К!', 'k!', 'K!'])

logging.basicConfig(format="%(levelname)s: %(funcName)s (%(lineno)d): %(name)s: %(message)s",
                    level=logging.INFO)
logger = logging.getLogger("main")
logger.setLevel(logging.INFO)


class Katherine(discord.Client):
    def __init__(self, client):
        self.client = client

        self.pgsql = PgSQLConnection()

        self.on_ready()
        self.events()

        # self.client.add_cog(AddChannels(client))
        self.client.add_cog(MainCommands(client))
        self.client.add_cog(Status(client))
        self.client.add_cog(Ban(client))
        # self.client.add_cog(Invests(client))
        self.client.add_cog(RPrequest(client))
        self.client.add_cog(Orders(client))

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
            logger.info('Someone added {} to guild "{}"'.format(self.client.user.name, guild.name))

        @self.client.event
        async def on_member_join(member):
            conn, user = self.pgsql.connect()
            roles = None
            roles_higher = list()

            try:
                user.execute("SELECT * FROM users WHERE \"discordID\" = %s", [member.id])
                var = user.fetchone()[0]
            except TypeError:
                now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))

                user.execute(
                    'INSERT INTO users VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                    (member.id, 0, 0, 0, 1, now.day - 1, None, json.dumps({str(member.guild.id): {}})))
                conn.commit()

            user.execute("SELECT roles FROM users WHERE \"discordID\" = %s", [member.id])

            try:
                roles = user.fetchone()[0]
            except TypeError:
                pass

            try:
                roles[str(member.guild.id)]
            except Exception:
                if not roles:
                    roles = {}
                roles[str(member.guild.id)] = {}
                return

            for id_role in roles[str(member.guild.id)]:
                role = member.guild.get_role(id_role)

                if role.name == "@everyone":
                    continue

                try:
                    await member.add_roles(role)
                except discord.Forbidden:
                    roles_higher.append(role)

            self.pgsql.close_conn(conn, user)

            channel = discord.utils.get(self.client.get_all_channels(), name='око')
            if not channel:
                pass
            else:
                await channel.send(embed=await functions.embeds.member_join(member))

                if len(roles_higher) == 0:
                    return

                embed = discord.Embed(colour=discord.Colour.red())
                if len(roles_higher) == 1:
                    embed.set_author(name="Недостаточно прав. Выдаваемая роль стоит выше, чем роль бота.")
                    embed.description = "Роль `{}` не может быть выдана `{}` " \
                                        "из-за недостатка прав.".format(roles_higher[0].name, member.name)
                else:
                    embed.set_author(name="Недостаточно прав. Выдаваемые роли стоят выше, чем роль бота.")
                    embed.description = "Роли `{}` не могут быть выданы `{}` " \
                                        "из-за недостатка прав.".format(', '.join(role.name for role in roles_higher),
                                                                        member.name)

                await channel.send(embed=embed)

        @self.client.event
        async def on_member_remove(member):
            if member.id == self.client.user.id:
                return

            conn, user = self.pgsql.connect()
            roles = None

            try:
                user.execute("SELECT roles FROM users WHERE \"discordID\" = %s", [member.id])
                roles = user.fetchone()[0]
                var = roles[str(member.guild.id)]
            except Exception:
                if not roles:
                    roles = {}
                roles[str(member.guild.id)] = {}

            roles[str(member.guild.id)] = [role.id for role in member.roles]

            user.execute("UPDATE users SET roles = %s WHERE \"discordID\" = %s", (json.dumps(roles), member.id))
            conn.commit()

            channel = discord.utils.get(self.client.get_all_channels(), name='око')
            if not channel:
                pass
            else:
                await channel.send(embed=await functions.embeds.member_exit(member))
                logger.info("Member remove from guild ({})".format(member.guild.name))

            self.pgsql.close_conn(conn, user)

        @self.client.event
        async def on_message_edit(msg_before, msg_after):
            if msg_after.content == msg_before.content or msg_before.author.id == self.client.user.id:
                return

            conn, user = self.pgsql.connect()

            channel = discord.utils.get(self.client.get_all_channels(), name='око')
            if not channel:
                pass
            else:
                embed = await functions.embeds.message_edit(msg_before, msg_after)

                try:
                    plot = io.open("changelog.txt", "rb")
                except FileNotFoundError:
                    await channel.send(embed=embed)
                except Exception as error:
                    logging.error(error)
                else:
                    msg_changes = discord.File(plot, filename="Message_changes.txt")
                    await channel.send(embed=embed, file=msg_changes)
                    plot.close()
                    os.remove("changelog.txt")
                    msg_changes.close()

            self.pgsql.close_conn(conn, user)

        @self.client.event
        async def on_message_delete(message):
            if message.author.id == self.client.user.id:
                return

            conn, user = self.pgsql.connect()

            guild_id, check, msg_delete = message.guild.id, None, None

            channel = discord.utils.get(self.client.get_all_channels(), name='око')
            if not channel:
                pass
            else:
                if message.content:
                    if len(message.content) > 50:
                        content = message.content[0:40] + "..."
                        check = True

                    if check:
                        try:
                            with io.open("changelogdeleted.txt", "w", encoding='utf8') as file:
                                file.write("Удаленное сообщение:\n" + message.content)

                            file = io.open("changelogdeleted.txt", "rb")
                            msg_delete = discord.File(file, filename="Message_deleted.txt")

                            await channel.send(embed=await functions.embeds.delete_message(message, content),
                                               file=msg_delete)

                            file.close()
                            msg_delete.close()
                            os.remove("changelogdeleted.txt")
                        except Exception as error:
                            logging.error(error)
                    else:
                        await channel.send(embed=await functions.embeds.delete_message(message, message.content))

            self.pgsql.close_conn(conn, user)

        @self.client.event
        async def on_raw_message_delete(payload):
            user_info = None
            if payload.cached_message:
                logger.info("Message was delete in cache.")
                return

            conn, user = self.pgsql.connect()
            guild_id = payload.guild_id

            guild = self.client.get_guild(guild_id)
            try:
                audit_logs = await guild.audit_logs(limit=1).flatten()
                user_info = [info.user for info in audit_logs]
            except AttributeError as error:
                logger.error(error)

            channel_log = discord.utils.get(self.client.get_all_channels(), name='око')
            if not channel_log:
                pass
            else:
                channel = self.client.get_channel(payload.channel_id)
                await channel_log.send(embed=await functions.embeds.raw_delete_message(user_info, channel,
                                                                                       payload.message_id))
                logger.info("Message was raw delete.")

            self.pgsql.close_conn(conn, user)

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
            else:
                await self.client.process_commands(message)


Katherine(client)

with open("TOKEN", "r", encoding="utf8") as file:
    client.run(file.read().splitlines()[0])
