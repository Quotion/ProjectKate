from discord.ext import commands
from functions.database import PgSQLConnection, MySQLConnection
from language.treatment_ru import *


class Society(commands.Cog, name="Общественные команды"):
    def __init__(self, client):
        self.client = client

        logger = logging.getLogger("society")
        logger.setLevel(logging.INFO)

        self.logger = logger

        self.mysql = MySQLConnection()
        self.pgsql = PgSQLConnection()

    @commands.command(name="хит", help="<префикс>хит <Discord>")
    async def hit(self, ctx):
        pass
