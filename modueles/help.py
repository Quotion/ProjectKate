<<<<<<< HEAD
import discord
from discord.ext import commands
from models import *


class MainCommands(commands.HelpCommand, name="Помощь"):

    def __init__(self, client):
        self.client = client

        logger = logging.getLogger("main_commands")
        logger.setLevel(logging.INFO)

        self.logger = logger

        self.choice_on = False

=======
import discord
from discord.ext import commands
from models import *


class MainCommands(commands.HelpCommand, name="Помощь"):

    def __init__(self, client):
        self.client = client

        logger = logging.getLogger("main_commands")
        logger.setLevel(logging.INFO)

        self.logger = logger

        self.choice_on = False

>>>>>>> 75b13045fc71e61cb736d610ba0be5d6d89e8926
        self.generate_promo.start()