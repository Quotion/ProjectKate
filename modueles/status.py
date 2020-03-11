import json
import discord
import functions
import datetime
import logging
from functions.database import MySQLConnection, PgSQLConnection
import valve.source.a2s
from discord.ext import commands
from language.treatment_ru import *


class Status(commands.Cog, name="Статус серверов"):

    def __init__(self, client):
        self.client = client

        logger = logging.getLogger("status")
        logger.setLevel(logging.INFO)
        self.logger = logger

        self.mysql = MySQLConnection()
        self.pgsql = PgSQLConnection()

    @commands.command(name="проверь_статус", help="<префикс>проверь_статус")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def check_status(self, ctx):
        conn, user = self.pgsql.connect()
        guild_id = ctx.guild.id
        user.execute("SELECT info FROM info WHERE guild_id = %s", [guild_id])
        info = user.fetchone()[0]

        if 'status' not in info.keys():
            self.pgsql.close_conn(conn, user)
            return

        channel = self.client.get_channel(info['status']['channel'])

        for key in info['status'].keys():
            if key == "channel":
                pass
            else:
                try:
                    await channel.fetch_message(info['status'][key]['message_id'])
                except discord.HTTPException:
                    del info['status'][key]
                    user.execute("UPDATE info SET info = %s WHERE guild_id = %s", (json.dumps(info), guild_id))
                    conn.commit()
                    await ctx.channel.send(embed=await functions.embeds.
                                           description(ctx.author.mention, message_not_found))
                    self.logger.info("{} was deleted from BD".format(info['status'][key]['message_id']))

        self.pgsql.close_conn(conn, user)

    async def _send(self, ctx):
        conn, user = self.pgsql.connect()
        guild_id = ctx.guild.id
        user.execute("SELECT info FROM info WHERE guild_id = %s", [guild_id])
        info = user.fetchone()[0]

        for key in info['status'].keys():
            if key != "channel" and not info['status'][key]['message_id']:
                channel = self.client.get_channel(info['status']['channel'])
                message = await channel.send("This is null message for server status.")
                await message.add_reaction("🔄")
                info['status'][key]['message_id'] = message.id
                try:
                    user.execute("UPDATE info SET info = %s WHERE guild_id = %s", (json.dumps(info), guild_id))
                    conn.commit()
                    self.logger.info("Channel for logging was saved.")
                except Exception as error:
                    await ctx.channel.send(something_went_wrong)
                    self.logger.error(error)

        self.pgsql.close_conn(conn, user)

    def get_info(self, server_address):
        try:
            data = valve.source.a2s.ServerQuerier(server_address)
            name = data.info()["server_name"]
            player_count = data.info()["player_count"]
            players = data.players()
            max_players = data.info()["max_players"]
            map_server = data.info()["map"]
        except Exception as error:
            self.logger.error(error)
            return 0, 0, 0, 0, 0, False
        else:
            self.logger.info("Connect to server establishment.")
            return name, player_count, players, max_players, map_server, True

    async def update(self, channel, message, server_address):
        try:
            buff = server_address.split(":")
            server_address = (buff[0], int(buff[1]))

            database, gamer = self.mysql.connect()
            conn, user = self.pgsql.connect()

            database.set_charset_collation('latin1', 'latin1_general_ci')
            database.commit()

            name, player_count, players, max_players, map_server, check_status = self.get_info(server_address)

            gamer.execute('SELECT nick, steamid FROM users_steam')
            come_in_ply = gamer.fetchall()

            if check_status:
                i = 0
                ply = ['*Загружается на сервер.*'] * player_count
                for player in players["players"]:
                    time = str(int(datetime.datetime.fromtimestamp(player["duration"]).strftime("%H"))) + \
                           datetime.datetime.fromtimestamp(player["duration"]).strftime(":%M:%S")
                    steamid = ''
                    checked_ply = None
                    for lone in come_in_ply:
                        if player["name"].encode('utf8').decode('latin1') in lone[0]:
                            steamid = lone[1]
                            break
                    user.execute('SELECT "discordID" FROM users WHERE steamid = \'' + steamid + '\'')
                    try:
                        checked_ply = user.fetchone()[0]
                    except TypeError:
                        pass
                    except Exception as error:
                        self.logger.error(error)
                    else:
                        member = await channel.guild.fetch_member(int(checked_ply))

                    if player["name"] != '' and steamid != '' and checked_ply:
                        ply[i] = str(i + 1) + '. ' + member.mention + ' `' + steamid + '` [' + time + ']'
                        i += 1
                    elif player["name"] != '' and steamid != '':
                        ply[i] = str(i + 1) + '. **' + player["name"] + '** `' + steamid + '` [' + time + ']'
                        i += 1
                    elif player["name"] != '':
                        ply[i] = str(i + 1) + '. **' + player["name"] + '** [' + time + ']'
                        i += 1
                await message.edit(content="Чтобы обновить статистику нажмите на значок 🔄")
                title = discord.Embed(colour=discord.Colour.from_rgb(54, 57, 63))
                title.set_author(name=name,
                                 icon_url=channel.guild.icon_url)
                title.add_field(name='Статус:',
                                value=f'__Онлайн__')
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
                await message.edit(embed=title)
            else:
                now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
                await message.edit(content=f'Информация по __**{server_address[0]}:{server_address[1]}**__.'
                                           f'\nВ данный момент сервер выключен или не удалось получить данные.'
                                           f'\nПоследнее обновление данных: __{str(now.strftime("%d.%m.%y %H:%M:%S "))}__',
                                   embed=None)

            self.pgsql.close_conn(conn, user)
            self.mysql.close_conn(gamer, database)
        except Exception as error:
            self.logger.error(error)

    @commands.command(name='статус', help="<префикс>статус <хайлайт канала>")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def main_channel(self, ctx):
        conn, user = self.pgsql.connect()
        guild_id = ctx.guild.id
        user.execute("SELECT info FROM info WHERE guild_id = %s", [guild_id])
        info = user.fetchone()[0]

        if 'status' in info.keys():
            await ctx.channel.send(embed=await functions.embeds.
                                   description(ctx.author.mention, status_already_exist))
            return

        elif ctx.message.channel_mentions and len(ctx.message.channel_mentions) == 1:
            info['status'] = {}
            info['status']['channel'] = ctx.message.channel_mentions[0].id
            await ctx.channel.send(channel_saved.format(ctx.author.mention, ctx.message.channel_mentions[0],
                                                        'статуса сервера(-ов)'))
            try:
                user.execute("UPDATE info SET info = %s WHERE guild_id = %s", (json.dumps(info), guild_id))
                conn.commit()
                self.logger.info("Channel for logging was saved.")
            except Exception as error:
                await ctx.channel.send(something_went_wrong)
                self.logger.error(error)
            else:
                await ctx.channel.send(embed=await functions.embeds.description(ctx.author.mention, please_confirm))

        elif ctx.message.channel_mentions:
            await ctx.channel.send(so_many_channels.format(ctx.author.mention))

        else:
            await ctx.channel.send(not_enough_channels.format(ctx.author.mention, self.client.command_prefix))
            self.logger.info("User entered incorrect data about guild channel: it's empty.")

        self.pgsql.close_conn(conn, user)

    @commands.command(help="<префикс>ip <ip:port>")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def ip(self, ctx):
        msg = ctx.message.content.split()
        address = msg[1].split(":")

        conn, user = self.pgsql.connect()
        guild_id = ctx.guild.id
        user.execute("SELECT info FROM info WHERE guild_id = %s", [guild_id])
        info = user.fetchone()[0]

        if address[1].isdigit() and len(msg) < 3:
            server_address = (address[0], int(address[1]))
            try:
                valve.source.a2s.ServerQuerier(server_address)
            except Exception as error:
                self.logger.error(error)
                await ctx.channel.send(server_not_valid.format(ctx.author.mention, msg[1]))
            else:
                if msg[1] not in info['status'].keys():
                    info['status'][msg[1]] = {}
                    info['status'][msg[1]]['message_id'] = None
                    info['status'][msg[1]]['time'] = int(datetime.datetime.today().timestamp()) - 60
                    try:
                        user.execute("UPDATE info SET info = %s WHERE guild_id = %s", (json.dumps(info), guild_id))
                        conn.commit()
                        self.logger.info("Channel for logging was saved.")
                    except Exception as error:
                        await ctx.channel.send(something_went_wrong)
                        self.logger.error(error)
                    else:
                        await self._send(ctx)
                        await ctx.channel.send("{} successes 👍".format(ctx.author.mention))
                else:
                    await ctx.channel.send(ip_exist.format(ctx.author.mention))
        elif len(msg) == 3:
            if msg[2] == "1":
                if msg[1] not in info['status'].keys():
                    info['status'][msg[1]] = {}
                    info['status'][msg[1]]['message_id'] = None
                    info['status'][msg[1]]['time'] = int(datetime.datetime.today().timestamp()) - 60
                    try:
                        user.execute("UPDATE info SET info = %s WHERE guild_id = %s", (json.dumps(info), guild_id))
                        conn.commit()
                        self.logger.info("Channel for logging was saved.")
                    except Exception as error:
                        await ctx.channel.send(something_went_wrong)
                        self.logger.error(error)
                    else:
                        await self._send(ctx)
                        await ctx.channel.send("{} successes 👍".format(ctx.author.mention))
                else:
                    await ctx.channel.send(ip_exist.format(ctx.author.mention))
        else:
            await ctx.channel.send(something_went_wrong_ip.format(ctx.author.mention, self.client.command_prefix))

        self.pgsql.close_conn(conn, user)

    @commands.command(name="удалить_статус", help="<префикс>удалить_статус")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def delete_status(self, ctx):
        conn, user = self.pgsql.connect()
        guild_id = ctx.guild.id
        user.execute("SELECT info FROM info WHERE guild_id = %s", [guild_id])
        info = user.fetchone()[0]

        if 'status' not in info.keys():
            await ctx.channel.send(nothing_to_delete.format(ctx.author.mention))
            return

        channel = self.client.get_channel(info['status']['channel'])

        for key in info['status'].keys():
            if key != 'channel':
                try:
                    message = await channel.fetch_message(info['status'][key]['message_id'])
                except Exception as error:
                    self.logger.error(error)
                else:
                    await message.delete()
        del info['status']
        try:
            user.execute("UPDATE info SET info = %s WHERE guild_id = %s", (json.dumps(info), guild_id))
            conn.commit()
            self.logger.info("Channel for logging was saved.")
        except Exception as error:
            await ctx.channel.send(something_went_wrong)
            self.logger.error(error)
        else:
            await ctx.channel.send("{} successes 👍".format(ctx.author.mention))

        self.pgsql.close_conn(conn, user)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):

        if str(payload.emoji) != "🔄":
            return

        conn, user = self.pgsql.connect()
        guild_id = payload.guild_id
        user.execute("SELECT info FROM info WHERE guild_id = %s", [guild_id])
        info = user.fetchone()[0]

        message_id = payload.message_id

        if 'status' not in info.keys():
            return

        if payload.channel_id != info['status']['channel']:
            return

        channel = self.client.get_channel(payload.channel_id)
        message = await channel.fetch_message(message_id)
        member = self.client.get_user(payload.user_id)

        for key in info['status'].keys():
            if key == "channel":
                pass

            elif info['status'][key]['message_id'] == message.id \
                    and info['status'][key]['time'] + 60 < int(datetime.datetime.today().timestamp()) \
                    and payload.user_id != self.client.user.id:
                await message.remove_reaction(payload.emoji, member)
                await self.update(channel, message, key)
                info['status'][key]['time'] = int(datetime.datetime.today().timestamp()) + 60
                try:
                    user.execute("UPDATE info SET info = %s WHERE guild_id = %s", (json.dumps(info), guild_id))
                    conn.commit()
                    self.logger.info("Channel for logging was saved.")
                except Exception as error:
                    self.logger.error(error)
                return
            elif info['status'][key]['message_id'] == message.id \
                    and payload.user_id != self.client.user.id:
                await message.remove_reaction(payload.emoji, member)

        self.pgsql.close_conn(conn, user)
