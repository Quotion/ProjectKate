import logging
import json
import requests
from bs4 import BeautifulSoup
from discord.ext import commands
from functions.embeds import *
from language.treatment_ru import *
from functions.database import PgSQLConnection
from functions.database import MySQLConnection


class Invests(commands.Cog, name="Инвистиции"):

    def __init__(self, user):
        self.client = user

        self.pgsql = PgSQLConnection()
        self.mysql = MySQLConnection()

        self.url = "https://www.rbc.ru/crypto/currency/neousd"

        logger = logging.getLogger("invests")
        logger.setLevel(logging.INFO)
        self.logger = logger

    def __check_course__(self):
        self.time = int(time.time())

        soup = BeautifulSoup(requests.get(self.url).text, features="lxml")

        table = soup.find("div", {"class": "chart__subtitle js-chart-value"})
        course = float(table.text[10:17].replace(' ', '').replace(',', '.'))

        return course

    @commands.command(name="инвест_помощь", help="закрывает и удаляет счет в банке")
    async def invest_help(self, ctx):
        await ctx.send(embed=await invest_help(ctx))

    @commands.command(name="имя_банка", help="изменяет название банка")
    @commands.has_permissions(administrator=True)
    async def name_bank(self, ctx, *, name: str):
        conn, user, bank = None, None, None
        try:
            conn, user = self.pgsql.connect()
            user.execute("SELECT bank_info FROM info WHERE guild_id = {}".format(ctx.guild.id))
            bank = user.fetchone()[0]
        except Exception as error:
            self.logger.error(error)
        finally:
            self.pgsql.close_conn(conn, user)

        bank['name'] = name

        try:
            conn, user = self.pgsql.connect()
            user.execute('UPDATE info SET bank_info = %s WHERE guild_id = %s', (json.dumps(bank), ctx.guild.id))
            conn.commit()
        except Exception as error:
            self.logger.error(error)
        else:
            await ctx.send(embed=await description(name, save_name_bank))
        finally:
            self.pgsql.close_conn(conn, user)

    @commands.command(name="имя_валюты", help="изменяет название валюты")
    @commands.has_permissions(administrator=True)
    async def name_currency(self, ctx, *, name: str):
        conn, user, bank = None, None, None
        try:
            conn, user = self.pgsql.connect()
            user.execute("SELECT bank_info FROM info WHERE guild_id = {}".format(ctx.guild.id))
            bank = user.fetchone()[0]
        except Exception as error:
            self.logger.error(error)
        finally:
            self.pgsql.close_conn(conn, user)

        bank['char_of_currency'] = name

        try:
            conn, user = self.pgsql.connect()
            user.execute('UPDATE info SET bank_info = %s WHERE guild_id = %s', (json.dumps(bank), ctx.guild.id))
            conn.commit()
        except Exception as error:
            self.logger.error(error)
        else:
            await ctx.send(embed=await description(name, save_name_currency))
        finally:
            self.pgsql.close_conn(conn, user)

    @commands.command(name="открыть_счёт", help="открывает счёт в банке")
    async def open_bill(self, ctx):
        conn, user = None, None
        try:
            conn, user = self.pgsql.connect()
            user.execute("INSERT INTO bank VALUES ({}, {}, {}, {})".format(ctx.author.id, ctx.guild.id, 0,
                                                                           int(time.time())))
            conn.commit()
        except Exception as error:
            await ctx.send(embed=await description(ctx.author.mention, account_exist))
            self.logger.error(error)
        else:
            await ctx.send(creating_bank_account.format(ctx.author.mention, ctx.author.id))
        finally:
            self.pgsql.close_conn(conn, user)

    @commands.command(name="счёт", help="выводит информацию по счёту")
    async def bill(self, ctx):
        conn, user, info, bank = None, None, None, None
        try:
            conn, user = self.pgsql.connect()
            user.execute("SELECT * FROM bank WHERE discordID = {}".format(ctx.author.id))
            info = user.fetchall()[0]
            user.execute("SELECT bank_info FROM info WHERE guild_id = {}".format(ctx.guild.id))
            bank = user.fetchone()[0]
        except TypeError as error:
            await ctx.send(account_not_exist.format(ctx.author.mention))
            self.logger.error(error)
        except Exception as error:
            await ctx.send(something_went_wrong)
            self.logger.error(error)
        else:
            await ctx.send(embed=await bill(ctx, info, bank))
        finally:
            self.pgsql.close_conn(conn, user)

    @commands.command(name="закрыть_счёт", help="закрывает и удаляет счет в банке")
    async def close_bill(self, ctx):
        conn, user = None, None
        try:
            conn, user = self.pgsql.connect()
            user.execute("DELETE FROM bank WHERE discordID = {}".format(ctx.author.id))
            conn.commit()
        except TypeError as error:
            await ctx.send(embed=await description(ctx.author.mention, nothing_to_close))
            self.logger.error(error)
        except Exception as error:
            await ctx.send(something_went_wrong)
            self.logger.error(error)
        else:
            await ctx.send(delete_bank_account.format(ctx.author.mention, ctx.author.id))
        finally:
            self.pgsql.close_conn(conn, user)

    @commands.command(name="банк", help="показывает информацию по банку")
    async def bank(self, ctx):
        conn, user, all_amount = None, None, .0
        try:
            conn, user = self.pgsql.connect()
            user.execute("SELECT SUM(amount) FROM bank WHERE guild_id = {}".format(ctx.guild.id))
            all_amount = user.fetchone()[0]
        except Exception as error:
            self.logger.error(error)
        finally:
            self.pgsql.close_conn(conn, user)

        try:

            conn, user = self.pgsql.connect()
            user.execute("SELECT bank_info FROM info WHERE guild_id = {}".format(ctx.guild.id))
            bank = user.fetchone()[0]

            course = self.__check_course__()

            await ctx.send(embed=await bank_info(ctx, all_amount, course, bank['name']))
        except Exception as error:
            self.logger.error(error)
        finally:
            self.pgsql.close_conn(conn, user)

    @commands.command(name="положить", help="кладет на счет в банке")
    async def put_in_bank(self, ctx, *, amount: str):

        if not amount.isdigit():
            await ctx.send(not_a_number.format(ctx.author.mention, self.client.command_prefix))
            return

        conn, user = None, None

        try:
            conn, user = self.pgsql.connect()
            user.execute("SELECT money FROM users WHERE \"discordID\" = {}".format(ctx.author.id))
            money = user.fetchone()[0]
            user.execute("SELECT bank_info FROM info WHERE guild_id = {}".format(ctx.guild.id))
            info = user.fetchone()

            if float(money) < float(amount):
                await ctx.send(not_enough_money.format(ctx.author.mention, info['name_of_currency']))
                return
        except Exception as error:
            self.logger.error(error)
        finally:
            self.pgsql.close_conn(conn, user)

        try:
            conn, user = self.pgsql.connect()
            user.execute("UPDATE bank SET amount = amount + %s WHERE discordID = %s;"
                         "UPDATE users SET money = money - %s WHERE \"discordID\" = %s;",
                         ((float(amount) * self.__check_course__()), ctx.author.id, amount, ctx.author.id))
            conn.commit()
            await ctx.send(embed=await description(ctx.author.mention, successful_put))

        except Exception as error:
            self.logger.error(error)
            await ctx.send(something_went_wrong)
        finally:
            self.pgsql.close_conn(conn, user)

    @commands.command(name="снять", help="возвращает вам деньги со счёта")
    async def get_from_bank(self, ctx, *, amount: str):

        if not amount.isdigit():
            await ctx.send(not_a_number.format(ctx.author.mention, self.client.command_prefix))
            return

        conn, user = None, None

        try:
            conn, user = self.pgsql.connect()
            user.execute("SELECT amount FROM bank WHERE \"discordID\" = {}".format(ctx.author.id))
            real_amount = user.fetchone()[0]

            if float(real_amount) < float(amount):
                await ctx.send(not_enough_money.format(ctx.author.mention, "NEO"))
                return
        except Exception as error:
            self.logger.error(error)
        finally:
            self.pgsql.close_conn(conn, user)

        try:
            conn, user = self.pgsql.connect()
            user.execute("UPDATE bank SET amount = amount - %s WHERE discordID = %s;"
                         "UPDATE users SET money = money + %s WHERE \"discordID\" = %s;",
                         (float(amount), ctx.author.id, int(float(amount) / self.__check_course__()), ctx.author.id))
            conn.commit()
            await ctx.send(embed=await description(ctx.author.mention, successful_get))

        except Exception as error:
            self.logger.error(error)
            await ctx.send(something_went_wrong)
        finally:
            self.pgsql.close_conn(conn, user)

    @commands.command(name="перевести", help="переводить на счёт")
    async def get_from_bank(self, ctx, *, bill_id: str, amount: str):
        pass

    @commands.command(name="инвест_статус", help="возвращает вам деньги со счёта")
    async def invest_status(self, ctx, *, amount: str):
        pass

    @commands.command(name="вложить", help="кладет на счет в банке")
    async def invest(self, ctx, *, amount: str):
        pass

    @commands.command(name="курс", help="кладет на счет в банке")
    async def course(self, ctx):
        course = self.__check_course__()
        embed = discord.Embed(colour=discord.Colour.default())
        embed.description = f"Нынешний курс банка: {course} ₽."
        await ctx.send(embed=embed)
