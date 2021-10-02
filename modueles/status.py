from models import GuildDiscord, StatusGMS, GmodPlayer, UserDiscord, db
import requests
import discord
import functions
import datetime
import logging
import peewee
from steam import game_servers
from steam.steamid import SteamID
from discord.ext import commands, tasks


class LoadDataStatusFailed(commands.CheckFailure):
    pass


class Status(commands.Cog, name="Статус серверов"):

    def __init__(self, client):
        self.client = client

        logger = logging.getLogger("status")
        logger.setLevel(logging.INFO)
        self.logger = logger

        self.count = 0
        self.id_creator = 349648699976318987

        self.update.start()

    async def open_connect(ctx):
        try:
            db.connect()
            return True
        except peewee.OperationalError:
            db.close()
            db.connect()
            return True

    async def admin(ctx):
        return ctx.author.id == 349648699976318987 or discord.Permissions.administrator in ctx.author.top_role().permissions

    @staticmethod
    def __get_info(server_address):
        try:
            data = game_servers.a2s_info(server_address, timeout=2)
            players = game_servers.a2s_players(server_address, timeout=2)
        except Exception:
            try:
                data = game_servers.a2s_info(server_address, timeout=2)
                players = game_servers.a2s_players(server_address, timeout=2)
            except Exception:
                return 0, 0, 0, 0, 0, 0, False
            else:
                
                ping = data['_ping']
                name = data['name']
                map_server = data['map']
                player_count = data['players']
                max_players = data['max_players']
                return ping, name, player_count, players, max_players, map_server, True
        else:
                ping = data['_ping']
                name = data['name']
                map_server = data['map']
                player_count = data['players']
                max_players = data['max_players']
                return ping, name, player_count, players, max_players, map_server, True

    async def __get_all_servers_ip(self, status):
        servers_info = list()

        channel = discord.utils.get(self.client.get_all_channels(), name='статус-серверов')
        if not channel:
            return None

        for value in status:
            try:
                message = await channel.fetch_message(value.message)
            except discord.NotFound:
                message = channel.id
            except discord.HTTPException:
                message = await channel.fetch_message(value.message)

            collection = f"https://steamcommunity.com/sharedfiles/filedetails/?id={value.collection}"
            name = value.name
            ip = value.ip.split(":")

            servers_info.append((ip[0], int(ip[1]), collection, message, name))

        return servers_info

    @tasks.loop(seconds=60.0)
    async def update(self):
        await self.open_connect()
        servers = None
        
        try:
            servers = StatusGMS.select().join(GuildDiscord)
        except peewee.PeeweeException as error:
            self.logger.error(error)

        if servers is None:
            return

        for server in servers:

            guild = self.client.get_guild(server.guild.guild)
            channel = discord.utils.get(guild.channels, name='статус-серверов')
            if not channel:
                continue

            server_address = (server.ip.split(":")[0], int(server.ip.split(":")[1]))
            collection = f"https://steamcommunity.com/sharedfiles/filedetails/?id={server.collection}"
            message_id = server.message

            try:
                message = await channel.fetch_message(message_id)
            except discord.NotFound:
                query = StatusGMS.delete().where(StatusGMS.id == server.id)
                query.execute()
                continue
            except discord.HTTPException:
                message = await channel.fetch_message(message_id)

            ping, name, player_count, players, max_players, map_server, check_status = \
                self.__get_info(server_address)

            if check_status:
                server.name = name
                server.save()
                ply = ['*Загружается на сервер.*'] * player_count
                for i, player in zip(range(len(players)), players):
                    time = str(datetime.datetime.utcfromtimestamp(int(player["duration"])).strftime("%H:%M:%S"))
                    SID, gmod, checked_ply, member, link = None, None, None, None, None
                    try:
                        gmod = GmodPlayer.get(GmodPlayer.nick == player["name"])
                    except peewee.DoesNotExist as error:
                        self.logger.debug(error)

                    if gmod is not None:
                        try:
                            checked_ply = UserDiscord.get(UserDiscord.SID == gmod.SID)
                            member = await message.guild.fetch_member(checked_ply.discord_id)
                        except peewee.DoesNotExist as error:
                            self.logger.debug(error)
                        except discord.NotFound as error:
                            self.logger.debug(error)

                        SID = SteamID(gmod.SID)
                        link = SID.community_url

                    if SID is not None and checked_ply is not None and member is not None:
                        ply[i] = f"{i + 1}. {member.mention} | **{time}**"
                    elif SID is not None:
                        ply[i] = f"{i + 1}. [{player['name']}]({link}) | **{time}**"
                    elif SID is None and player["name"] != '':
                        ply[i] = f"{i + 1}. [{player['name']}]({link}) | `ДАННЫЕ ОТСУТСТВУЮТ`"

                title = discord.Embed(colour=discord.Colour.dark_green(),
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
                now = datetime.datetime.now()
                title.set_footer(text=f'Последнее обновление данных: {str(now.strftime("%d.%m.%y %H:%M:%S "))}')
                await message.edit(embed=title)
                if self.count == 5 or self.count == 30:
                    creator = await self.client.fetch_user(self.id_creator)
                    await creator.send("Окей, все ок.")
                    self.count == 0
            else:
                name = server.name
                now = datetime.datetime.now()
                embed = discord.Embed(colour=discord.Colour.dark_red(),
                                      url=collection,
                                      title=f'Коллекция сервера')
                embed.description = f'Информация по `{name}`.' \
                                    f'\nВ данный момент сервер выключен или не удалось получить его данные.'
                embed.set_footer(text=f'Последнее обновление данных: {str(now.strftime("%d.%m.%y %H:%M:%S "))}')
                self.count += 1
                await message.edit(embed=embed)
                if self.count == 5 or self.count == 30:
                    creator = await self.client.fetch_user(self.id_creator)
                    await creator.send("Статус-серверов, проверь пжспс. Там опять беда. Знаю не охото но надо.")

    @update.before_loop
    async def ready(self):
        await self.client.wait_until_ready()

    @commands.command(
        help="<префикс>ip 192.168.1.1:27015 https://steamcommunity.com/sharedfiles/filedetails/?id=...",
        brief="<префикс>ip <ip:port> <коллекция workshop>")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    @commands.check(open_connect)
    @commands.check(admin)
    async def ip(self, ctx, ip: str, collection: str):
        address = ip.split(":")

        request = requests.head(collection)
        if request.status_code != 200:
            await ctx.channel.send(embed=await functions.embeds.description("Ссылка коллекции недействительна",
                                                                            "URL коллекции не доступна для просмотра. "
                                                                            "Если это программная ошибка, то "
                                                                            "пожалуйста попробуйте позже."))

        if not address[1].isdigit():
            await ctx.channel.send(embed=await functions.embeds.description("Порт указан с ошибкой",
                                                                            "Порт {} не является числом, пожалуйста "
                                                                            "перепроверте его.".format(address[1])))
            return
 
        channel = discord.utils.get(ctx.guild.channels, name='статус-серверов')
        if not channel:
            await ctx.channel.send(embed=await functions.embeds.description("Канал СТАТУС-СЕРВЕРОВ не создан",
                                                                            "Чтобы статус серверов заработал нужен"
                                                                            "канал с названием **статус-серверов**"
                                                                            " его, иначе ничего работать не будет"))
            return

        collection_id = collection.split("=")[-1]

        message = await channel.send(embed=await functions.embeds.description("Ожидайте изменение статуса",
                                                                              "Статус изменится в течение минуты."))

        guild = GuildDiscord.get(GuildDiscord.guild == ctx.guild.id)

        query = StatusGMS.insert(ip=ip,
                                 guild=guild.guild_id,
                                 message=message.id,
                                 collection=int(collection_id))
        query.execute()
        await ctx.channel.send(embed=await functions.embeds.description("IP успешно добавлен",
                                                                        "Адресс: `{}` успешно выведен в "
                                                                        "канал.".format(ip)))
