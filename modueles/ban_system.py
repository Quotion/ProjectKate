import discord
from models import *
from discord.ext import commands
import functions
import datetime
import logging
import steam.steamid


class Ban(commands.Cog, name="Система банов"):

    def __init__(self, client):
        self.client = client

        self.servers = 2

        logger = logging.getLogger("ban")
        logger.setLevel(logging.INFO)

        self.logger = logger

    async def open_connect(self):
        try:
            db.connect()
            return True
        except peewee.OperationalError:
            db.close()
            db.connect()
            return True

    @commands.check(open_connect)
    async def check_client(self, ctx, client):
        if client.find("<@!") != -1:
            client = await commands.MemberConverter().convert(ctx, client)
            if not client:
                await ctx.channel.send(
                    embed=await functions.embeds.description("Discord пользователя не был найден.",
                                                             "Пользователь с таким Discord-ом не"
                                                             " был найден. Пожалуйста перероверте"
                                                             " правильность введных Вами данных."))
                return None
            else:
                return client
        else:
            client = client.upper()
            data = GmodPlayer.select().where(GmodPlayer.SID == client)
            if len(data) < 1:
                self.logger.error("SteamID for ban not in BD.")
                await ctx.channel.send(embed=await functions.embeds.description("SteamID не найдено в базе данных.",
                                                                                "Игрок с таким SteamID ниразу не "
                                                                                "появлялся на сервере и не был внесен "
                                                                                "в базу данных, поэтому забанить его "
                                                                                "можно только после его появления на "
                                                                                "сервере."))
                return None
            else:
                return client 

    @staticmethod
    @commands.check(open_connect)
    async def get_data_gamer(ctx, client):
        if isinstance(client, discord.Member):
            try:
                user = UserDiscord.get(UserDiscord.discord_id == client.id)
            except peewee.DoesNotExist:
                await ctx.channel.send(embed=await functions.embeds.description("У данного пользователя нету профиля",
                                                                                "Вы не сможете забанить данного игрока"
                                                                                "через Discord, т.к. у него нету"
                                                                                "профиля."))
                return None

            if not user.SID:
                await ctx.channel.send(embed=await functions.embeds.description("Игрок не синхронизирован",
                                                                                "Игрок с таким Discord-ом не "
                                                                                "синхронизирован. Введите его SteamID, "
                                                                                "чтобы забанить."))
                return None

            data_gamer = GmodBan.select().where(GmodBan.SID == user.SID).order_by(GmodBan.server)
            if not data_gamer:
                try:
                    for i in range(1, self.servers + 1):
                        GmodBan.insert(SID=client, server=i)
                
                    data_gamer = GmodBan.select().where(GmodBan.SID == user.SID).order_by(GmodBan.server)
                except:
                    await ctx.channel.send(embed=await functions.embeds.description("Игрок ни разу не был на сервере",
                                                                                "Игрок с таким Discord-ом не "
                                                                                "был найден в БД сервера."))
                return None

            return data_gamer

    @commands.command(
        name='бан',
        help="Данные которые нужны для использования этой команды:"
             "\n<client>: SteamID (пример: STEAM_0:0:00000) или Discord (пример: @Chell)"
             "\n<time>: Время в минутах"
             "\n<reason>: Причина должна быть указана в конец и не должна быть больше чем 256 символов.",
        brief="<префикс>бан STEAM_0:0:00000 1000 нарушение правил",
        description="Команда, с помощью которой, можно забнить игрока, не заходя на сервер.")
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @commands.check(open_connect)
    async def ban(self, ctx, client: str, time: int, *args):
        if len(args) > 0:
            reason = ' '.join([word for word in args])
        else:
            reason = 'причина'

        client = await self.check_client(ctx, client)

        if not client:
            return

        time_ban = int(datetime.datetime.today().timestamp())
        time_unban = int(time) * 60 + int(datetime.datetime.today().timestamp())

        data_gamer = await self.get_data_gamer(ctx, client)

        if not data_gamer:
            return

        user = None

        for column in data_gamer:
            if column.ban == 0 and column.ban_admin is '':
                column.ban_reason = reason
                column.ban_admin = ctx.author.name
                column.ban_date = time_ban
                column.unban_date = time_unban
                column.save()
                await ctx.channel.send(embed=await functions.embeds.ban_message(column))
            else:
                await ctx.channel.send(embed=await functions.embeds.description("Игрок уже забанен на {} сервере.".format(column.server),
                                                                                "Игрок **{}({})** уже забанен по причине `"
                                                                                "{}`".format(column.SID.nick,
                                                                                            column.SID_id,
                                                                                            column.ban_reason)))

    @commands.command(
        name='разбан',
        help="Данные которые нужны для использования этой команды:"
             "\n<client>: SteamID (пример: STEAM_0:0:00000) или Discord (пример: @Chell)",
        brief="<префикс>разбан @Chell",
        description="Команда, с помощью которой, можно разбанить игрока, не заходя на сервер.")
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @commands.check(open_connect)
    async def unban(self, ctx, client: str):
        now = datetime.datetime.now()

        client = await self.check_client(ctx, client)

        if not client:
            return

        data_gamer = await self.get_data_gamer(ctx, client)

        if not data_gamer:
            return

        for column in data_gamer:
            if column.ban > 0 and column.ban_reason is not '':
                column.ban_reason = None
                column.ban_admin = None
                column.ban_date = None
                column.unban_date = None
                column.save()
                await ctx.channel.send(embed=await functions.embeds.description(f"{data_gamer.SID.nick} был разбанен на {column.server} сервере.",
                                                                                f"Игрок **{data_gamer.SID.nick}"
                                                                                f"({data_gamer.SID_id}**) разбанен.\n"
                                                                                f"Дата разбана: "
                                                                                f"({now.strftime('%H:%M %d.%m.%Y')})\n"
                                                                                f"Разбанил: {ctx.author.mention}", ))
            else:
                await ctx.channel.send(embed=await functions.embeds.description("Игрок уже забанен на {} сервере.".format(column.server),
                                                                                "Игрок **{}({})** уже забанен по причине `"
                                                                                "{}`".format(column.SID.nick,
                                                                                            column.SID_id,
                                                                                            column.ban_reason)))

    @commands.command(
        name='проверь',
        help="Данные которые нужны для использования этой команды:"
             "\n<client>: SteamID (пример: STEAM_0:0:00000), "
             "или Discord (пример: @Chell), "
             "или можно оставить просто команду",
        brief="<префикс>проверь",
        description="Команда, с помощью которой, можно проверить игрока, находится ли тот в бане или нет.")
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.check(open_connect)
    async def check_ban(self, ctx, client: str):
        client = await self.check_client(ctx, client)

        if not client:
            return

        data_gamer = await self.get_data_gamer(ctx, client)


        if not data_gamer:
            return

        user = data_gamer[0]

        if user.ban == 0 and (not user.ban_admin or user.ban_admin == "None"):
            await ctx.channel.send(embed=await functions.embeds.description("Игрок не забнен",
                                                                            f"Игрок (**{user.SID_id}**) "
                                                                            f"не забанен."))
        else:
            await ctx.channel.send(embed=await functions.embeds.discord_check_ban(user))

    @commands.command(name='синхр',
                      help="Данные которые нужны для использования этой команды:"
                           "\n<data>: Ссылка на аккаунт Steam (пример: https://steamcommunity.com/id/garry) "
                           "или все виды SteamID (примеры: STEAM_0:1:7099 или 76561197960279927 и т.д.)",
                      brief="<префикс>синхр https://steamcommunity.com/id/garry",
                      description="Команда, с помощью которой, можно синхронизировать аккаунт в Garry's mod и Discord,"
                                  "чтобы стало удобно менять Ваш ранг или просмотривать Вашу статистику.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.check(open_connect)
    async def sync(self, ctx, data: str):
        try:
            user = UserDiscord.get(UserDiscord.discord_id == ctx.author.id)
        except peewee.DoesNotExist:
            await ctx.channel.send(embed=await functions.embeds.description("Создайте профиль для синхронизации!",
                                                                            f"Для того чтобы синхронизировать свой"
                                                                            f"аккаунт в Garry's mod и Discord "
                                                                            f"необходимо создать **профиль**. "
                                                                            f"Для этого введите команду "
                                                                            f"**{self.client.command_prefix[0]}"
                                                                            f"профиль**"))
            return

        if data.startswith('https://steamcommunity.com/') or data.startswith('http://steamcommunity.com/'):
            SteamID = steam.steamid.steam64_from_url(data)
            if not SteamID:
                await ctx.channel.send(embed=await functions.embeds.description("SteamID не найден.",
                                                                                f"После отправки запроса с данными"
                                                                                f", которые Вы ввели, нам не "
                                                                                f"пришло подтверждения, что такой "
                                                                                f"SteamID существует."))
                return
            steamid = steam.steamid.SteamID(SteamID).as_steam2_zero
        else:
            SteamID = steam.steamid.SteamID(data)
            if not SteamID:
                await ctx.channel.send(embed=await functions.embeds.description("SteamID не найден.",
                                                                                f"После отправки запроса с данными"
                                                                                f", которые Вы ввели, нам не "
                                                                                f"пришло подтверждения, что такой "
                                                                                f"SteamID существует."))
                return
            steamid = SteamID.as_steam2_zero

        try:
            player = GmodPlayer.get(GmodPlayer.SID == steamid)
        except peewee.DoesNotExist:
            await ctx.channel.send(embed=await functions.embeds.description("Не найден в базе данных.",
                                                                            f"Игрок с таким SteamID ни разу не "
                                                                            f"играл на сервере."))
            return

        if user.SID is None or user.SID is "None":
            user.SID = steamid
            user.save()
            await ctx.channel.send(embed=await functions.embeds.description("SteamID успешно синхронизирован.",
                                                                            f"Спасибо за синхронизацию вашего "
                                                                            f"аккаунта Garry's mod и Discord."))
        elif player.SID == user.SID:
            await ctx.channel.send(embed=await functions.embeds.description("Вы уже синхронизированы.",
                                                                            f"Данный SteamID уже пренадлежит вашему "
                                                                            f"аккаунту."))
        else:
            await ctx.channel.send(embed=await functions.embeds.description("Данный SteamID уже используется.",
                                                                            f"Пожалуйста не пытайтесь ввести чужой"
                                                                            f"SteamID. Это ни к чему хорошему не "
                                                                            f"приведет."))

    @commands.command(name='разсинхр',
                      help="Данные которые нужны для использования этой команды:"
                           "\n<data>: Ссылка на аккаунт Steam (пример: https://steamcommunity.com/id/garry) "
                           "или все виды SteamID (примеры: STEAM_0:1:709900023 или 76561197960279927 и т.д.)",
                      brief="<префикс>синхр https://steamcommunity.com/id/garry",
                      description="Команда, с помощью которой, можно синхронизировать аккаунт в Garry's mod и Discord,"
                                  "чтобы стало удобно менять Ваш ранг или просмотривать Вашу статистику.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.check(open_connect)
    async def sync_down(self, ctx):
        try:
            user = UserDiscord.get(UserDiscord.discord_id == ctx.author.id)
        except peewee.DoesNotExist:
            await ctx.channel.send(embed=await functions.embeds.description("Создайте профиль для синхронизации!",
                                                                            f"Для того чтобы синхронизировать свой"
                                                                            f"аккаунт в Garry's mod и Discord "
                                                                            f"необходимо создать **профиль**. "
                                                                            f"Для этого введите команду "
                                                                            f"**{self.client.command_prefix[0]}"
                                                                            f"профиль**"))
            return

        if user.SID is None or user.SID is "None":
            await ctx.channel.send(embed=await functions.embeds.description("Вы не были синхронизированы.",
                                                                            f"Чтобы разсинхронизировать ваш аккаунт со "
                                                                            f"Garry's mod-ом вам нужно для начало его"
                                                                            f"синхронизировать."))
        else:
            user.SID = None
            user.save()
            await ctx.channel.send(embed=await functions.embeds.description("Аккаунт успешно разсинхронизирован.",
                                                                            f"Ваш аккаунт Garry's mod-а успешно "
                                                                            f"разсинхронизирован с Discord"))

    @commands.command(name="ранг",
                      help="Данные которые нужны для использования этой команды:"
                           "\n<client>: SteamID (пример: STEAM_0:0:00000) или Discord (пример: @Chell)"
                           "\n<rank>: Ранг, на который нужно нужно поменять действющий "
                           "(примеры: superadmin или operator)",
                      brief="<префикс>ранг STEAM_0:0:0000000 superadmin",
                      description="Команда, с помощью которой, можно изменить ранг игрока, не заходя на сервер.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @commands.check(open_connect)
    async def set_rank(self, ctx, client: str, rank: str):

        client = await self.check_client(ctx, client)

        if not client:
            return

        data_gamer = await self.get_data_gamer(ctx, client)

        if not data_gamer:
            return

        data_gamer.SID.group = rank
        data_gamer.SID.save()
        self.logger.info("User with SteamID {} successfully changed rank.".format(data_gamer.SID))
        await ctx.channel.send(embed=await functions.embeds.description("Ранг игрока был изменен.",
                                                                        f"Ранг игрока **{data_gamer.SID.nick}** был изменен "
                                                                        f"на {rank}."))

    # @commands.command(
    #     name="купить_ранг",
    #     help="Данные которые нужны для использования этой команды:"
    #          "\n<rank>: Название ранга, который вы хотите приобрести (пример: VIP)",
    #     brief="<префикс>купить_ранг superadmin",
    #     description="Команда, с помощью которой, можно приобрести ранг на сервере, за обычную валюту.")
    # @commands.cooldown(1, 30, commands.BucketType.user)
    # async def buy_rank(self, ctx, rank: str):
    #     if rank.lower( and rank.lower() != "superadmin":
    #         await ctx.send(embed=await functions.embeds.description("Ранг не продается.", "Ранг, который вы хотите "
    #                                                                                       "купить либо не существует,"
    #                                                                                       "либо не продается."))
    #         return
    #
    #     elif rank.lower() == "superadmin":
    #         await ctx.send(embed=await functions.embeds.description("Нафиг пошел.", "Фу, брось бяку."))
    #         return
    #
    #     conn, user = self.pgsql.connect()
    #     database, gamer = self.mysql.connect()
    #     user.execute("SELECT * FROM users WHERE \"discordID\" = {}".format(ctx.author.id))
    #     data_user = user.fetchone()
    #     if not data_user[6] or data_user[6] == "None":
    #         await ctx.channel.send(embed=await functions.embeds.description("Игрок не синхронизирован",
    #                                                                         "Игрок с таким Discord-ом не "
    #                                                                         "синхронизирован. Введите его SteamID, "
    #                                                                         "чтобы забанить."))
    #         return
    #
    #     gamer.execute("SELECT rank FROM users_steam WHERE steamid = '{}'".format(data_user[6]))
    #     now_rank = gamer.fetchone()[0]
    #     if rank == now_rank:
    #         await ctx.send(embed=await functions.embeds.description("Ранги одинаковы", "Ранг, который вы хотите купить"
    #                                                                                    "у Вас уже есть."))
    #
    #     if int(data_user[3]) >= 500000 and rank.lower() == "vip":
    #         user.execute("UPDATE users SET goldmoney = goldmoney - {} WHERE \"discordID\" = {}".
    #                      format(500000, ctx.author.id))
    #         conn.commit()
    #         gamer.execute(f"UPDATE users_steam SET rank = 'admin' WHERE steamid = '{data_user[6]}'")
    #         database.commit()
    #         role = discord.utils.get(ctx.guild.roles, name="VIP")
    #         await ctx.author.add_roles(role)
    #         await ctx.send(embed=await functions.embeds.description("Вы купили VIP-ранг.", "Спасибо за приобретение "
    #                                                                                        "ранга на нешем сервере."
    #                                                                                        "Желаем Вам приятной игры!"))
    #     # elif money >= 1000000 and rank.lower() == "premium":
    #     #     user.execute("UPDATE users SET goldmoney = goldmoney - {} WHERE \"discordID\" = {}".
    #     #                  format(1000000, ctx.author.id))
    #     #     conn.commit()
    #     #     gamer.execute(f"UPDATE users_steam SET rank = 'premium' WHERE steamid = '{steamid}'")
    #     #     database.commit()
    #     #     await ctx.send(embed=await functions.embeds.description(ctx.author.mention, buying_premium))
    #     else:
    #         await ctx.send(embed=await functions.embeds.description("Недостаточно средств.", "Как говорится, денег нет,"
    #                                                                                          " но вы держитесь."))
    #
    #     self.pgsql.close_conn(conn, user)
    #     self.mysql.close_conn(database, gamer)
