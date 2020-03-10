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
        self.SAMPLE_SPREADSHEET_ID = None
        with open("modueles/spreadsheetid", "r", encoding="utf") as id:
            self.SAMPLE_SPREADSHEET_ID=str(id.read().splitlines()[0])
        self.CREDEBTIALS_FILE = 'modueles/credentials.json'

    def connect(self):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
                      self.CREDEBTIALS_FILE,
                      ['https://www.googleapis.com/auth/spreadsheets',
                       'https://www.googleapis.com/auth/drive'])
        httpAuth = credentials.authorize(httplib2.Http())
        return apiclient.discovery.build('sheets', 'v4', http = httpAuth, cache_discovery=False)

    def get_parameters(self):
        service = Sheet.connect(self)

        values = service.spreadsheets().values().get(spreadsheetId=self.SAMPLE_SPREADSHEET_ID,
                                                     range="I2:I6",
                                                     majorDimension="ROWS"
                                                     ).execute()

        return values['values']

    def append_to_sheet(self, values):
        service = Sheet.connect(self)

        service.spreadsheets().values().append(spreadsheetId=self.SAMPLE_SPREADSHEET_ID,
                                               range="'request'!A1",
                                               body=values,
                                               insertDataOption="INSERT_ROWS",
                                               valueInputOption="RAW"
                                               ).execute()




class RPrequest(commands.Cog, name="Заявки на РП-сессию"):

    def __init__(self, client):
        self.client = client

        self.sheet = Sheet()

        logger = logging.getLogger("rprequest")
        logger.setLevel(logging.INFO)

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
    async def request(self, ctx):
        values = self.sheet.get_parameters()

        if await RPrequest.profile_exist(self, ctx):
            ctx.send(embed=await functions.embeds.description(ctx.author.mention, you_not_synchronized))
            return

        try:
            conn, user = self.pgsql.connect()

            user.execute(f"SELECT steamid FROM users WHERE \"discordID\" = {ctx.author.id}")
            steamid = user.fetchone()[0]
            if steamid == "None" or not steamid:
                ctx.send(embed=await functions.embeds.description(ctx.author.mention, you_not_synchronized))
                return
            elif steamid:
                data = ctx.message.content.split()
                if data[2].lower() == "дцх":
                    values = {"values": [[data[1], steamid, data[2], "-", data[3]]]}
                    append_to_sheet(values)
                elif data[2].lower() == "дсцп" or data[2].lower() == "маневровый":
                    values = {"values": [[data[1], steamid, data[2], "-", data[3]]]}
                    append_to_sheet(values)
                elif data[2].lower() == "машинист":
                    values = {"values": [[data[1], steamid, data[2], data[3], "-"]]}
                    append_to_sheet(values)
                else:
                    ctx.send(embed=await functions.embeds.description(ctx.author.mention, role_dont_exist))

        except Exception as error:
            self.logger.error(error)
        finally:
            self.pgsql.close_conn(conn, user)

    @commands.command(name="удалить_заявку", help="<префикс>удалить_заявку (<хайлайт игрока>)")
    async def delete_request(self, ctx):

        if await RPrequest.profile_exist(self, ctx):
            ctx.send(embed=await functions.embeds.description(ctx.author.mention, dont_write))
            return

        try:
            conn, user = self.pgsql.connect()

            user.execute(f"SELECT steamid FROM users WHERE \"discordID\" = {ctx.author.id}")
            steamid = user.fetchone()[0]
            if steamid == "None" or not steamid:
                ctx.send(embed=await functions.embeds.description(ctx.author.mention, dont_write))
                return
            elif steamid:
                service.spreadsheets().values().get(spreadsheetId=spreadsheet_id,
                                                    range="'request'!A")
        except Exception as error:
            self.logger.error(error)
        finally:
            self.pgsql.close_conn(conn, user)

    @commands.command(name="участники", help="<префикс>участники")
    async def members(self, ctx):
        pass

# values = service.spreadsheets().values().append(
#          spreadsheetId=SAMPLE_SPREADSHEET_ID,
#          range="'Лист1'!A1",
#          body={
#                "values": [["Nikolay", "машинист", "32 маршрут"]]
#          },
#          insertDataOption="INSERT_ROWS",
#          valueInputOption="RAW"
# ).execute()
