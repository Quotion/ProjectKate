import logging
from discord.ext import commands
from language.treatment_ru import *
from functions.database import PgSQLConnection
from functions.database import MySQLConnection


class Invests(commands.Cog, name="Инвистиции"):

    def __init__(self, user):
        self.client = user

        self.pgsql = PgSQLConnection()
        self.mysql = MySQLConnection()

        logger = logging.getLogger("invests")
        logger.setLevel(logging.INFO)
        self.logger = logger

    @commands.command(name="открыть_счёт", help="открывает счёт в банке")
    async def open_bill(self, ctx):
        conn, user = None, None
        try:
            conn, user = self.pgsql.connect()

            user.execute("INSERT INTO bank (discordID) VALUES ({})".format(ctx.author.id))
            conn.commit()
        except Exception as error:
            self.logger.error(error)
        else:
            user.execute("SELECT accountID FROM bank WHERE discordID = {}".format(ctx.author.id))
            await ctx.send(creating_bank_account.format(ctx.author.mention, user.fetchone()[0]))
        finally:
            self.pgsql.close_conn(conn, user)

    @commands.command(name="банк", help="показывает ваше состояние")
    async def bank(self, ctx):
        pass

    @commands.command(name="закрыть_счёт", help="закрывает и удаляет счет в банке")
    async def close_bill(self, ctx):
        pass

    @commands.command(name="положить", help="кладет на счет в банке")
    async def put_in_bank(self, ctx):
        pass

    @commands.command(name="снять", help="возвращает вам деньги со счёта")
    async def get_from_bank(self, ctx):
        pass

    @commands.command(name="вложить", help="кладет на счет в банке")
    async def invest(self, ctx):
        pass

    @commands.command(name="курс", help="кладет на счет в банке")
    async def course(self, ctx):
        pass
