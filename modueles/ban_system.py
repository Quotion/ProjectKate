from discord.ext import commands
from functions.database import PgSQLConnection, MySQLConnection
import functions
import datetime
import logging
from language.treatment_ru import *


class Ban(commands.Cog, name="Система банов"):

    def __init__(self, client):
        self.client = client

        logger = logging.getLogger("ban")
        logger.setLevel(logging.INFO)

        self.logger = logger

        self.mysql = MySQLConnection()
        self.pgsql = PgSQLConnection()

    def get_all_steamid(self):
        conn, user = self.mysql.connect()
        user.execute("SELECT steamid FROM users_steam")
        ids = [x[0] for x in user.fetchall()]
        self.mysql.close_conn(conn, user)
        return ids

    def get_all_discordid(self):
        conn, user = self.pgsql.connect()
        user.execute("SELECT \"discordID\" FROM users")
        ids = [x[0] for x in user.fetchall()]
        self.pgsql.close_conn(conn, user)
        return ids

    @commands.command(name='бан', help="банит игрока")
    @commands.has_permissions(administrator=True)
    async def ban(self, ctx):
        message = ctx.message.content.split()
        steamids = self.get_all_steamid()
        discordids = self.get_all_discordid()

        conn, user = self.pgsql.connect()
        database, gamer = self.mysql.connect()

        if len(message) < 3:
            self.logger.error("Message for ban entered incorrect.")
            await ctx.channel.send(embed=await functions.embeds.description(ctx.author.mention, wrong_ban_data))
            return

        if not message[2].isdigit():
            self.logger.error("Number minutes of ban entered incorrect.")
            await ctx.channel.send(embed=await functions.embeds.description(ctx.author.mention, time_not_right))
            return

        if ctx.message.mentions:
            if ctx.message.mentions[0].id in discordids:
                pass
            elif not message[1].upper() in steamids:
                self.logger.error("SteamID or DiscordID for ban not in BD.")
                await ctx.channel.send(embed=await functions.embeds.description(ctx.author.mention, steamid_not_exist))
                return

        time_ban = int(datetime.datetime.today().timestamp())
        time_unban = int(message[2]) * 60 + int(datetime.datetime.today().timestamp())

        if len(message) == 3 and message[1].upper() in steamids:
            steamid = message[1].upper()
            gamer.execute(f"SELECT ban FROM users_steam WHERE steamid = '{steamid}'")
            ban = gamer.fetchone()[0]
            if ban != 1:
                self.logger.info(f'{ctx.author.name} banned {steamid} for {(time_unban - time_ban) // 60} '
                                 f'minutes.')
                gamer.execute(f"UPDATE users_steam SET ban_reason = 'reason', ban_admin = '{ctx.author.name}', "
                              f"ban_date = {time_ban}, unban_date = {time_unban} WHERE steamid = '{steamid}'")
                database.commit()
                await ctx.channel.send(embed=await functions.embeds.ban_message(ban_message, ctx.author.mention,
                                                                                steamid, (time_unban - time_ban)
                                                                                // 60, "reason"))
            else:
                await ctx.channel.send(embed=await functions.embeds.description(
                    ctx.author.mention, already_in_ban))

        elif message[1].upper() in steamids:
            steamid = message[1].upper()
            gamer.execute(f"SELECT ban FROM users_steam WHERE steamid = '{steamid}'")
            ban = gamer.fetchone()[0]
            if ban != 1:
                reason = ""
                for item in message[3:len(message)]:
                    reason += item
                    reason += ' '
                reason = reason[0:len(reason) - 1]
                self.logger.info(f'{ctx.author.name} banned {steamid} for {(time_unban - time_ban) // 60} '
                                 f'minutes because "{reason}".')
                gamer.execute(f"UPDATE users_steam SET ban_reason = 'reason', ban_admin = '{ctx.author.name}', "
                              f"ban_date = {time_ban}, unban_date = {time_unban} WHERE steamid = '{steamid}'")
                database.commit()
                await ctx.channel.send(embed=await functions.embeds.ban_message(ban_message, ctx.author.mention,
                                                                                steamid, (time_unban - time_ban)
                                                                                // 60, reason))
            else:
                await ctx.channel.send(embed=await functions.embeds.description(
                    ctx.author.mention, already_in_ban))

        if len(message) == 3 and ctx.message.mentions[0].id in discordids:
            discordid = ctx.message.mentions[0].id
            user.execute(f"SELECT steamid FROM users WHERE \"discordID\" = {discordid}")
            steamid = user.fetchone()[0]
            if steamid == "None":
                await ctx.channel.send(not_synchronized.format(ctx.author.mention,
                                                               self.client.get_user(int(discordid)).mention))
                return
            gamer.execute(f"SELECT ban FROM users_steam WHERE steamid = '{steamid}'")
            ban = gamer.fetchone()[0]
            if ban != 1:
                self.logger.info(f'{ctx.author.name} banned {steamid} for {(time_unban - time_ban) // 60} '
                                 f'minutes.')
                gamer.execute(f"UPDATE users_steam SET ban_reason = 'reason', ban_admin = '{ctx.author.name}', "
                              f"ban_date = {time_ban}, unban_date = {time_unban} WHERE steamid = '{steamid}'")
                database.commit()
                await ctx.channel.send(embed=await functions.embeds.ban_message(ban_message, ctx.author.mention,
                                                                                self.client.get_user(int(discordid))
                                                                                .mention,
                                                                                (time_unban - time_ban) // 60,
                                                                                "reason"))
            else:
                await ctx.channel.send(embed=await functions.embeds.description(
                    ctx.author.mention, already_in_ban))

        elif ctx.message.mentions[0].id in discordids:
            discordid = ctx.message.mentions[0].id
            user.execute(f"SELECT steamid FROM users WHERE \"discordID\" = {discordid}")
            steamid = user.fetchone()[0]
            if steamid == "None":
                await ctx.channel.send(not_synchronized.format(ctx.author.mention,
                                                               self.client.get_user(int(discordid)).mention))
                return
            gamer.execute(f"SELECT ban FROM users_steam WHERE steamid = '{steamid}'")
            ban = gamer.fetchone()[0]
            if ban != 1:
                reason = ""
                for item in message[3:len(message)]:
                    reason += item
                    reason += ' '
                reason = reason[0:len(reason) - 1]
                self.logger.info(f'{ctx.author.name} banned {steamid} for {(time_unban - time_ban) // 60} '
                                 f'minutes because {reason}.')
                gamer.execute(f"UPDATE users_steam SET ban_reason = '{reason}', ban_admin = '{ctx.author.name}', "
                              f"ban_date = {time_ban}, unban_date = {time_unban} WHERE steamid = '{steamid}'")
                database.commit()
                await ctx.channel.send(embed=await functions.embeds.ban_message(ban_message, ctx.author.mention,
                                                                                self.client.get_user(int(discordid))
                                                                                .mention,
                                                                                (time_unban - time_ban) // 60,
                                                                                reason))
            else:
                await ctx.channel.send(embed=await functions.embeds.description(
                    ctx.author.mention, already_in_ban))

        self.pgsql.close_conn(conn, user)
        self.mysql.close_conn(database, gamer)

    @commands.command(name='разбан', help="разбанивает игрока")
    @commands.has_permissions(administrator=True)
    async def unban(self, ctx):

        try:

            message = ctx.message.content.split()
            steamids = self.get_all_steamid()
            discordids = self.get_all_discordid()

            conn, user = self.pgsql.connect()
            database, gamer = self.mysql.connect()

            now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))

            if ctx.message.mentions:
                if ctx.message.mentions[0].id in discordids:
                    pass
                elif not message[1].upper() in steamids:
                    self.logger.error("SteamID or DiscordID for ban not in BD.")
                    await ctx.channel.send(
                        embed=await functions.embeds.description(ctx.author.mention, steamid_not_exist))
                    return

            if message[1].upper() in steamids:
                steamid = message[1].upper()
                gamer.execute(f"UPDATE users_steam SET ban = 1, ban_reason = 'None', ban_admin = 'None', "
                              f"ban_date = 'None', unban_date = 'None' WHERE steamid = '{steamid}'")
                database.commit()
                self.logger.info("User with SteamID {} successfully unbaned.".format(steamid))
                await ctx.channel.send(
                    unban_message.format(ctx.author.mention, steamid, now.strftime('%H:%M %d.%m.%Y')))

            elif ctx.message.mentions[0].id in discordids:
                discordid = ctx.message.mentions[0].id
                user.execute(f"SELECT steamid FROM users WHERE \"discordID\" = {discordid}")
                steamid = user.fetchone()[0]
                if steamid == "None":
                    await ctx.channel.send(not_synchronized.format(ctx.author.mention,
                                                                   self.client.get_user(int(discordid)).mention))
                    return
                gamer.execute(f"UPDATE users_steam SET ban = 1, ban_reason = 'None', ban_admin = 'None', "
                              f"ban_date = 'None', unban_date = 'None' WHERE steamid = '{steamid}'")
                database.commit()
                self.logger.info("User with SteamID {} successfully unbaned.".format(steamid))
                await ctx.channel.send(
                    unban_message.format(ctx.author.mention, self.client.get_user(int(discordid)).mention,
                                         now.strftime('%H:%M %d.%m.%Y')))

            else:
                await ctx.channel.send(something_went_wrong)

            self.pgsql.close_conn(conn, user)
            self.mysql.close_conn(database, gamer)

        except Exception as error:
            self.logger.error(error)

    @commands.command(name='проверь', help="проверяет находится ли игрок в бане")
    async def check_ban(self, ctx):

        message = ctx.message.content.split()
        steamids = self.get_all_steamid()
        discordids = self.get_all_discordid()

        conn, user = self.pgsql.connect()
        database, gamer = self.mysql.connect()

        if ctx.message.mentions:
            if ctx.message.mentions[0].id in discordids:
                pass
            elif not message[1].upper() in steamids:
                self.logger.error("SteamID or DiscordID for ban not in BD.")
                await ctx.channel.send(
                    embed=await functions.embeds.description(ctx.author.mention, steamid_not_exist))
                return

        if message[1].upper() in steamids:
            steamid = message[1].upper()
            gamer.execute(f"SELECT * FROM users_steam WHERE steamid = '{steamid}'")
            ban = gamer.fetchall()[0]
            if not str(ban[3]).isdigit():
                gamer.execute(f"UPDATE users_steam SET ban = 0 WHERE steamid = '{steamid}'")
                database.commit()
                await ctx.channel.send(successful_find.format(ctx.author.mention))
            else:
                if ban[3] == 0 and (not ban[4] or ban[4] == "None"):
                    await ctx.channel.send(not_in_ban.format(ctx.author.mention, steamid))
                else:
                    await ctx.channel.send(embed=await functions.embeds.check_ban(ban))

        elif ctx.message.mentions[0].id in discordids:
            discordid = ctx.message.mentions[0].id
            user.execute(f"SELECT steamid FROM users WHERE \"discordID\" = {discordid}")
            steamid = user.fetchone()[0]
            if steamid == "None":
                await ctx.channel.send(not_synchronized.format(ctx.author.mention,
                                                               self.client.get_user(discordid).mention))
                return
            gamer.execute(f"SELECT * FROM users_steam WHERE steamid = '{steamid}'")
            ban = gamer.fetchall()[0]
            if not str(ban[3]).isdigit():
                gamer.execute(f"UPDATE users_steam SET ban = 0 WHERE steamid = '{steamid}'")
                database.commit()
                await ctx.channel.send(successful_find.format(ctx.author.mention))
            else:
                if ban[3] == 0 and (not ban[4] or ban[4] == "None"):
                    await ctx.channel.send(not_in_ban.format(ctx.author.mention,
                                                             self.client.get_user(discordid).mention))
                else:
                    await ctx.channel.send(embed=await functions.embeds.discord_check_ban(ban, self.client.
                                                                                          get_user(discordid).
                                                                                          name))

        self.pgsql.close_conn(conn, user)
        self.mysql.close_conn(database, gamer)

    @commands.command(name='синхр', help="синхронизирует GMod и discord")
    async def sync(self, ctx):

        message = ctx.message.content.split()

        conn, user = self.pgsql.connect()
        database, gamer = self.mysql.connect()

        try:
            user.execute("SELECT * FROM users WHERE \"discordID\" = {}".format(ctx.author.id))
            var = user.fetchone()[0]
        except TypeError:
            await ctx.send(account_not_exist.format(ctx.author.mention, self.client.command_prefix[0]))
        except Exception as error:
            await ctx.send(something_went_wrong)
            self.logger.error(error)

        if len(message) < 2:
            await ctx.channel.send("{}, SteamID.".format(ctx.author.mention))
            return

        gamer.execute(f"SELECT * FROM users_steam WHERE steamid = '{message[1].upper()}'")
        k = gamer.fetchone()

        if not k:
            await ctx.channel.send(steamid_not_in_bd)
            return

        await ctx.channel.send(successful_added.format(ctx.author.mention))
        user.execute(f"UPDATE users SET steamid = '{message[1]}' WHERE \"discordID\" = '{ctx.author.id}'")
        conn.commit()

        self.pgsql.close_conn(conn, user)
        self.mysql.close_conn(database, gamer)

    @commands.command(name="ранг", help="ставит ранг определенному игроку")
    @commands.has_permissions(administrator=True)
    async def set_rank(self, ctx):
        try:

            message = ctx.message.content.split()

            if len(message) < 3:
                await ctx.channel.send(embed=await functions.embeds.description(ctx.author.mention, len_of_command))

            steamids = self.get_all_steamid()
            discordids = self.get_all_discordid()

            conn, user = self.pgsql.connect()
            database, gamer = self.mysql.connect()

            if ctx.message.mentions:
                if ctx.message.mentions[0].id in discordids:
                    pass
                elif not message[1].upper() in steamids:
                    self.logger.error("SteamID or DiscordID for ban not in BD.")
                    await ctx.channel.send(
                        embed=await functions.embeds.description(ctx.author.mention, steamid_not_exist))
                    return
            else:
                await ctx.channel.send(embed=await functions.embeds.description(ctx.author.mention, not_highlight))

            if message[1].upper() in steamids:
                steamid = message[1].upper()
                gamer.execute(f"UPDATE users_steam SET rank = '{message[2]}' WHERE steamid = '{steamid}'")
                database.commit()
                self.logger.info("User with SteamID {} successfully changed rank.".format(steamid))
                await ctx.channel.send(
                    rank_changed.format(ctx.author.mention, steamid))

            elif ctx.message.mentions[0].id in discordids:
                discordid = ctx.message.mentions[0].id
                user.execute(f"SELECT steamid FROM users WHERE \"discordID\" = {discordid}")
                steamid = user.fetchone()[0]
                if steamid == "None":
                    await ctx.channel.send(not_synchronized.format(ctx.author.mention,
                                                                   self.client.get_user(int(discordid)).mention))
                    return
                gamer.execute(f"UPDATE users_steam SET rank = '{message[2]}' WHERE steamid = '{steamid}'")
                database.commit()
                self.logger.info("User with SteamID {} successfully changed rank.".format(steamid))
                await ctx.channel.send(
                    rank_changed.format(ctx.author.mention, self.client.get_user(int(discordid)).mention))

            else:
                await ctx.channel.send(something_went_wrong)

            self.pgsql.close_conn(conn, user)
            self.mysql.close_conn(database, gamer)

        except Exception as error:
            self.logger.error(error)

    @commands.command(name="купить_ранг", help="продает ранг за ВС")
    async def buy_rank(self, ctx, *, rank: str):
        if rank.lower() != "vip" and rank.lower() != "premium":
            await ctx.send(embed=await functions.embeds.description(ctx.author.mention, role_not_exist))
            return

        if rank.lower() == "superadmin":
            await ctx.send(embed=await functions.embeds.description(ctx.author.mention, heh_mdam))
            return

        conn, database, user, gamer = None, None, None, None

        try:
            conn, user = self.pgsql.connect()
            user.execute("SELECT steamid FROM users WHERE \"discordID\" = {}".format(ctx.author.id))
            steamid = user.fetchone()[0]
            if not steamid or steamid == "None":
                await ctx.send(embed=await functions.embeds.description(ctx.author.mention, you_not_synchronized))
                return
        except Exception as error:
            self.logger.error(error)
        finally:
            self.pgsql.close_conn(conn, user)

        try:
            conn, user = self.pgsql.connect()
            database, gamer = self.mysql.connect()
            user.execute("SELECT steamid FROM users WHERE \"discordID\" = {}".format(ctx.author.id))
            steamid = user.fetchone()[0]
            gamer.execute("SELECT rank FROM users_steam WHERE steamid = '{}'".format(steamid))
            now_rank = gamer.fetchone()[0]
            if rank == now_rank:
                await ctx.send(embed=await functions.embeds.description(ctx.author.mention, the_same_ranks))
        except Exception as error:
            self.logger.error(error)
        finally:
            self.pgsql.close_conn(conn, user)
            self.mysql.close_conn(database, gamer)

        try:
            conn, user = self.pgsql.connect()
            database, gamer = self.mysql.connect()
            user.execute("SELECT goldmoney, steamid FROM users WHERE \"discordID\" = {}".format(ctx.author.id))
            data = user.fetchall()[0]
            money, steamid = data[0], data[1]
            if money >= 1000000 and rank == "vip":
                user.execute("UPDATE users SET goldmoney = goldmoney - {} WHERE \"discordID\" = {}".
                             format(1000000, ctx.author.id))
                conn.commit()
                gamer.execute(f"UPDATE users_steam SET rank = 'vip' WHERE steamid = '{steamid}'")
                database.commit()
                await ctx.send(embed=await functions.embeds.description(ctx.author.mention, buying_vip))
            elif money >= 25000000 and rank == "premium":
                user.execute("UPDATE users SET goldmoney = goldmoney - {} WHERE \"discordID\" = {}".
                             format(10000000, ctx.author.id))
                conn.commit()
                gamer.execute(f"UPDATE users_steam SET rank = 'premium' WHERE steamid = '{steamid}'")
                database.commit()
                await ctx.send(embed=await functions.embeds.description(ctx.author.mention, buying_premium))
            else:
                await ctx.send(embed=await functions.embeds.description(ctx.author.mention, not_enough_gold))
        except Exception as error:
            self.logger.error(error)
        finally:
            self.pgsql.close_conn(conn, user)
            self.mysql.close_conn(database, gamer)
