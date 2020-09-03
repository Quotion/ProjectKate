from discord.ext import commands
from functions.database import PgSQLConnection
from language.treatment_ru import *
import json
import logging


class InfoNotExist(commands.CheckFailure):
    pass


class AddChannels(commands.Cog, name='Добавление каналов'):

    def __init__(self, client):
        self.client = client

        logger = logging.getLogger("add_channels")
        logger.setLevel(logging.INFO)
        self.logger = logger

        self.pgsql = PgSQLConnection()

    def info_exist(self):
        async def predicate(ctx):
            conn, user = self.pgsql.connect()
            user.execute("SELECT promocode FROM promocode WHERE guild_id = %s", [ctx.guild.id])
            info = user.fetchone()[0]

            self.pgsql.close_conn(conn, user)
            if not info:
                raise InfoNotExist
            return True
        return commands.check(predicate)

    @commands.command(name="основной", help="<префикс>основной <хайлайт канала>")
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def main_channel(self, ctx):
        AddChannels.info_exist(self)

        conn, user = self.pgsql.connect()
        guild_id = ctx.guild.id
        user.execute("SELECT promocode FROM promocode WHERE guild_id = %s", [guild_id])
        info = user.fetchone()[0]

        if ctx.message.channel_mentions and len(ctx.message.channel_mentions) == 1:
            info['main'] = ctx.message.channel_mentions[0].id
            await ctx.channel.send(channel_saved.format(ctx.author.mention, ctx.message.channel_mentions[0],
                                                        'основного общения'))
            try:
                user.execute("UPDATE promocode SET info = %s WHERE guild_id = %s", (json.dumps(info), guild_id))
                conn.commit()
                self.logger.info("Channel for main communication was saved.")
            except Exception as error:
                await ctx.channel.send(something_went_wrong)
                self.logger.error(error)

        elif ctx.message.channel_mentions:
            await ctx.channel.send(so_many_channels.format(ctx.author.mention))
        else:
            await ctx.channel.send(not_enough_channels.format(ctx.author.mention, self.client.command_prefix[0]))
            self.logger.info("User entered incorrect data about guild channel: it's empty.")

    @commands.command(name='новости', help="<префикс>новости <хайлайт канала>")
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def news(self, ctx):
        AddChannels.info_exist(self)

        conn, user = self.pgsql.connect()
        guild_id = ctx.guild.id
        user.execute("SELECT promocode FROM promocode WHERE guild_id = %s", [guild_id])
        info = user.fetchone()[0]

        if ctx.message.channel_mentions and len(ctx.message.channel_mentions) == 1:
            info['news'] = ctx.message.channel_mentions[0].id
            await ctx.channel.send(channel_saved.format(ctx.author.mention, ctx.message.channel_mentions[0],
                                                        'новостей'))
            try:
                user.execute("UPDATE promocode SET info = %s WHERE guild_id = %s", (json.dumps(info), guild_id))
                conn.commit()
                self.logger.info("Channel for news was saved.")
            except Exception as error:
                await ctx.channel.send(something_went_wrong)
                self.logger.error(error)

        elif ctx.message.mentions:
            await ctx.channel.send(so_many_channels.format(ctx.author.mention))

        else:
            await ctx.channel.send(not_enough_channels.format(ctx.author.mention, self.client.command_prefix[0]))
            self.logger.info("User entered incorrect data about guild channel: it's empty.")

    @commands.command(name='логи', help="<префикс>логи <хайлайт канала>")
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def log(self, ctx):
        AddChannels.info_exist(self)

        conn, user = self.pgsql.connect()
        guild_id = ctx.guild.id
        user.execute("SELECT promocode FROM promocode WHERE guild_id = %s", [guild_id])
        info = user.fetchone()[0]

        if ctx.message.channel_mentions and len(ctx.message.channel_mentions) == 1:
            info['logging'] = ctx.message.channel_mentions[0].id
            await ctx.channel.send(channel_saved.format(ctx.author.mention, ctx.message.channel_mentions[0],
                                                        'логгирования'))
            try:
                user.execute("UPDATE promocode SET info = %s WHERE guild_id = %s", (json.dumps(info), guild_id))
                conn.commit()
                self.logger.info("Channel for logging was saved.")
            except Exception as error:
                await ctx.channel.send(something_went_wrong)
                self.logger.error(error)

        elif ctx.message.channel_mentions:
            await ctx.channel.send(so_many_channels.format(ctx.author.mention))
        else:
            await ctx.channel.send(not_enough_channels.format(ctx.author.mention, self.client.command_prefix[0]))
            self.logger.info("User entered incorrect data about guild channel: it's empty.")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, InfoNotExist):
            self._correct_info(ctx.guild.id)
            await ctx.channel.send(error_json_info.format(ctx.author.mention))
            self.logger.error("An error occurred while creating the id.")

    def _correct_info(self, guild_id):

        conn, user = self.pgsql.connect()
        user.execute("SELECT promocode FROM promocode WHERE guild_id = {}".format(guild_id))
        info = user.fetchall()
        if not info:
            information = {'main': 0, 'news': 0, 'logging': 0}
            user.execute("INSERT INTO promocode VALUES (%s, %s)", (guild_id, json.dumps(information),))
            conn.commit()

        self.logger.info('The error has been fixed. Guild ID {} was added in JSON table.'.format(guild_id))
