import logging
import random as rd
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

        self.timer = 3600
        self.time = 0
        self.url = "https://www.rbc.ru/crypto/currency/neousd"

        logger = logging.getLogger("invests")
        logger.setLevel(logging.INFO)
        self.logger = logger

    async def __check_course__(self):
        self.time = int(time.time())

        soup = BeautifulSoup(requests.get(self.url).text, features="lxml")
        table = soup.find("div", {"class": "chart__subtitle js-chart-value"})
        course = float(table.text[12:17].replace(' ', '').replace(',', '.'))

        return course

    @commands.command(name="инвест_помощь", help="закрывает и удаляет счет в банке")
    async def invest_help(self, ctx):
        await ctx.send(embed=await invest_help(ctx))

    @commands.command(name="открыть_счёт", help="открывает счёт в банке")
    async def open_bill(self, ctx):
        conn, user = None, None
        try:
            conn, user = self.pgsql.connect()
            user.execute("INSERT INTO bank (discordID, guild_id) VALUES ({}, {})".
                         format(ctx.author.id, ctx.guild.id))
            conn.commit()
        except Exception as error:
            await ctx.send(embed=await description(ctx.author.mention, account_exist))
            self.logger.error(error)
        else:
            await ctx.send(creating_bank_account.format(ctx.author.mention, ctx.author.id))
        finally:
            self.pgsql.close_conn(conn, user)

    @commands.command(name="счёт", help="закрывает и удаляет счет в банке")
    async def bill(self, ctx):
        pass

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

    @commands.command(name="банк", help="показывает ваше состояние")
    async def bank(self, ctx):
        conn, user = None, None
        course = await self.__check_course__()
        try:
            conn, user = self.pgsql.connect()
            user.execute("SELECT SUM(amount) FROM bank")
            amount = user.fetchone()[0]
            await ctx.send(embed=await bank_info(ctx, amount, course))

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
            user.execute("SELECT money FROM users WHERE discordID = {}".
                         format(float(amount) * await self.__check_course__(), ctx.author.id))
            await ctx.send(embed=await description(ctx.author.mention, successful_put))

        except Exception as error:
            self.logger.error(error)
        finally:
            self.pgsql.close_conn(conn, user)

        try:
            conn, user = self.pgsql.connect()
            user.execute("UPDATE bank SET amount = amount + {} WHERE discordID = {}".
                         format(float(amount) * await self.__check_course__(), ctx.author.id))
            await ctx.send(embed=await description(ctx.author.mention, successful_put))

        except Exception as error:
            self.logger.error(error)
        finally:
            self.pgsql.close_conn(conn, user)

    @commands.command(name="снять", help="возвращает вам деньги со счёта")
    async def get_from_bank(self, ctx, *, amount: str):
        pass

    @commands.command(name="ивест_статус", help="возвращает вам деньги со счёта")
    async def invest_status(self, ctx, *, amount: str):
        pass

    @commands.command(name="вложить", help="кладет на счет в банке")
    async def invest(self, ctx, *, amount: str):
        pass

    @commands.command(name="курс", help="кладет на счет в банке")
    async def course(self, ctx):
        course = await self.__check_course__()
        embed = discord.Embed(colour=discord.Colour.default())
        embed.description = f"Нынешний курс банка: {course} ₽."
        await ctx.send(embed=embed)
