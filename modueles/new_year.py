import logging
from discord.ext import commands
import functions.database


class New_Year(commands.Cog, name="Новогодний модуль"):
    def __init__(self, bot):
        self.client = bot

        self.pgsql = functions.database.PgSQLConnection()

        logger = logging.getLogger("new_year")
        logger.setLevel(logging.INFO)

        self.logger = logger

    @commands.command(name="кинуть_снежок", help="кидает снежок в игрока")
    async def slap(self):
        pass

    @commands.command(name="снеговик", help="выведет вашу аватарку")
    async def snowman(self):
        pass

