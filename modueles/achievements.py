import json
import discord
import functions
import datetime
import logging
from functions.database import MySQLConnection, PgSQLConnection
import valve.source.a2s
from discord.ext import commands, tasks
from language.treatment_ru import *

class Achievements(commands.Cog, name="Достижения"):

    def __init__(self, client):
        self.client = client

        logger = logging.getLogger("achievements")
        logger.setLevel(logging.INFO)
        self.logger = logger
        self.guild_id = 626848568938070036

        self.mysql = MySQLConnection()
        self.pgsql = PgSQLConnection()

        self.achievements.start()

    @tasks.loop(seconds=60.0)
    async def achievements(self):
        data_of_servers = None

        try:
            conn, user = self.pgsql.connect()

            user.execute("SELECT info FROM info")
            data_of_servers = user.fetchall()
        except Exception:
            self.logger.exception("Failed")
        finally:
            self.pgsql.close_conn(conn, user)


        for buff_server in data_of_servers:
            info_server = dict(buff_server[0])
            if "status" not in info_server.keys():
                pass
            else:
                for key in info_server['status'].keys():
                    if key != "channel":
                        players, channel, steamid, gamer_achievements = None, None, None, None

                        buff = key.split(":")
                        server_address = (buff[0], int(buff[1]))
                        try:
                            players = valve.source.a2s.ServerQuerier(server_address).players()
                        except Exception as error:
                            self.logger.debug(error)
                        else:

                            guild = self.client.get_guild(self.guild_id)
                            database, gamer = self.mysql.connect()
                            conn, user = self.pgsql.connect()

                            for player in players["players"]:
                                time = str(int(datetime.datetime.fromtimestamp(player["duration"]).strftime("%H"))) + \
                                       datetime.datetime.fromtimestamp(player["duration"]).strftime(":%M:%S")
                                member = None

                                try:
                                    gamer.execute('SELECT steamid FROM users_steam WHERE nick = %s', [player["name"].encode('utf8').decode('latin1')])
                                    steamid = gamer.fetchone()[0]
                                except Exception:
                                    pass

                                if steamid:
                                    gamer.execute("SELECT * FROM achievements WHERE steamid = %s", [steamid])
                                    gamer_achievements = gamer.fetchall()[0]

                                try:
                                    user.execute("SELECT \"discordID\" FROM users WHERE steamid = %s", [steamid])
                                    checked_ply = user.fetchone()[0]
                                    member = await guild.fetch_member(int(checked_ply))
                                except TypeError:
                                    pass
                                except IndexError:
                                    pass
                                except discord.errors.NotFound:
                                    member = None
                                except Exception as error:
                                    self.logger.error(error)

                                if gamer_achievements and member:
                                    if not 1 in gamer_achievements:
                                         return
                                    columns_names = [description[0] for description in gamer.description]
                                    for achievement, column_name in zip(gamer_achievements, columns_names):
                                        if achievement == 1 and column_name != "steamid":
                                            try:
                                                embed, reward = await functions.embeds.achievement(member, column_name, guild)
                                                gamer.execute("UPDATE achievements SET {} = 2 WHERE steamid = '{}'".format(column_name, steamid))
                                                database.commit()

                                                user.execute("UPDATE users SET rating = rating + {} WHERE \"discordID\" = {}".format(reward, checked_ply))
                                                conn.commit()

                                                await guild.system_channel.send(embed = embed)
                                            except Exception as error:
                                                print(error)

    @achievements.before_loop
    async def ready(self):
        await self.client.wait_until_ready()
