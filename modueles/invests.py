from discord.ext import commands
from functions.database import PgSQLConnection
from functions.database import MySQLConnection


class Invests(commands.Cog, name="Инвистиции"):

    def __init__(self, user):
        self.client = user

        self.pgsql = PgSQLConnection()
        self.mysql = MySQLConnection()

    async def course(self, ctx):
        pass

    @commands.command(name="банк", help="показывает ваше состояние")
    async def bank(self, ctx):
        pass

    @commands.command(name="открыть_счёт", help="открывает счёт в банке")
    async def open_bill(self, ctx):
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
