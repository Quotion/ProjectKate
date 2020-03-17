import httplib2
import discord
import logging
import functions.embeds
import apiclient.discovery
from discord.ext import commands
from oauth2client.service_account import ServiceAccountCredentials
from language.treatment_ru import *
from pprint import pprint

class Sheet(object):

    def __init__(self):
        logger = logging.getLogger("sheet")
        logger.setLevel(logging.INFO)

        self.logger = logger

        self.SAMPLE_SPREADSHEET_ID = None
        with open("modueles/spreadsheetid", "r", encoding="utf") as id:
            self.SAMPLE_SPREADSHEET_ID=str(id.read().splitlines()[0])
        self.CREDEBTIALS_FILE = 'modueles/credentials.json'

    def connect(self):
        try:
            credentials = ServiceAccountCredentials.from_json_keyfile_name(
                          self.CREDEBTIALS_FILE,
                          ['https://www.googleapis.com/auth/spreadsheets',
                           'https://www.googleapis.com/auth/drive'])
            httpAuth = credentials.authorize(httplib2.Http())
            service = apiclient.discovery.build('sheets', 'v4', http = httpAuth, cache_discovery=False)
        except Exception as error:
            self.logger.error(error)
            return None
        else:
            return service

    def get_parameters(self):
        service = Sheet.connect(self)

        if not service:
            return None

        values = service.spreadsheets().values().get(spreadsheetId=self.SAMPLE_SPREADSHEET_ID,
                                                     range="'parameters'!B2:B4",
                                                     majorDimension="ROWS"
                                                     ).execute()

        return values['values']

    def get_data(self, id_cloumn):
        service = Sheet.connect(self)

        if not service:
            return None

        roles = list()

        values = service.spreadsheets().values().get(spreadsheetId=self.SAMPLE_SPREADSHEET_ID,
                                                     range=f"'request'!{chr(65 + id_cloumn)}2:{chr(65 + id_cloumn)}30",
                                                     majorDimension="COLUMNS"
                                                     ).execute()

        if "values" not in values.keys():
            return []

        for value in values['values'][0]:
            if value == "" or not value:
                break
            else:
                roles.append(value)

        return roles

    def get_all_data(self):
        service = Sheet.connect(self)

        if not service:
            return None

        values = service.spreadsheets().values().get(spreadsheetId=self.SAMPLE_SPREADSHEET_ID,
                                                     range="'request'!A1:F30",
                                                     majorDimension="ROWS"
                                                     ).execute()

        values = values['values']

        for array, i in zip(values, range(0, len(values))):
            if array[0] == "":
                values = values[0:i]
                break

        return values

    def append_to_sheet(self, values):
        service = Sheet.connect(self)

        service.spreadsheets().values().append(spreadsheetId=self.SAMPLE_SPREADSHEET_ID,
                                               range="'request'!A1:F1",
                                               body=values,
                                               insertDataOption="OVERWRITE",
                                               valueInputOption="RAW"
                                               ).execute()

    def delete_info(self, id_row):
        service = Sheet.connect(self)

        if not service:
            return None

        service.spreadsheets().values().clear(spreadsheetId=self.SAMPLE_SPREADSHEET_ID,
                                              range=f"'request'!A{id_row}:F{id_row}"
                                              ).execute()


class RPrequest(commands.Cog, name="Заявки на РП-сессию"):

    def __init__(self, client):
        self.client = client

        self.sheet = Sheet()

        logger = logging.getLogger("rprequest")
        logger.setLevel(logging.DEBUG)

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
                    (ctx.author.id, 0, 0, 0, 1, now.day - 1, ctx.author.name))
                conn.commit()
                self.logger.info("Profile of {} successfully created.".format(ctx.author.name))
            except Exception as error:
                await ctx.send(something_went_wrong)
                self.logger.error(error)
            finally:
                self.pgsql.close_conn(conn, user)
                return True

    @commands.command(name="заявка", help="<префикс>заявка <ник> <роль> <номер/ст.> <линия>")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def request(self, ctx):
        if await RPrequest.profile_exist(self, ctx):
            await ctx.send(embed=await functions.embeds.description(ctx.author.mention, you_not_synchronized))
            return

        try:
            conn, user = self.pgsql.connect()
            values = self.sheet.get_parameters()
            data = ctx.message.content.split()

            if not values:
                await ctx.send(something_went_wrong)
                raise Warning

            user.execute(f"SELECT steamid FROM users WHERE \"discordID\" = {ctx.author.id}")
            steamid = user.fetchone()[0]

            if steamid == "None" or not steamid:
                await ctx.send(embed=await functions.embeds.description(ctx.author.mention, you_not_synchronized))
                raise Exception("Person not synchronized")
            else:
                if steamid in self.sheet.get_data(1):
                    await ctx.send(embed=await functions.embeds.description(ctx.author.mention, already_in_rp))
                    raise Warning("# WARNING: Person already on RP")

                if len(data) < 4:
                    await ctx.send(not_enough_words_to_rp.format(ctx.author.mention, self.client.command_prefix[0]))
                    raise Warning("# WARNING: Not enough words")

                if data[2].lower() != "дцх" and data[2].lower() != "дсцп" and data[2].lower() != "маневровый" and data[2].lower() != "машинист":
                    await ctx.send(embed=await functions.embeds.description(ctx.author.mention, role_dont_exist))
                    raise Warning("# WARNING: Entered role dont exist")

                if data[2].lower() == "дцх":
                    if (int(data[3]) > int(values[0][0])) or (int(data[3]) <= 0):
                        await ctx.send(embed=await functions.embeds.description(ctx.author.mention, line_not_exist))
                        raise Warning("# WARNING: Too many lines")
                    elif int(values[0][0]) <= self.sheet.get_data(2).count("дцх"):
                        await ctx.send(embed=await functions.embeds.description(ctx.author.mention, dch_already_taken))
                        raise Warning("# WARNING: Line already taken")
                    else:
                        full_info = {"values": [[data[1], steamid, "дцх", "-", "-", data[3]]]}
                        self.sheet.append_to_sheet(full_info)
                        await ctx.send(success_add_dch.format(ctx.author.mention, data[3]))
                        raise Warning("# WARNING: Person successfully added on RP")

                if len(data) > 5:
                    await ctx.send(not_enough_words_to_rp.format(ctx.author.mention, self.client.command_prefix[0]))
                    raise Warning("# WARNING: Not enough words")

                if (int(data[4]) > int(values[0][0])) or (int(data[4]) <= 0):
                    await ctx.send(embed=await functions.embeds.description(ctx.author.mention, line_not_exist))
                    raise Warning("# WARNING: Too many lines")

                if data[2].lower() == "дсцп":
                    if int(values[2][0]) <= self.sheet.get_data(2).count("дсцп"):
                        await ctx.send(embed=await functions.embeds.description(ctx.author.mention, dscp_already_taken))
                        raise Warning("# WARNING: Role already taken")
                    else:
                        full_info = {"values": [[data[1], steamid, "дсцп", "-", data[3], data[4]]]}
                        self.sheet.append_to_sheet(full_info)
                        await ctx.send(success_add_dscp.format(ctx.author.mention, data[3]))
                        raise Warning("# WARNING: Person successfully added on RP")

                if data[2].lower() == "маневровый":
                    if int(values[1][0]) == 0:
                        await ctx.send(embed=await functions.embeds.description(ctx.author.mention, driver_shunting))
                        raise Warning("# WARNING: Shunting driver not on RP")
                    elif int(values[1][0]) <= self.sheet.get_data(2).count("маневровый"):
                        await ctx.send(embed=await functions.embeds.description(ctx.author.mention, driver_shunting_already_exist))
                        raise Warning("# WARNING: Role already taken")
                    else:
                        full_info = {"values": [[data[1], steamid, "маневровый", "-", data[3], data[4]]]}
                        self.sheet.append_to_sheet(full_info)
                        await ctx.send(success_add_shunting_driver.format(ctx.author.mention, data[4], data[3]))
                        raise Warning("# WARNING: Person successfully added on RP")


                if data[2].lower() == "машинист":
                    if data[3] not in self.sheet.get_data(3):
                        full_info = {"values": [[data[1], steamid, "машинист", data[3], "-", data[4]]]}
                        self.sheet.append_to_sheet(full_info)
                        await ctx.send(success_add_driver.format(ctx.author.mention, data[4], data[3]))
                        raise Warning("# WARNING: Person successfully added on RP")
                    else:
                        await ctx.send(embed=await functions.embeds.description(ctx.author.mention, number_already_taken))
                        raise Warning("# WARNING: Number already taken")

        except Warning as warning:
            self.logger.warning(warning)
        except Exception as error:
            await ctx.send(you_not_right.format(ctx.author.mention, self.client.command_prefix[0]))
            self.logger.error(error)
        finally:
            self.pgsql.close_conn(conn, user)

    @commands.command(name="удалить_заявку", help="<префикс>удалить_заявку (<хайлайт игрока>)")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def delete_request(self, ctx):

        if await RPrequest.profile_exist(self, ctx):
            await ctx.send(embed=await functions.embeds.description(ctx.author.mention, dont_write))
            return

        try:
            conn, user = self.pgsql.connect()

            user.execute(f"SELECT steamid FROM users WHERE \"discordID\" = {ctx.author.id}")
            steamid = user.fetchone()[0]
            if steamid == "None" or not steamid:
                await ctx.send(embed=await functions.embeds.description(ctx.author.mention, dont_write))
                raise Warning
            elif steamid:
                if steamid in self.sheet.get_data(1):
                    self.sheet.delete_info(self.sheet.get_data(1).index(steamid) + 2)
                    await ctx.send(embed=await functions.embeds.description(ctx.author.mention, success_delete))
                    raise Warning
                else:
                    await ctx.send(embed=await functions.embeds.description(ctx.author.mention, dont_write))
                    raise Warning

        except Warning:
            pass
        except Exception as error:
            self.logger.error(error)
        finally:
            self.pgsql.close_conn(conn, user)

    @commands.command(name="участники", help="<префикс>участники")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def members(self, ctx):
        all_data = self.sheet.get_all_data()

        if not all_data:
            await ctx.send(something_went_wrong)
            raise Warning

        await ctx.send(embed=await functions.embeds.all_members(ctx, all_data))
