import logging
import json
import requests
import random
from bs4 import BeautifulSoup
from discord.ext import commands, tasks
from functions.embeds import *
from language.treatment_ru import *
from functions.database import PgSQLConnection
from functions.database import MySQLConnection


class Invests(commands.Cog, name="Инвистиции"):

    def __init__(self, user):
        self.client = user

        self.pgsql = PgSQLConnection()
        self.mysql = MySQLConnection()

        self.update_invests.start()

        self.url = "https://www.rbc.ru/crypto/currency/neousd"

        logger = logging.getLogger("invests")
        logger.setLevel(logging.INFO)
        self.logger = logger

    def __check_course__(self):
        self.time = int(time.time())

        soup = BeautifulSoup(requests.get(self.url).text, features="lxml")

        table = soup.find("div", {"class": "chart__subtitle js-chart-value"})
        course = float(table.text[10:17].replace(' ', '').replace(',', '.'))

        return course

    @tasks.loop(minutes=30.0)
    async def update_invests(self):

        with open("invests.json", "r", encoding="utf8") as file:
            info = json.load(file)

        if not info:
            info = {
                "first_company": {
                    "name": "ProjectINC",
                    "percent_of_lucky": 45,
                    "share_price": 45.57
                },
                "second_company": {
                    "name": "RiderCorp",
                    "percent_of_lucky": 23,
                    "share_price": 61.77
                },
                "third_company": {
                    "name": "UnionStd",
                    "percent_of_lucky": 58,
                    "share_price": 25.74
                }
            }

        lucky = random.choices([True, False],
                               weights=[info['first_company']['percent_of_lucky'],
                                        100 - info['first_company']['percent_of_lucky']])

        if lucky[0]:
            f1 = abs(round(random.uniform(float(info['first_company']['share_price']) / self.__check_course__(),
                                          float(info['first_company']['share_price']) / self.__check_course__() + 6.0)
                           * self.__check_course__(), 2))
        else:
            f1 = abs(round(random.uniform(1, float(info['first_company']['share_price']) / self.__check_course__() - 1)
                           * self.__check_course__(), 2))

        lucky = random.choices([True, False],
                               weights=[info['second_company']['percent_of_lucky'],
                                        100 - info['second_company']['percent_of_lucky']])

        if lucky[0]:
            f2 = abs(round(random.uniform(float(info['second_company']['share_price']) / self.__check_course__(),
                                          float(info['second_company']['share_price']) / self.__check_course__() + 6.0)
                           * self.__check_course__(), 2))
        else:
            f2 = abs(
                round(random.uniform(1, (float(info['third_company']['share_price']) / self.__check_course__()) - 1)
                      * self.__check_course__(), 2))

        lucky = random.choices([True, False],
                               weights=[info['third_company']['percent_of_lucky'],
                                        100 - info['third_company']['percent_of_lucky']])

        if lucky[0]:
            f3 = abs(round(random.uniform(float(info['third_company']['share_price']) / self.__check_course__(),
                                          float(info['third_company']['share_price']) / self.__check_course__() + 6.0)
                           * self.__check_course__(), 2))
        else:
            f3 = abs(
                round(random.uniform(1, (float(info['third_company']['share_price']) / self.__check_course__()) - 1)
                      * self.__check_course__(), 2))

        info = {
            'first_company': {
                'name': "ProjectINC",
                'percent_of_lucky': random.randint(10, 66),
                'share_price': f1
            },
            'second_company': {
                'name': "RiderCorp",
                'percent_of_lucky': random.randint(10, 66),
                'share_price': f2
            },
            'third_company': {
                'name': "UnionStd",
                'percent_of_lucky': random.randint(10, 66),
                'share_price': f3
            }
        }

        with open("invests.json", "w", encoding="utf8") as file:
            json.dump(info, file, indent=5)

    @commands.command(name="инвест_помощь", help="закрывает и удаляет счет в банке")
    async def invest_help(self, ctx):
        await ctx.send(embed=await invest_help(ctx))

    @commands.command(name="имя_банка", help="изменяет название банка")
    @commands.has_permissions(administrator=True)
    async def name_bank(self, ctx, *, name: str):
        conn, user, bank = None, None, None
        try:
            conn, user = self.pgsql.connect()
            user.execute("SELECT bank_info FROM info WHERE guild_id = {}".format(ctx.guild.id))
            bank = user.fetchone()[0]
        except Exception as error:
            self.logger.error(error)
        finally:
            self.pgsql.close_conn(conn, user)

        bank['name'] = name

        try:
            conn, user = self.pgsql.connect()
            user.execute('UPDATE info SET bank_info = %s WHERE guild_id = %s', (json.dumps(bank), ctx.guild.id))
            conn.commit()

            await ctx.send(embed=await description(name, save_name_bank))
        except Exception as error:
            self.logger.error(error)
        finally:
            self.pgsql.close_conn(conn, user)

    @commands.command(name="имя_валюты", help="изменяет название валюты")
    @commands.has_permissions(administrator=True)
    async def name_currency(self, ctx, *, name: str):
        conn, user, bank = None, None, None
        try:
            conn, user = self.pgsql.connect()
            user.execute("SELECT bank_info FROM info WHERE guild_id = {}".format(ctx.guild.id))
            bank = user.fetchone()[0]
        except Exception as error:
            self.logger.error(error)
        finally:
            self.pgsql.close_conn(conn, user)

        bank['char_of_currency'] = name

        try:
            conn, user = self.pgsql.connect()
            user.execute('UPDATE info SET bank_info = %s WHERE guild_id = %s', (json.dumps(bank), ctx.guild.id))
            conn.commit()
        except Exception as error:
            self.logger.error(error)
        else:
            await ctx.send(embed=await description(name, save_name_currency))
        finally:
            self.pgsql.close_conn(conn, user)

    @commands.command(name="открыть_счёт", help="открывает счёт в банке")
    async def open_bill(self, ctx):
        conn, user = None, None
        try:
            conn, user = self.pgsql.connect()
            user.execute("SELECT guild_id FROM bank WHERE discordID = {}".format(ctx.author.id))
            guild_id = user.fetchone()[0]

            if guild_id != ctx.guild.id:
                await ctx.send(embed=await description(ctx.author.mention, bill_already_open))
                return

        except Exception as error:
            await ctx.send(something_went_wrong)
            self.logger.error(error)
        finally:
            self.pgsql.close_conn(conn, user)

        try:
            invest_status = {"first_company": 0, "second_company": 0, "third_company": 0}

            conn, user = self.pgsql.connect()
            user.execute("INSERT INTO bank VALUES ({}, {}, {}, {})".format(ctx.author.id, ctx.guild.id, 0,
                                                                           int(time.time())), json.dumps(invest_status))
            conn.commit()

            await ctx.send(creating_bank_account.format(ctx.author.mention, ctx.author.id))
        except Exception as error:
            await ctx.send(embed=await description(ctx.author.mention, account_exist))
            self.logger.error(error)
        finally:
            self.pgsql.close_conn(conn, user)

    @commands.command(name="счёт", help="выводит информацию по счёту")
    async def bill(self, ctx):
        conn, user, info, bank = None, None, None, None
        try:
            conn, user = self.pgsql.connect()
            user.execute("SELECT * FROM bank WHERE discordID = {}".format(ctx.author.id))
            info = user.fetchall()[0]
            user.execute("SELECT bank_info FROM info WHERE guild_id = {}".format(info[1]))
            bank = user.fetchone()[0]
        except TypeError as error:
            await ctx.send(account_not_exist.format(ctx.author.mention))
            self.logger.error(error)
        except Exception as error:
            await ctx.send(something_went_wrong)
            self.logger.error(error)
        else:
            await ctx.send(embed=await bill(ctx, info, bank))
        finally:
            self.pgsql.close_conn(conn, user)

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

    @commands.command(name="банк", help="показывает информацию по банку")
    async def bank(self, ctx):
        conn, user, all_amount = None, None, .0
        try:
            conn, user = self.pgsql.connect()
            user.execute("SELECT SUM(amount) FROM bank WHERE guild_id = {}".format(ctx.guild.id))
            all_amount = user.fetchone()[0]
        except Exception as error:
            self.logger.error(error)
        finally:
            self.pgsql.close_conn(conn, user)

        try:

            conn, user = self.pgsql.connect()
            user.execute("SELECT bank_info FROM info WHERE guild_id = {}".format(ctx.guild.id))
            bank = user.fetchone()[0]

            course = self.__check_course__()

            await ctx.send(embed=await bank_info(ctx, all_amount, course, bank['name']))
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
            user.execute("SELECT money FROM users WHERE \"discordID\" = {}".format(ctx.author.id))
            money = user.fetchone()[0]
            user.execute("SELECT bank_info FROM info WHERE guild_id = {}".format(ctx.guild.id))
            info = user.fetchone()

            if float(money) < float(amount):
                await ctx.send(not_enough_money.format(ctx.author.mention, info['name_of_currency']))
                return
        except TypeError as error:
            await ctx.send(account_not_exist.format(ctx.author.mention))
            self.logger.error(error)
            return
        except Exception as error:
            self.logger.error(error)
        finally:
            self.pgsql.close_conn(conn, user)

        try:
            conn, user = self.pgsql.connect()
            user.execute("UPDATE bank SET amount = amount + %s WHERE discordID = %s;"
                         "UPDATE users SET money = money - %s WHERE \"discordID\" = %s;",
                         ((float(amount) * self.__check_course__()), ctx.author.id, amount, ctx.author.id))
            conn.commit()
            await ctx.send(embed=await description(ctx.author.mention, successful_put))

        except Exception as error:
            self.logger.error(error)
            await ctx.send(something_went_wrong)
        finally:
            self.pgsql.close_conn(conn, user)

    @commands.command(name="перевести", help="переводит со счёта на счёт")
    async def transaction(self, ctx, *, data: str):
        conn, user = None, None

        data = data.split()

        bill_id = data[0]
        amount = data[1]

        if not bill_id.isdigit() or not amount.isdigit():
            await ctx.send(transaction_error.format(ctx.author.mention, self.client.command_prefix))
            return

        try:
            conn, user = self.pgsql.connect()

            user.execute("SELECT * FROM bank WHERE discordID = {}".format(int(bill_id)))
            user.fetchall()[0]

            user.execute("SELECT bank_info FROM info WHERE guild_id = {}".format(ctx.guild.id))
            info = user.fetchone()

            user.execute("SELECT amount FROM bank WHERE discordID = {}".format(ctx.author.id))
            if user.fetchone()[0] < float(amount):
                await ctx.send(not_enough_money.format(ctx.author.mention, info['name_of_currency']))
                return

            user.execute("UPDATE bank SET amount = amount - %s WHERE discordID = %s;"
                         "UPDATE bank SET amount = amount + %s WHERE discordID = %s;",
                         (float(amount), ctx.author.id, float(amount), int(bill_id)))
            conn.commit()
        except TypeError as error:
            await ctx.send(embed=await description(ctx.author.mention, bill_not_found))
            self.logger.error(error)
        except Exception as error:
            await ctx.send(something_went_wrong)
            self.logger.error(error)
        finally:
            self.pgsql.close_conn(conn, user)

    @commands.command(name="снять", help="переводить на счёт")
    async def get_from_bank(self, ctx, *, amount: str):
        if not amount.isdigit():
            await ctx.send(not_a_number.format(ctx.author.mention, self.client.command_prefix))
            return

        conn, user = None, None

        try:
            conn, user = self.pgsql.connect()
            user.execute("SELECT amount FROM bank WHERE discordID = {}".format(ctx.author.id))
            real_amount = user.fetchone()[0]

            if float(real_amount) < float(amount):
                await ctx.send(not_enough_money.format(ctx.author.mention, "NEO"))
                return
        except TypeError as error:
            await ctx.send(account_not_exist.format(ctx.author.mention))
            self.logger.error(error)
            return
        except Exception as error:
            self.logger.error(error)
        finally:
            self.pgsql.close_conn(conn, user)

        try:
            conn, user = self.pgsql.connect()
            user.execute("UPDATE bank SET amount = amount - %s WHERE discordID = %s;"
                         "UPDATE users SET money = money + %s WHERE \"discordID\" = %s;",
                         (float(amount), ctx.author.id,
                          int(float(amount) / self.__check_course__()) + 1, ctx.author.id))
            conn.commit()
            await ctx.send(embed=await description(ctx.author.mention, successful_get))

        except Exception as error:
            self.logger.error(error)
            await ctx.send(something_went_wrong)
        finally:
            self.pgsql.close_conn(conn, user)

    @commands.command(name="инвест_статус", help="возвращает вам деньги со счёта")
    async def invest_status(self, ctx):
        with open("invests.json", "r", encoding="utf8") as file:
            info = json.load(file)

            await ctx.send(embed=await invests_status(ctx, info))

    @commands.command(name="купить_акции", help="вкладывается в опроеделенную компанию")
    async def buy_share(self, ctx, *, data: str):
        data = data.split()

        conn, user, all_info = None, None, None

        if not data[1].isdigit():
            await ctx.send(not_a_number.format(ctx.author.mention, self.client.command_prefix))
            return

        with open("invests.json", "r", encoding="utf8") as file:
            invests = json.load(file)

        try:
            conn, user = self.pgsql.connect()

            user.execute("SELECT * FROM bank WHERE discordID = {}".format(ctx.author.id))
            all_info = user.fetchall()[0]
        except TypeError as error:
            await ctx.send(account_not_exist.format(ctx.author.mention))
            self.logger.error(error)
            return
        except Exception as error:
            self.logger.error(error)
        finally:
            self.pgsql.close_conn(conn, user)

        amount = all_info[2]
        invest_status = all_info[4]

        if not invest_status:
            invest_status = {'first_company': 0, 'second_company': 0, 'third_company': 0}

        if data[0].lower() == invests['first_company']['name'].lower():
            if invest_status['first_company'] + int(data[1]) > 1000:
                await ctx.send(embed=await description(ctx.author.mention, more_than_hundred))
                return

            elif float(data[1]) * invests['first_company']['share_price'] > amount:
                await ctx.send(more_than_have.format(ctx.author.mention, "NEO"))
                return

            amount = round(invests['first_company']['share_price'] * float(data[1]), 2)
            invest_status['first_company'] += int(data[1])

            await ctx.send(successful_buy.format(ctx.author.mention, invests['first_company']['name'], amount))

        elif data[0].lower() == invests['second_company']['name'].lower():
            if invest_status['second_company'] + int(data[1]) > 1000:
                await ctx.send(embed=await description(ctx.author.mention, more_than_hundred))
                return

            elif float(data[1]) * invests['second_company']['share_price'] > amount:
                await ctx.send(more_than_have.format(ctx.author.mention, "NEO"))
                return

            amount = round(invests['second_company']['share_price'] * float(data[1]), 2)
            invest_status['second_company'] += int(data[1])

            await ctx.send(successful_buy.format(ctx.author.mention, invests['second_company']['name'], amount))

        elif data[0].lower() == invests['third_company']['name'].lower():
            if invest_status['third_company'] + int(data[1]) > 1000:
                await ctx.send(embed=await description(ctx.author.mention, more_than_hundred))
                return

            elif float(data[1]) * invests['third_company']['share_price'] > amount:
                await ctx.send(more_than_have.format(ctx.author.mention, "NEO"))
                return

            amount = round(invests['third_company']['share_price'] * float(data[1]), 2)
            invest_status['third_company'] += int(data[1])

            await ctx.send(successful_buy.format(ctx.author.mention, invests['third_company']['name'], amount))
        else:
            await ctx.send(embed=await description(ctx.author.mention, company_not_found))
            return

        try:
            conn, user = self.pgsql.connect()

            user.execute("UPDATE bank SET invest_status = %s, amount = amount - %s WHERE discordID = %s",
                         (json.dumps(invest_status), amount, ctx.author.id))
            conn.commit()
        except Exception as error:
            self.logger.error(error)
        finally:
            self.pgsql.close_conn(conn, user)

    @commands.command(name="акции", help="показывает акции которые у вас есть")
    async def share(self, ctx):
        conn, user = None, None

        try:
            conn, user = self.pgsql.connect()

            user.execute("SELECT * FROM bank WHERE discordID = {}".format(ctx.author.id))
            var = user.fetchall()[0]

            user.execute("SELECT invest_status FROM bank WHERE discordID = {}".format(ctx.author.id))
            info = user.fetchone()[0]

            await ctx.send(embed=await share(ctx, info))
        except TypeError as error:
            await ctx.send(account_not_exist.format(ctx.author.mention))
            self.logger.error(error)
        except Exception as error:
            self.logger.error(error)
        finally:
            self.pgsql.close_conn(conn, user)

    @commands.command(name="продать_акции", help="продает акции")
    async def sale_share(self, ctx, *, data: str):
        data = data.split()

        conn, user, invest_status, amount = None, None, None, None

        with open("invests.json", "r", encoding="utf8") as file:
            invests = json.load(file)

        try:
            conn, user = self.pgsql.connect()

            user.execute("SELECT invest_status FROM bank WHERE discordID = {}".format(ctx.author.id))
            invest_status = user.fetchone()[0]
        except TypeError as error:
            await ctx.send(account_not_exist.format(ctx.author.mention))
            self.logger.error(error)
        except Exception as error:
            self.logger.error(error)
        finally:
            self.pgsql.close_conn(conn, user)

        if not invest_status:
            await ctx.send(embed=await description(ctx.author.mention, not_buy_anything))
            return

        if data[0].lower() == invests['first_company']['name'].lower():
            if invest_status['first_company'] < int(data[1]):
                await ctx.send(more_than_have.format(ctx.author.mention, "акций"))
                return

            amount = round(invests['first_company']['share_price'] * float(data[1]), 2)
            invest_status['first_company'] -= int(data[1])

            await ctx.send(successful_sale.format(ctx.author.mention, invests['first_company']['name'], amount))

        elif data[0].lower() == invests['second_company']['name'].lower():
            if invest_status['second_company'] < int(data[1]):
                await ctx.send(more_than_have.format(ctx.author.mention, "акций"))
                return

            amount = round(invests['second_company']['share_price'] * float(data[1]), 2)
            invest_status['second_company'] -= int(data[1])

            await ctx.send(successful_sale.format(ctx.author.mention, invests['second_company']['name'], amount))

        elif data[0].lower() == invests['third_company']['name'].lower():
            if invest_status['third_company'] < int(data[1]):
                await ctx.send(more_than_have.format(ctx.author.mention, "акций"))
                return

            amount = round(invests['third_company']['share_price'] * float(data[1]), 2)
            invest_status['third_company'] -= int(data[1])

            await ctx.send(successful_sale.format(ctx.author.mention, invests['third_company']['name'], amount))
        else:
            await ctx.send(embed=await description(ctx.author.mention, company_not_found))
            return

        try:
            conn, user = self.pgsql.connect()

            user.execute("UPDATE bank SET invest_status = %s, amount = amount + %s WHERE discordID = %s",
                         (json.dumps(invest_status), amount, ctx.author.id))
            conn.commit()
        except Exception as error:
            self.logger.error(error)
        finally:
            self.pgsql.close_conn(conn, user)

    @commands.command(name="курс", help="кладет на счет в банке")
    async def course(self, ctx):
        course = self.__check_course__()
        embed = discord.Embed(colour=discord.Colour.default())
        embed.description = f"Нынешний курс банка: {course} NEO."
        await ctx.send(embed=embed)
