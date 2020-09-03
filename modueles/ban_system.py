import discord
from discord.ext import commands
from functions.database import PgSQLConnection, MySQLConnection
import functions
import datetime
import logging
import steam.steamid


class Ban(commands.Cog, name="Система банов"):

    def __init__(self, client):
        self.client = client

        logger = logging.getLogger("ban")
        logger.setLevel(logging.INFO)

        self.logger = logger

        self.mysql = MySQLConnection()
        self.pgsql = PgSQLConnection()

    async def check_client(self, ctx, client, gamer):
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
            gamer.execute("SELECT * FROM users_steam WHERE steamid = '{}'".format(client))
            data = gamer.fetchall()
            if not data:
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
    async def get_data_gamer(ctx, client, user, gamer):
        if isinstance(client, discord.Member):
            user.execute(f"SELECT steamid FROM users WHERE \"discordID\" = {client.id}")
            steamid = user.fetchone()[0]
            if not steamid or steamid == "None":
                await ctx.channel.send(embed=await functions.embeds.description("Игрок не синхронизирован",
                                                                                "Игрок с таким Discord-ом не "
                                                                                "синхронизирован. Введите его SteamID, "
                                                                                "чтобы забанить."))
                return None
            else:
                gamer.execute(f"SELECT * FROM users_steam WHERE steamid = '{steamid}'")
                data_gamer = gamer.fetchone()
                if not data_gamer:
                    await ctx.channel.send(
                        embed=await functions.embeds.description("Игрок ни разу не заходил на сервер",
                                                                 "Игрок с таким серверов ни разу не "
                                                                 "заходил на ."))
                    return None
                else:
                    return data_gamer[0]

        else:
            gamer.execute(f"SELECT * FROM users_steam WHERE steamid = '{client}'")
            data_gamer = gamer.fetchone()
            if not data_gamer:
                await ctx.channel.send(embed=await functions.embeds.description("Игрок ни разу не заходил на сервер",
                                                                                "Игрок с таким серверов ни разу не "
                                                                                "заходил на ."))
                return None
            else:
                return data_gamer[0]

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
    async def ban(self, ctx, client: str, time: int, *, reason: str):
        conn, user = self.pgsql.connect()
        database, gamer = self.mysql.connect()

        client = await self.check_client(ctx, client, gamer)
        
        if not client:
            return

        time_ban = int(datetime.datetime.today().timestamp())
        time_unban = int(time) * 60 + int(datetime.datetime.today().timestamp())

        data_gamer = self.get_steamid(ctx, client, user, gamer)

        if not data_gamer:
            return

        if data_gamer[3] != 1:
            self.logger.info(f'{ctx.author.name} banned {data_gamer[0]} for {(time_unban - time_ban) // 60} '
                             f'minutes, reason: {reason}.')
            gamer.execute(f"UPDATE users_steam SET ban_reason = '{reason}', ban_admin = '{ctx.author.name}', "
                          f"ban_date = {time_ban}, unban_date = {time_unban} WHERE steamid = '{data_gamer[0]}'")
            database.commit()
            await ctx.channel.send(embed=await functions.embeds.ban_message(reason, ctx.author.mention,
                                                                            data_gamer[0], (time_unban - time_ban)
                                                                            // 60, reason))
        else:
            await ctx.channel.send(embed=await functions.embeds.description("Игрок уже забанен",
                                                                            "Игрок {}({}) уже был забанен по "
                                                                            "причине "
                                                                            "{}".format(data_gamer[1],
                                                                                        data_gamer[0],
                                                                                        data_gamer[5])))

        self.pgsql.close_conn(conn, user)
        self.mysql.close_conn(database, gamer)

    @commands.command(
        name='разбан',
        help="Данные которые нужны для использования этой команды:"
             "\n<client>: SteamID (пример: STEAM_0:0:00000) или Discord (пример: @Chell)",
        brief="<префикс>разбан @Chell",
        description="Команда, с помощью которой, можно разбанить игрока, не заходя на сервер.")
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def unban(self, ctx, client: str):
        conn, user = self.pgsql.connect()
        database, gamer = self.mysql.connect()
        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))

        client = await self.check_client(ctx, client, gamer)

        if not client:
            return

        data_gamer = await self.get_data_gamer(ctx, client, user, gamer)

        if not data_gamer:
            return

        gamer.execute(f"UPDATE users_steam SET ban = 1, ban_reason = 'None', ban_admin = 'None', "
                      f"ban_date = 'None', unban_date = 'None' WHERE steamid = '{data_gamer[0]}'")
        database.commit()
        self.logger.info("User with SteamID {} successfully unbaned.".format(client))
        await ctx.channel.send(embed=await functions.embeds.description(f"{data_gamer[1]} был разбанен.",
                                                                        f"Игрок (**{data_gamer[0]}**) разбанен.\n"
                                                                        f"Дата разбана: "
                                                                        f"({now.strftime('%H:%M %d.%m.%Y')})\n"
                                                                        f"Разбанил: {ctx.author.mention}",))

        self.pgsql.close_conn(conn, user)
        self.mysql.close_conn(database, gamer)

    @commands.command(
        name='проверь',
        help="Данные которые нужны для использования этой команды:"
             "\n<client>: SteamID (пример: STEAM_0:0:00000), "
             "или Discord (пример: @Chell), "
             "или можно оставить просто команду",
        brief="<префикс>проверь",
        description="Команда, с помощью которой, можно проверить игрока, находится ли тот в бане или нет.")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def check_ban(self, ctx, client: str):
        conn, user = self.pgsql.connect()
        database, gamer = self.mysql.connect()

        client = await self.check_client(ctx, client, gamer)

        if not client:
            return

        data_gamer = await self.get_data_gamer(ctx, client, user, gamer)

        if not data_gamer:
            return

        if not str(data_gamer[3]).isdigit():
            gamer.execute(f"UPDATE users_steam SET ban = 0 WHERE steamid = '{data_gamer[0]}'")
            database.commit()
            data_gamer[3] = 0
            await ctx.channel.send(embed=await functions.embeds.description("Игрок не забнен",
                                                                            f"Игрок (**{data_gamer[0]}**) не забанен."))
            return
        else:
            if data_gamer[3] == 0 and (not data_gamer[4] or data_gamer[4] == "None"):
                await ctx.channel.send(embed=await functions.embeds.description("Игрок не забнен",
                                                                                f"Игрок (**{data_gamer[0]}**) "
                                                                                f"не забанен."))
            else:
                await ctx.channel.send(embed=await functions.embeds.discord_check_ban(data_gamer, client.name))

        self.pgsql.close_conn(conn, user)
        self.mysql.close_conn(database, gamer)

    @commands.command(name='синхр',
                      help="Данные которые нужны для использования этой команды:"
                           "\n<data>: Ссылка на аккаунт Steam (пример: https://steamcommunity.com/id/garry) "
                           "или все виды SteamID (примеры: STEAM_0:1:7099 или 76561197960279927 и т.д.)",
                      brief="<префикс>синхр https://steamcommunity.com/id/garry",
                      description="Команда, с помощью которой, можно синхронизировать аккаунт в Garry's mod и Discord,"
                                  "чтобы стало удобно менять Ваш ранг или просмотривать Вашу статистику.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def sync(self, ctx, data: str):
        try:
            conn, user = self.pgsql.connect()
            database, gamer = self.mysql.connect()

            try:
                user.execute("SELECT * FROM users WHERE \"discordID\" = {}".format(ctx.author.id))
                var = user.fetchone()[0]
            except TypeError:
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

            gamer.execute("SELECT nick FROM users_steam WHERE steamid = %s", [steamid])
            k = gamer.fetchone()

            try:
                user.execute("SELECT * FROM users WHERE steamid = '{}'".format(steamid))
                var = user.fetchone()[0]
            except IndexError:
                pass
            except TypeError:
                pass
            else:
                await ctx.channel.send(embed=await functions.embeds.description("Данный SteamID уже используется.",
                                                                                f"Пожалуйста не пытайтесь ввести чужой"
                                                                                f"SteamID. Это ни к чему хорошему не "
                                                                                f"приведет."))
                return

            if not k:
                await ctx.channel.send(embed=await functions.embeds.description("Не найден в базе данных.",
                                                                                f"Игрок с таким SteamID ни разу не "
                                                                                f"играл на сервере."))
                return

            user.execute(f"UPDATE users SET steamid = '{steamid}' WHERE \"discordID\" = '{ctx.author.id}'")
            conn.commit()
            await ctx.channel.send(embed=await functions.embeds.description("SteamID успешно синхронизирован.",
                                                                            f"Спасибо за синхронизацию вашего "
                                                                            f"аккаунта Garry's mod и Discord."))
        except Exception as error:
            self.logger.error(error)
        finally:
            self.pgsql.close_conn(conn, user)
            self.mysql.close_conn(database, gamer)

    @commands.command(name="ранг",
                      help="Данные которые нужны для использования этой команды:"
                           "\n<client>: SteamID (пример: STEAM_0:0:00000) или Discord (пример: @Chell)"
                           "\n<rank>: Ранг, на который нужно нужно поменять действющий "
                           "(примеры: superadmin или operator)",
                      brief="<префикс>ранг STEAM_0:0:0000000 superadmin",
                      description="Команда, с помощью которой, можно изменить ранг игрока, не заходя на сервер.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def set_rank(self, ctx, client: str, rank: str):
        conn, user = self.pgsql.connect()
        database, gamer = self.mysql.connect()

        client = await self.check_client(ctx, client, gamer)

        if not client:
            return

        data_gamer = await self.get_data_gamer(ctx, client, user, gamer)

        if not data_gamer:
            return

        gamer.execute(f"UPDATE users_steam SET rank = '{rank}' WHERE steamid = '{data_gamer[0]}'")
        database.commit()
        self.logger.info("User with SteamID {} successfully changed rank.".format(data_gamer[0]))
        await ctx.channel.send(embed=await functions.embeds.description("Ранг игрока был изменен.",
                                                                        f"Ранг игрока **{data_gamer[1]}** был изменен "
                                                                        f"на {rank}."))

        self.pgsql.close_conn(conn, user)
        self.mysql.close_conn(database, gamer)

    @commands.command(
        name="купить_ранг",
        help="Данные которые нужны для использования этой команды:"
             "\n<rank>: Название ранга, который вы хотите приобрести (пример: VIP)",
        brief="<префикс>купить_ранг superadmin",
        description="Команда, с помощью которой, можно приобрести ранг на сервере, за обычную валюту.")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def buy_rank(self, ctx, rank: str):
        if rank.lower() != "vip" and rank.lower() != "premium" and rank.lower() != "superadmin":
            await ctx.send(embed=await functions.embeds.description("Ранг не продается.", "Ранг, который вы хотите "
                                                                                          "купить либо не существует,"
                                                                                          "либо не продается."))
            return

        elif rank.lower() == "superadmin":
            await ctx.send(embed=await functions.embeds.description("Нафиг пошел.", "Фу, брось бяку."))
            return

        conn, user = self.pgsql.connect()
        database, gamer = self.mysql.connect()
        user.execute("SELECT * FROM users WHERE \"discordID\" = {}".format(ctx.author.id))
        data_user = user.fetchone()
        if not data_user[6] or data_user[6] == "None":
            await ctx.channel.send(embed=await functions.embeds.description("Игрок не синхронизирован",
                                                                            "Игрок с таким Discord-ом не "
                                                                            "синхронизирован. Введите его SteamID, "
                                                                            "чтобы забанить."))
            return

        gamer.execute("SELECT rank FROM users_steam WHERE steamid = '{}'".format(data_user[6]))
        now_rank = gamer.fetchone()[0]
        if rank == now_rank:
            await ctx.send(embed=await functions.embeds.description("Ранги одинаковы", "Ранг, который вы хотите купить"
                                                                                       "у Вас уже есть."))

        if int(data_user[3]) >= 500000 and rank.lower() == "vip":
            user.execute("UPDATE users SET goldmoney = goldmoney - {} WHERE \"discordID\" = {}".
                         format(500000, ctx.author.id))
            conn.commit()
            gamer.execute(f"UPDATE users_steam SET rank = 'admin' WHERE steamid = '{data_user[6]}'")
            database.commit()
            role = discord.utils.get(ctx.guild.roles, name="VIP")
            await ctx.author.add_roles(role)
            await ctx.send(embed=await functions.embeds.description("Вы купили VIP-ранг.", "Спасибо за приобретение "
                                                                                           "ранга на нешем сервере."
                                                                                           "Желаем Вам приятной игры!"))
        # elif money >= 1000000 and rank.lower() == "premium":
        #     user.execute("UPDATE users SET goldmoney = goldmoney - {} WHERE \"discordID\" = {}".
        #                  format(1000000, ctx.author.id))
        #     conn.commit()
        #     gamer.execute(f"UPDATE users_steam SET rank = 'premium' WHERE steamid = '{steamid}'")
        #     database.commit()
        #     await ctx.send(embed=await functions.embeds.description(ctx.author.mention, buying_premium))
        else:
            await ctx.send(embed=await functions.embeds.description("Недостаточно средств.", "Как говорится, денег нет,"
                                                                                             " но вы держитесь."))

        self.pgsql.close_conn(conn, user)
        self.mysql.close_conn(database, gamer)
