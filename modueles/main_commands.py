import datetime
import logging
import os

import discord
from discord.ext import commands

import functions.database
import functions.helper
from functions.create_plot import create_figure
from language.treatment_ru import *


class MainCommands(commands.Cog, name="Основные команды"):

    def __init__(self, client):
        self.client = client

        logger = logging.getLogger("main_commands")
        logger.setLevel(logging.INFO)

        self.logger = logger

        self.mysql = functions.database.MySQLConnection()
        self.pgsql = functions.database.PgSQLConnection()

    async def profile_exist(self, ctx):
        conn, user = self.pgsql.connect()
        try:
            user.execute('SELECT * FROM users WHERE "discordID" = %s', [ctx.author.id])
            var = user.fetchall()[0]
            self.pgsql.close_conn(conn, user)
            return False
        except IndexError as error:
            self.logger.error(error)

            now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))

            try:
                user.execute(
                    'INSERT INTO users ("discordID", rating, money, goldMoney, "chanceRol", "dateRol", nick) '
                    'VALUES(%s, %s, %s, %s, %s, %s, %s)',
                    (ctx.author.id, 0, 0, 0, 1, now.day, ctx.author.name))
                conn.commit()
                await ctx.send(profile_create.format(ctx.author.mention))
                self.logger.info("Profile of {} successfully created.".format(ctx.author.name))
            except Exception as error:
                await ctx.send(something_went_wrong)
                self.logger.info(error)

            self.pgsql.close_conn(conn, user)
            return True

    @commands.command(name='профиль', help="полна информация по вашему профилю")
    async def profile(self, ctx):
        if await MainCommands.profile_exist(self, ctx):
            return

        conn, user = self.pgsql.connect()
        data = None

        user.execute("SELECT bank_info FROM info WHERE guild_id = {}".format(ctx.guild.id))
        name_of_currency = user.fetchone()[0]['char_of_currency']

        if len(ctx.message.content.split()) == 2 and len(ctx.message.mentions) == 1:
            user.execute('SELECT * FROM users WHERE "discordID" = %s', [ctx.message.mentions[0].id])
            user_ctx = self.client.get_user(ctx.message.mentions[0].id)
        elif len(ctx.message.content.split()) == 1:
            user.execute('SELECT * FROM users WHERE "discordID" = %s', [ctx.author.id])
            user_ctx = ctx.author
        else:
            await ctx.send(something_went_wrong)
            return
        try:
            data = user.fetchall()[0]
        except IndexError as error:
            self.logger.error(error)
        try:
            if data[7] and data[7] != "None":
                conn_mysql, user_mysql = self.mysql.connect()
                user_mysql.execute("SELECT * FROM users_steam WHERE steamid = '{}'".format(data[7]))
                steam = user_mysql.fetchall()[0]

                all_data = dict(rating=data[1], money=data[2], gold_money=data[3], steamid=data[7], nick=steam[1],
                                rank=steam[2], name_of_currency=name_of_currency)

                self.mysql.close_conn(conn_mysql, user_mysql)
            else:
                all_data = dict(rating=data[1], money=data[2], gold_money=data[3], steamid='Не синхронизирован',
                                nick='Не синхронизирован', rank='Не синхронизирован',
                                name_of_currency=name_of_currency)

            await ctx.send(embed=await functions.embeds.profile(all_data,
                                                                name=user_ctx.name,
                                                                icon_url=ctx.guild.icon_url,
                                                                avatar_url=user_ctx.avatar_url,
                                                                mention=user_ctx.mention,
                                                                guild_name=ctx.guild.name))
        except TypeError as error:
            self.logger.error(error)

        finally:
            self.pgsql.close_conn(conn, user)

    @commands.command(name='удали', help="удаляет определенное количество сообщений")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def delete(self, ctx):
        conn, user = self.pgsql.connect()
        guild_id = ctx.guild.id
        user.execute("SELECT info FROM info WHERE guild_id = %s", [guild_id])
        info = user.fetchone()[0]

        msg = ctx.message.content.split()
        if not msg[1].isdigit():
            await ctx.send(not_a_number.format(ctx.author.mention, self.client.command_prefix))
            self.logger.info("{} entered not a number.".format(ctx.author.name))
            return

        await ctx.channel.purge(limit=int(msg[1]) + 1)
        if info['logging']:
            channel = self.client.get_channel(info['logging'])
            await channel.send(embed=await functions.embeds.purge(ctx, int(msg[1])))

    @commands.command(name='рулетка', help="рандомно даёт приз один раз в сутки")
    async def roulette(self, ctx):
        if await MainCommands.profile_exist(self, ctx):
            return

        conn, user = self.pgsql.connect()

        user.execute("SELECT bank_info FROM info WHERE guild_id = {}".format(ctx.guild.id))
        name_of_currency = user.fetchone()[0]['char_of_currency']

        user.execute('SELECT "dateRol" FROM users WHERE "discordID" = {}'.format(ctx.author.id))
        date = user.fetchone()[0]

        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
        if date == now.day:
            await ctx.send(roulette_ended.format(ctx.author.mention))
            return

        user.execute('UPDATE users SET "dateRol" = {} WHERE "discordID" = {}'.format(now.day, ctx.author.id))
        conn.commit()

        win, thing = await functions.helper.random_win()

        if thing == 0:
            user.execute('UPDATE users SET money = money + {} WHERE "discordID" = {}'.format(win, ctx.author.id))
            conn.commit()
            await ctx.send(embed=await functions.embeds.roulette(ctx, win, name_of_currency.title()))
        elif thing == 1:
            user.execute('UPDATE users SET goldMoney = goldMoney + {} WHERE "discordID" = {}'.
                         format(win, ctx.author.id))
            conn.commit()
            await ctx.send(embed=await functions.embeds.roulette(ctx, win, f"Зол. {name_of_currency.title()}"))
        else:
            user.execute('UPDATE users SET rating = rating + {} WHERE "discordID" = {}'.format(win, ctx.author.id))
            conn.commit()
            await ctx.send(embed=await functions.embeds.roulette(ctx, win, "ретинга"))

        self.pgsql.close_conn(conn, user)

    @commands.command(name='топ', help="вывод топ всех людей по рейтингу")
    async def top(self, ctx):
        conn, user = None, None

        try:
            conn, user = self.pgsql.connect()

            user.execute("SELECT \"discordID\", rating FROM users ORDER BY rating DESC LIMIT 5")
            data = user.fetchall()

            embed = discord.Embed(colour=discord.Colour.dark_gold())

            embed.description = "Топ пользователей по рейтингу."
            for info, count in zip(data, range(0, len(data))):
                name = None
                try:
                    name = self.client.get_user(int(info[0])).name
                except Exception as error:
                    self.logger.error(error)
                    name = "no data"
                finally:
                    embed.add_field(name=f"{count + 1} место",
                                    value=f"__{name}__: **{info[1]}** рейтинга",
                                    inline=False)

            await ctx.send(embed=embed)

        except Exception as error:
            self.logger.error(error)
        finally:
            self.pgsql.close_conn(conn, user)

    @commands.command(name='продать', help="продает рейтинг за ВС (1:1000)")
    async def sale(self, ctx):
        if await MainCommands.profile_exist(self, ctx):
            return

        conn, user = self.pgsql.connect()

        user.execute("SELECT bank_info FROM info WHERE guild_id = {}".format(ctx.guild.id))
        name_of_currency = user.fetchone()[0]['char_of_currency']

        msg = ctx.message.content.split()

        if len(msg) < 2:
            await ctx.send(just_a_command.format(ctx.author.mention, self.client.command_prefix))
            self.logger.info("{} entered one word.".format(ctx.author.name))
            return

        if not msg[1].isdigit():
            await ctx.send(not_a_number.format(ctx.author.mention, self.client.command_prefix))
            self.logger.info("{} entered not a number.".format(ctx.author.name))
            return

        conn, user = self.pgsql.connect()

        user.execute('SELECT rating FROM users WHERE "discordID" = {}'.format(ctx.author.id))
        rating = int(user.fetchone()[0])
        msg[1] = int(msg[1])

        if rating < msg[1] or rating <= 0:
            await ctx.send(not_correct.format(ctx.author.mention, "рейтинга"))
            self.logger.info("{} entered a number more than have rating.")
            self.pgsql.close_conn(conn, user)
            return

        user.execute('UPDATE users SET rating = rating - {}, money = money + {} WHERE "discordID" = {}'.
                     format(msg[1], msg[1] * 1000, ctx.author.id))
        conn.commit()

        await ctx.send(rating_sale.format(ctx.author.mention, msg[1] * 1000, name_of_currency.title(), 1000))

        self.pgsql.close_conn(conn, user)

    @commands.command(name='обмен', help="меняет обычные ВС на золотую ВС")
    async def swap(self, ctx):
        if await MainCommands.profile_exist(self, ctx):
            return

        msg = ctx.message.content.split()
        if len(msg) < 2:
            await ctx.send(just_a_command.format(ctx.author.mention, self.client.command_prefix))
            self.logger.info("{} entered one word.".format(ctx.author.name))
            return

        if not msg[1].isdigit():
            await ctx.send(not_a_number.format(ctx.author.mention, self.client.command_prefix))
            self.logger.info("{} entered not a number.".format(ctx.author.name))
            return

        conn, user = self.pgsql.connect()

        user.execute('SELECT money FROM users WHERE "discordID" = {}'.format(ctx.author.id))
        revers = int(user.fetchone()[0])
        msg[1] = int(msg[1])

        if revers < msg[1]:
            await ctx.send(more_than_have.format(ctx.author.mention, "реверсивок"))
            self.logger.info("{} entered a number more than have rating.")
            self.pgsql.close_conn(conn, user)
            return

        user.execute('UPDATE users SET money = money - {} WHERE "discordID" = {}'.
                     format(int(msg[1]), ctx.author.id))
        conn.commit()

        user.execute('UPDATE users SET goldMoney = goldMoney + {} WHERE "discordID" = {}'.
                     format(int(msg[1] / 4), ctx.author.id))
        conn.commit()

        await ctx.send(embed=await functions.embeds.swap(ctx, int(msg[1] / 4), msg[1], swaps))

    @commands.command(name="статистика", help="основная команда для статистики")
    async def static(self, ctx):
        conn, user = self.pgsql.connect()
        database, gamer = self.mysql.connect()
        user.execute("SELECT steamid FROM users WHERE \"discordID\" = %s", [ctx.author.id])

        steamid = None

        try:
            steamid = user.fetchone()[0]
        except IndexError as error:
            self.logger.error(error)
            await ctx.send(embed=await functions.embeds.description(ctx.author.mention, you_not_synchronized))

        if steamid != "None" and steamid:
            gamer.execute("SELECT * FROM users_steam WHERE steamid = %s", [steamid])
            data = gamer.fetchall()[0]

            labels, all_time = await create_figure(data)

            if not labels:
                await ctx.send(embed=await functions.embeds.description(ctx.author.mention, for_statistics))
                return

            image = open("statistics.png", 'rb')
            await ctx.send(f"{ctx.author.mention}, вы провели за пултом {all_time}"
                           f"\nВот список составов, в которых вы находились:\n```" +
                           '\n'.join([x for x in labels]) + "```"
                           "\nГрафик ниже предоставит вам дополнительную информацию:",
                           file=discord.File(fp=image, filename="statistics.png"))
            image.close()
        else:
            await ctx.send(embed=await functions.embeds.description(ctx.author.mention, you_not_synchronized))
        try:
            os.remove("statistics.png")
        except PermissionError as error:
            self.logger.error(error)

    @commands.command(name="сервер", help="выводит информацию о сервере")
    async def server_info(self, ctx):
        embed = await functions.embeds.server_info(ctx.guild)
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(missing_permission.format(ctx.author.mention))
            self.logger.error(error)
        elif isinstance(error, commands.CommandNotFound):
            await ctx.send(command_not_found.format(ctx.author.mention, ctx.message.content))
        else:
            self.logger.error(error)
