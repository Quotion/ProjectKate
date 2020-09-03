import json
from pprint import pprint
import requests
import discord
import functions
import datetime
import logging
from functions.database import MySQLConnection, PgSQLConnection
import steam.game_servers
from discord.ext import commands, tasks


class LoadDataStatusFailed(commands.CheckFailure):
    pass


class Status(commands.Cog, name="Статус серверов"):

    def __init__(self, client):
        self.client = client

        logger = logging.getLogger("status")
        logger.setLevel(logging.INFO)
        self.logger = logger

        self.mysql = MySQLConnection()
        self.pgsql = PgSQLConnection()

        self.update.start()

    @staticmethod
    def __get_info(server_address):
        try:
            data = steam.game_servers.a2s_info(server_address, timeout=5)
            players = steam.game_servers.a2s_players(server_address, timeout=5)
            ping = data['_ping']
            name = data['name']
            map_server = data['map']
            player_count = data['players']
            max_players = data['max_players']
        except Exception:
            return 0, 0, 0, 0, 0, 0, False
        else:
            return ping, name, player_count, players, max_players, map_server, True

    async def __get_all_servers_ip(self, status):
        servers_info = list()

        channel = discord.utils.get(self.client.get_all_channels(), name='статус-серверов')
        if not channel:
            return None

        for value in status:
            try:
                message = await channel.fetch_message(value[1])
            except discord.NotFound:
                message = channel.id
            except discord.HTTPException:
                message = await channel.fetch_message(value[1])

            collection = f"https://steamcommunity.com/sharedfiles/filedetails/?id={value[2]}"

            ip = value[0].split(":")

            servers_info.append((ip[0], int(ip[1]), collection, message))

        return servers_info

    @tasks.loop(seconds=60.0)
    async def update(self):
        try:
            conn, user = self.pgsql.connect()

            user.execute("SELECT * FROM status")
            data_of_servers = user.fetchall()
        except Exception:
            raise LoadDataStatusFailed("Данные не могут быть прогруженны с сервера.")
        finally:
            self.pgsql.close_conn(conn, user)

        try:
            conn, user = self.pgsql.connect()
            database, gamer = self.mysql.connect()

            servers_info = await self.__get_all_servers_ip(data_of_servers)

            if not servers_info:
                return

            for server_info in servers_info:

                server_address = ((server_info[0]), server_info[1])
                collection = server_info[2]
                message = server_info[3]

                if not isinstance(message, discord.Message):
                    user.execute("DELETE FROM status WHERE ip = %s", [f"{server_info[0]}:{servers_info[1]}"])
                    conn.commit()
                    continue

                ping, name, player_count, players, max_players, map_server, check_status = \
                    self.__get_info(server_address)

                if check_status:
                    i = 0
                    ply = ['*Загружается на сервер.*'] * player_count
                    for player in players:
                        time = str(int(datetime.datetime.fromtimestamp(player["duration"]).strftime("%H"))) + \
                               datetime.datetime.fromtimestamp(player["duration"]).strftime(":%M:%S")
                        steamid = ''
                        checked_ply = None
                        try:
                            gamer.execute('SELECT steamid FROM users_steam WHERE nick = %s', [player["name"]])
                            gamer_data = gamer.fetchone()[0]
                            if gamer_data:
                                steamid = gamer_data
                        except IndexError:
                            pass
                        except TypeError:
                            pass
                        except Exception as error:
                            self.logger.error(error)

                        try:
                            user.execute('SELECT "discordID" FROM users WHERE steamid = \'' + steamid + '\'')
                            checked_ply = user.fetchone()[0]
                            member = await message.guild.fetch_member(int(checked_ply))
                        except TypeError:
                            pass
                        except IndexError:
                            pass
                        except discord.errors.NotFound:
                            checked_ply = None
                        except Exception as error:
                            self.logger.error(error)

                        if player["name"] != '' and steamid != '' and checked_ply:
                            ply[i] = str(i + 1) + '. ' + member.mention + ' `' + str(steamid) + '` [' + str(time) + ']'
                            i += 1
                        elif player["name"] != '' and steamid != '':
                            ply[i] = str(i + 1) + '. **' + player["name"] + '** `' + str(steamid) + '` [' + str(time) + ']'
                            i += 1
                        elif player["name"] != '' and not steamid != '':
                            ply[i] = str(i + 1) + '. **' + player["name"] + '** `ДАННЫЕ ОТСУТСТВУЮТ`'
                            i += 1
                    title = discord.Embed(colour=discord.Colour.from_rgb(54, 57, 63),
                                          url=collection,
                                          title=f'Коллекция сервера')
                    title.set_author(name=name,
                                     icon_url=message.guild.icon_url)
                    title.add_field(name='Статус:',
                                    value=f'__Онлайн__')
                    title.add_field(name='Пинг:',
                                    value=f"{int(ping)}ms")
                    if player_count != 0:
                        title.add_field(name=f'Всего: ',
                                        value=f'{player_count}/{max_players} игроков')
                        title.add_field(name='Игроки: ',
                                        value='\n'.join([player for player in ply]),
                                        inline=False)
                    else:
                        title.add_field(name=f'Всего: ',
                                        value=f'¯\_(ツ)_/¯')
                    title.add_field(name='Карта:',
                                    value=f'{map_server}',
                                    inline=False)
                    title.add_field(name='IP-ссылка на сервер:',
                                    value=f'steam://connect/{server_address[0]}:{server_address[1]}',
                                    inline=False)
                    title.set_thumbnail(
                        url='https://poolwiki.peoplefone.com/images/6/66/Green_Tick.png')
                    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
                    title.set_footer(text=f'Последнее обновление данных: {str(now.strftime("%d.%m.%y %H:%M:%S "))}')
                    await message.edit(content=None, embed=title)
                else:
                    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
                    await message.edit(content=f'Информация по `{server_address[0]}:{server_address[1]}`.'
                                               f'\nВ данный момент сервер выключен или не удалось получить его данные.'
                                               f'\nПоследнее обновление данных: __{str(now.strftime("%d.%m.%y %H:%M:%S "))}__',
                                       embed=None)

        except Exception as error:
            self.logger.error(error)
        finally:
            self.pgsql.close_conn(conn, user)
            self.mysql.close_conn(database, gamer)

    @update.before_loop
    async def ready(self):
        await self.client.wait_until_ready()

    # @commands.command(
    #     name='статус',
    #     help="<префикс>статус #статус-серверов",
    #     brief="<префикс>статус <хайлайт канала>")
    # @commands.cooldown(1, 5, commands.BucketType.user)
    # @commands.guild_only()
    # @commands.has_permissions(administrator=True)
    # async def main_channel(self, ctx, channel: discord.TextChannel):
    #     conn, user = self.pgsql.connect()
    #     guild_id = channel.guild.id
    #     user.execute("SELECT info FROM info WHERE guild_id = %s", [guild_id])
    #     info = user.fetchone()[0]
    #
    #     if 'status' in info.keys():
    #         await ctx.channel.send(embed=await functions.embeds.
    #                                description("Статус уже существует.", "Канал, куда отсылается вся инофрмация по "
    #                                                                      "статусам серверов уже есть."))
    #         return
    #
    #     info['status'] = {}
    #     info['status']['channel'] = channel.id
    #     await ctx.channel.send(embed=await functions.embeds.
    #                            description("Статус уже существует.", "Канал, куда отсылается вся инофрмация по "
    #                                                                  "статусам серверов уже есть."))
    #
    #     user.execute("UPDATE info SET info = %s WHERE guild_id = %s", (json.dumps(info), guild_id))
    #     conn.commit()
    #     self.logger.info("Channel for logging was saved.")
    #
    #     await ctx.channel.send(embed=await functions.embeds.description("ВНИМАНИЕ", "Пожалуйста убедитесь, "
    #                                                                                 "что в этот канал никто не "
    #                                                                                 "сможет писать, а также "
    #                                                                                 "ставить реакции! \nВ "
    #                                                                                 "противном случае, обновление "
    #                                                                                 "статуса может работать "
    #                                                                                 "неверно."))
    #
    #     self.pgsql.close_conn(conn, user)

    @commands.command(
        help="<префикс>ip 192.168.1.1:27015 https://steamcommunity.com/sharedfiles/filedetails/?id=...",
        brief="<префикс>ip <ip:port> <коллекция workshop>")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def ip(self, ctx, ip: str, collection: str):
        address = ip.split(":")

        request = requests.head(collection)
        if request.status_code != 200:
            await ctx.channel.send(embed=await functions.embeds.description("Ссылка коллекции недействительна",
                                                                            "URL коллекции не доступна для просмотра. "
                                                                            "Если это программная ошибка, то "
                                                                            "пожалуйста попробуйте позже."))

        conn, user = self.pgsql.connect()

        user.execute("SELECT * FROM status")
        status = user.fetchall()

        if not address[1].isdigit():
            await ctx.channel.send(embed=await functions.embeds.description("Порт указан с ошибкой",
                                                                            "Порт {} не является числом, пожалуйста "
                                                                            "перепроверте его.".format(address[1])))
            return

        if ip not in status:
            channel = discord.utils.get(self.client.get_all_channels(), name='статус-серверов')
            if not channel:
                await ctx.channel.send(embed=await functions.embeds.description("Канал СТАТУС-СЕРВЕРОВ не создан",
                                                                                "Чтобы статус серверов заработал нужен"
                                                                                "канал с названием **статус-серверов**"
                                                                                " его, иначе ничего работать не будет"))
                return

            id = collection.split("=")

            message = await channel.send(embed=await functions.embeds.description("Ожидайте изменение статуса",
                                                                                  "Ожидайте, пока пройдет "
                                                                                  "загружаются данные."))

            user.execute(f"INSERT INTO status VALUES (%s, %s, %s)", (str(ip), message.id, int(id[1])))
            conn.commit()
            await ctx.channel.send(embed=await functions.embeds.description("IP успешно добавлен",
                                                                            "Адресс: `{}` успешно выведен в "
                                                                            "канал.".format(ip)))

        self.pgsql.close_conn(conn, user)

    # @commands.command(
    #     name="удалить_статус",
    #     help="<префикс>удалить_статус")
    # @commands.cooldown(1, 5, commands.BucketType.user)
    # @commands.guild_only()
    # @commands.has_permissions(administrator=True)
    # async def delete_status(self, ctx):
    #     conn, user = self.pgsql.connect()
    #     guild_id = ctx.guild.id
    #     user.execute("SELECT info FROM info WHERE guild_id = %s", [guild_id])
    #     info = user.fetchone()[0]
    #
    #     if 'status' not in info.keys():
    #         await ctx.channel.send(embed=await functions.embeds.description("Статуса не существует.",
    #                                                                         "Либо вы его уже удалили, либо никогда не "
    #                                                                         "создавали."))
    #         return
    #
    #     channel = self.client.get_channel(info['status']['channel'])
    #
    #     for key in info['status'].keys():
    #         if key != 'channel':
    #             try:
    #                 message = await channel.fetch_message(info['status'][key]['message_id'])
    #             except Exception as error:
    #                 self.logger.error(error)
    #             else:
    #                 await message.delete()
    #     del info['status']
    #
    #     user.execute("UPDATE info SET info = %s WHERE guild_id = %s", (json.dumps(info), guild_id))
    #     conn.commit()
    #     self.logger.info("Channel for logging was saved.")
    #
    #     await ctx.channel.send(embed=await functions.embeds.description("Статус успешно удален.",
    #                                                                     "Канал, куда указывалась информация по "
    #                                                                     "серверам, успешно удален."))
    #
    #     self.pgsql.close_conn(conn, user)
