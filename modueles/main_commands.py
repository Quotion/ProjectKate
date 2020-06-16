import datetime
import requests
import logging
import os
import json

import discord
from discord.ext import commands, tasks
import random

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from io import BytesIO


import functions.database
import functions.helper
from functions.create_plot import create_figure
from language.treatment_ru import *


class MainCommands(commands.Cog, name="Основные команды"):

    def __init__(self, client):
        self.client = client

        logger = logging.getLogger("main_commands")
        logger.setLevel(logging.INFO)

        self.logger = logger

        self.mysql = functions.database.MySQLConnection()
        self.pgsql = functions.database.PgSQLConnection()

        self.generate_promo.start()

    async def profile_exist(self, author, channel):
        conn, user = self.pgsql.connect()
        try:
            user.execute('SELECT * FROM users WHERE "discordID" = %s', [author.id])
            var = user.fetchall()[0]
            self.pgsql.close_conn(conn, user)
            return False
        except IndexError as error:

            now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))

            try:
                user.execute(
                    'INSERT INTO users ("discordID", rating, money, goldMoney, "chanceRol", "dateRol", nick) '
                    'VALUES(%s, %s, %s, %s, %s, %s, %s)',
                    (author.id, 0, 0, 0, 1, now.day - 1, author.name))
                conn.commit()
                self.logger.info("Profile of {} successfully created.".format(author.name))
            except Exception as error:
                await channel.send(something_went_wrong)
                self.logger.info(error)

            self.pgsql.close_conn(conn, user)
            return True

    @tasks.loop(minutes=873.0)
    async def generate_promo(self):
        data, conn, user = None, None, None

        try:
            conn, user = self.pgsql.connect()
            user.execute("SELECT guild_id, promocode, bank_info FROM info WHERE NOT (promocode ->> 'code'::text) = '0'::text")
            data = user.fetchall()
            if not data:
                raise IndexError
        except IndexError as error:
            pass
        except Exception as error:
            self.logger.error(error)
        else:
            for item in data:

                channel = self.client.get_guild(int(item[0])).system_channel

                promo, win, thing = None, None, None
                comment = random.choice(promo_event)

                if not item[1]['code'] == 1:
                    promo = item[1]['code']
                    thing = int(str(item[1]['code'])[5]) - 4
                    win = item[1]['amount']
                else:
                    win, thing = await functions.helper.promo_win()
                    promo = str(random.randint(10000, 100000)) + str(thing + 4)

                    user.execute("UPDATE info SET promocode = %s WHERE guild_id = %s", (json.dumps({"amount": win, "code": int(promo)}), item[0]))
                    conn.commit()

                if thing == 0:
                    await channel.send(comment.format(win, item[2]['char_of_currency'], promo))
                elif thing == 1:
                    await channel.send(comment.format(win, f"зол. {item[2]['char_of_currency']}", promo))
                else:
                    await channel.send(comment.format(win, f"рейт.", promo))

        finally:
            self.pgsql.close_conn(conn, user)

    @generate_promo.before_loop
    async def ready(self):
        await self.client.wait_until_ready()

    @commands.command(name='вкл_промо', help="<префикс>вкл_промо")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def promo_on(self, ctx):
        try:
            conn, user = self.pgsql.connect()
            user.execute("SELECT promocode FROM info WHERE guild_id = {}".format(ctx.guild.id))
            promo = user.fetchone()[0]
            if not promo or promo == "null":
                user.execute("UPDATE info SET promocode = %s WHERE guild_id = %s", (json.dumps({"amount": 0, "code": 1}), ctx.guild.id))
                conn.commit()
                await ctx.send(promo_on.format(ctx.author.mention, self.client.command_prefix[0]))
            elif promo['code'] == 0:
                user.execute("UPDATE info SET promocode = %s WHERE guild_id = %s", (json.dumps({"amount": 0, "code": 1}), ctx.guild.id))
                conn.commit()
                await ctx.send(promo_on.format(ctx.author.mention, self.client.command_prefix[0]))
            elif not promo['code'] == 0:
                await ctx.send(embed=await functions.embeds.description(ctx.author.mention, promo_already_on))
                return
        except IndexError as error:
            self.logger.error(error)
        except Exception as error:
            self.logger.error(error)
        finally:
            self.pgsql.close_conn(conn, user)

    @commands.command(name='выкл_промо', help="<префикс>вкл_промо")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def promo_off(self, ctx):
        conn, user = None, None

        try:
            conn, user = self.pgsql.connect()
            user.execute("SELECT promocode FROM info WHERE guild_id = {}".format(ctx.guild.id))
            promo = user.fetchone()[0]
            if promo['code'] == 0:
                await ctx.send(embed=await functions.embeds.description(ctx.author.mention, promo_already_off))
                return
            else:
                user.execute("UPDATE info SET promocode = %s WHERE guild_id = %s", (json.dumps({"amount": 0, "code": 0}), ctx.guild.id))
                conn.commit()
                await ctx.send(promo_off.format(ctx.author.mention, self.client.command_prefix[0]))
        except IndexError as error:
            self.logger.error(error)
        except Exception as error:
            self.logger.error(error)
        finally:
            self.pgsql.close_conn(conn, user)


    @commands.command(name='профиль', help="<префикс>профиль <Discord или ничего>")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def profile(self, ctx):
        if await MainCommands.profile_exist(self, ctx.author, ctx.channel):
            pass

        conn, user = self.pgsql.connect()
        data = None

        user.execute("SELECT bank_info FROM info WHERE guild_id = {}".format(ctx.guild.id))
        name_of_currency = user.fetchone()[0]['char_of_currency']

        if len(ctx.message.content.split()) == 2 and len(ctx.message.mentions) == 1:
            if await MainCommands.profile_exist(self, self.client.get_user(ctx.message.mentions[0].id), ctx.channel):
                pass
            user.execute('SELECT * FROM users WHERE "discordID" = %s', [ctx.message.mentions[0].id])
            user_ctx = self.client.get_user(ctx.message.mentions[0].id)
        elif len(ctx.message.content.split()) == 1:
            user.execute('SELECT * FROM users WHERE "discordID" = %s', [ctx.author.id])
            user_ctx = ctx.author
        else:
            await ctx.send(something_went_wrong)
            return
        try:
            data = user.fetchall()[0]
        except IndexError as error:
            self.logger.error(error)
        try:
            if data[7] and data[7] != "None":
                conn_mysql, user_mysql = self.mysql.connect()
                user_mysql.execute("SELECT * FROM users_steam WHERE steamid = '{}'".format(data[7]))
                steam = user_mysql.fetchall()[0]

                user_mysql.execute("SELECT all_time_on_server FROM statistics WHERE steamid = '{}'".format(data[7]))
                time = user_mysql.fetchone()

                all_data = dict(rating=data[1], money=data[2], gold_money=data[3], steamid=data[7], nick=steam[1], time=time[0],
                                rank=steam[2], name_of_currency=name_of_currency)

                self.mysql.close_conn(conn_mysql, user_mysql)
            else:
                all_data = dict(rating=data[1], money=data[2], gold_money=data[3], steamid='Не синхронизирован',
                                nick='Не синхронизирован', time='Не синхронизирован', rank='Не синхронизирован',
                                name_of_currency=name_of_currency)

            try:
                img_profile = Image.open("stuff/profile.jpg")

                fileRequest = requests.get(ctx.author.avatar_url)
                img_avatar = Image.open(BytesIO(fileRequest.content))

                img_avatar = img_avatar.resize((300, 300), Image.ANTIALIAS)

                img_profile.paste(img_avatar, (120, 60))

                draw = ImageDraw.Draw(img_profile)
                nick_font = ImageFont.truetype("stuff/OpenSans.ttf", 80)
                text_font = ImageFont.truetype("stuff/Arial AMU.ttf", 55)
                nick_steam_font = ImageFont.truetype("stuff/OpenSans.ttf", 55)

                draw.text((430, 210), ctx.author.name, (255,255,255), font=nick_font)

                if str(ctx.author.status) == "online":
                    draw.text((430, 310), "Онлайн", (255,255,255), font=text_font)
                elif str(ctx.author.status) == "idle":
                    draw.text((430, 310), "Отошел, но при это посмотрел профиль", (255,255,255), font=text_font)
                elif str(ctx.author.status) == "dnd":
                    draw.text((430, 310), "Не беспокоить", (255,255,255), font=text_font)
                elif str(ctx.author.status) == "offline":
                    draw.text((430, 310), "Не в сети, но мы то знаем...", (255,255,255), font=text_font)
                else:
                    draw.text((430, 310), "Онлайн", (255,255,255), font=text_font)

                draw.text((390, 385), f"{all_data['money']} {name_of_currency} | {all_data['gold_money']} зол. {name_of_currency}", (255,255,255), font=text_font)

                draw.text((330, 545), all_data['nick'], (255,255,255), font=nick_steam_font)

                draw.text((340, 475), f"{all_data['rating']}", (255,255,255), font=text_font)

                if all_data['rank'] == "user":
                    draw.text((275, 645), "Машинист", (255,255,255), font=text_font)
                elif all_data['rank'] == "user+":
                    draw.text((275, 645), "Машинист+", (255,255,255), font=text_font)
                elif all_data['rank'] == "admin":
                    draw.text((275, 645), "VIP", (255,255,255), font=text_font)
                elif all_data['rank'] == "operator":
                    draw.text((275, 645), "Модератор", (255,255,255), font=text_font)
                elif all_data['rank'] == "moderator":
                    draw.text((275, 645), "Ст. модератор", (255,255,255), font=text_font)
                elif all_data['rank'] == "premium":
                    draw.text((275, 645), "Премиум", (255,255,255), font=text_font)
                elif all_data['rank'] == "moderator+":
                    draw.text((275, 645), "Гл. модератор", (255,255,255), font=text_font)
                elif all_data['rank'] == "superadmin":
                    draw.text((275, 645), "Администратор", (255,255,255), font=text_font)

                draw.text((350, 720), f"{all_data['steamid']}", (255,255,255), font=text_font)

                all_time = all_data['time']

                if all_data['time'] != "Не синхронизирован":

                    all_time = str(datetime.timedelta(seconds=all_data['time']))

                    if all_time.find("days") != -1:
                        all_time = all_time.replace("days", "дн")
                    else:
                        all_time = all_time.replace("day", "дн")

                    if all_time.find("weeks") != -1:
                        all_time = all_time.replace("weeks", "нед")
                    else:
                        all_time = all_time.replace("week", "нед")

                draw.text((560, 805), all_time, (255,255,255), font=text_font)

                img_profile.save("stuff/custom_profile.jpg")

                fileRequest.close()
                img_profile.close()

                with open("stuff/custom_profile.jpg", "rb") as jpg:
                    file = discord.File(jpg, filename="profile.jpg")
                    await ctx.send(file=file)

                os.remove("stuff/custom_profile.jpg")
            except Exception as ep:
                self.logger.error(ep)

            # await ctx.send(embed=await functions.embeds.profile(all_data,
            #                                                     name=user_ctx.name,
            #                                                     icon_url=ctx.guild.icon_url,
            #                                                     avatar_url=user_ctx.avatar_url,
            #                                                     mention=user_ctx.mention,
            #                                                     guild_name=ctx.guild.name))
        except IndexError as error:
            self.logger.error(error)

        finally:
            self.pgsql.close_conn(conn, user)

    @commands.command(name='удалить', help="<префикс>удалить <количество сообщений (меньше 100)>")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def delete(self, ctx):
        conn, user = self.pgsql.connect()
        guild_id = ctx.guild.id
        user.execute("SELECT info FROM info WHERE guild_id = %s", [guild_id])
        info = user.fetchone()[0]

        msg = ctx.message.content.split()
        if not msg[1].isdigit():
            await ctx.send(not_a_number.format(ctx.author.mention, self.client.command_prefix[0]))
            self.logger.info("{} entered not a number.".format(ctx.author.name))
            return

        if int(msg[1]) > 100:
            await ctx.send(number_of_delete_messages_hude.format(ctx.author.mention))
            return

        if info['logging']:

            messages = await ctx.channel.history(limit=int(msg[1]) + 1).flatten()

            with open("purgedeleted.txt", "w", encoding='utf8') as file:
                file.write("Удаленные сообщения:\n\n\n")
                for message in messages:
                    file.write("\n" + str(message.created_at) + ": " + message.content)

            file = open("purgedeleted.txt", "rb")
            msgs_deleted = discord.File(file, filename="All_deleted_message.txt")

            await ctx.channel.purge(limit=int(msg[1]) + 1)

            channel = self.client.get_channel(info['logging'])
            await channel.send(embed=await functions.embeds.purge(ctx, int(msg[1])), file=msgs_deleted)

            file.close()
            msgs_deleted.close()
            os.remove("purgedeleted.txt")

    @commands.command(name="промокод", help="<префикс>промокод <6 цифр>")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def promocode(self, ctx, *, promo: str):
        if await MainCommands.profile_exist(self, ctx.author, ctx.channel):
            pass

        if not promo.isdigit or not len(promo) == 6:
            await ctx.send(embed = await functions.embeds.description(ctx.author.mention, not_a_number))
            return

        try:
            conn, user = self.pgsql.connect()

            user.execute("SELECT bank_info FROM info WHERE guild_id = {}".format(ctx.guild.id))
            name_of_currency = user.fetchone()[0]['char_of_currency']

            user.execute("SELECT promocode FROM info WHERE guild_id = {}".format(ctx.guild.id))
            promo = user.fetchone()[0]

            if promo['code'] == 0:
                await ctx.send(embed = await functions.embeds.description(ctx.author.mention, promo_is_off))
                return
            elif promo['code'] == 1:
                await ctx.send(embed = await functions.embeds.description(ctx.author.mention, promo_is_enter))
                return
            elif str(promo['code'])[5] == "4":
                user.execute('UPDATE users SET money = money + {} WHERE "discordID" = {}'.format(promo["amount"], ctx.author.id))
                conn.commit()
                await ctx.send(promo_is_active.format(ctx.author.mention, promo["amount"], name_of_currency))
            elif str(promo['code'])[5] == "5":
                user.execute('UPDATE users SET goldmoney = goldmoney + {} WHERE "discordID" = {}'.format(promo["amount"], ctx.author.id))
                conn.commit()
                await ctx.send(promo_is_active.format(ctx.author.mention, promo["amount"], f"Зол. {name_of_currency}"))
            elif str(promo['code'])[5] == "6":
                user.execute('UPDATE users SET rating = rating + {} WHERE "discordID" = {}'.format(promo["amount"], ctx.author.id))
                conn.commit()
                await ctx.send(promo_is_active.format(ctx.author.mention, promo["amount"], "рейтинга"))

            user.execute("UPDATE info SET promocode = %s WHERE guild_id = %s", (json.dumps({"amount": 0, "code": 1}), ctx.guild.id))
            conn.commit()

        except Exception as error:
            self.logger.error(error)

        finally:
            self.pgsql.close_conn(conn, user)


    @commands.command(name='рулетка', help="<префикс>рулетка")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def roulette(self, ctx):
        if await MainCommands.profile_exist(self, ctx.author, ctx.channel):
            pass

        conn, user = self.pgsql.connect()

        user.execute("SELECT bank_info FROM info WHERE guild_id = {}".format(ctx.guild.id))
        name_of_currency = user.fetchone()[0]['char_of_currency']

        user.execute('SELECT "dateRol" FROM users WHERE "discordID" = {}'.format(ctx.author.id))
        date = user.fetchone()[0]

        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
        if date == now.day:
            await ctx.send(roulette_ended.format(ctx.author.mention))
            return

        user.execute('UPDATE users SET "dateRol" = {} WHERE "discordID" = {}'.format(now.day, ctx.author.id))
        conn.commit()

        win, thing = await functions.helper.random_win()

        if thing == 0:
            user.execute('UPDATE users SET money = money + {} WHERE "discordID" = {}'.format(win, ctx.author.id))
            conn.commit()
            await ctx.send(embed=await functions.embeds.roulette(ctx, win, name_of_currency))
        elif thing == 1:
            user.execute('UPDATE users SET goldMoney = goldMoney + {} WHERE "discordID" = {}'.
                         format(win, ctx.author.id))
            conn.commit()
            await ctx.send(embed=await functions.embeds.roulette(ctx, win, f"Зол. {name_of_currency}"))
        else:
            user.execute('UPDATE users SET rating = rating + {} WHERE "discordID" = {}'.format(win, ctx.author.id))
            conn.commit()
            await ctx.send(embed=await functions.embeds.roulette(ctx, win, "рейтинга"))

        self.pgsql.close_conn(conn, user)

    @commands.command(name='топ', help="<префикс>топ")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def top(self, ctx):
        all_data = list()

        try:
            database, gamer = self.mysql.connect()

            gamer.execute("SELECT steamid, all_time_on_server FROM statistics ORDER BY all_time_on_server DESC LIMIT 5")
            data = gamer.fetchall()

            embed = discord.Embed(colour=discord.Colour.dark_gold())

            all_data.append("Топ игроков сервера.")

            for info, count in zip(data, range(0, len(data))):
                gamer.execute("SELECT nick FROM users_steam WHERE steamid = %s;", [info[0]])
                nick = gamer.fetchone()[0]

                time = str(datetime.timedelta(seconds=info[1]))
                if time.find("days") != -1:
                    time = time.replace("days", "дн")
                else:
                    time = time.replace("day", "дн")

                if time.find("weeks") != -1:
                    time = time.replace("weeks", "нед")
                else:
                    time = time.replace("week", "нед")
                all_data.append(f"{count + 1}. `{nick}` ({info[0]}) - {time}")

            embed.description = '\n'.join([one_man for one_man in all_data])

            await ctx.send(embed=embed)

        except Exception as error:
            self.logger.error(error)
        finally:
            self.mysql.close_conn(database, gamer)

    @commands.command(name='продать', help="<префикс>продать <количество рейтинга>")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def sale(self, ctx):
        if await MainCommands.profile_exist(self, ctx.author, ctx.channel):
            pass

        conn, user = self.pgsql.connect()

        user.execute("SELECT bank_info FROM info WHERE guild_id = {}".format(ctx.guild.id))
        name_of_currency = user.fetchone()[0]['char_of_currency']

        msg = ctx.message.content.split()

        if len(msg) < 2:
            await ctx.send(just_a_command.format(ctx.author.mention, self.client.command_prefix[0]))
            self.logger.info("{} entered one word.".format(ctx.author.name))
            return

        if not msg[1].isdigit():
            await ctx.send(not_a_number.format(ctx.author.mention, self.client.command_prefix[0]))
            self.logger.info("{} entered not a number.".format(ctx.author.name))
            return

        conn, user = self.pgsql.connect()

        user.execute('SELECT rating FROM users WHERE "discordID" = {}'.format(ctx.author.id))
        rating = int(user.fetchone()[0])
        msg[1] = int(msg[1])

        if rating < msg[1] or rating <= 0:
            await ctx.send(not_correct.format(ctx.author.mention, "рейтинга"))
            self.logger.info("{} entered a number more than have rating.")
            self.pgsql.close_conn(conn, user)
            return

        user.execute('UPDATE users SET rating = rating - {}, money = money + {} WHERE "discordID" = {}'.
                     format(msg[1], msg[1] * 1000, ctx.author.id))
        conn.commit()

        await ctx.send(rating_sale.format(ctx.author.mention, msg[1] * 1000, name_of_currency.title(), 1000))

        self.pgsql.close_conn(conn, user)

    @commands.command(name='обмен', help="<префикс>обмен <количетсво ВС>")
    async def swap(self, ctx):
        if await MainCommands.profile_exist(self, ctx.author, ctx.channel):
            pass

        msg = ctx.message.content.split()
        if len(msg) < 2:
            await ctx.send(just_a_command.format(ctx.author.mention, self.client.command_prefix[0]))
            self.logger.info("{} entered one word.".format(ctx.author.name))
            return

        if not msg[1].isdigit():
            await ctx.send(not_a_number.format(ctx.author.mention, self.client.command_prefix[0]))
            self.logger.info("{} entered not a number.".format(ctx.author.name))
            return

        conn, user = self.pgsql.connect()

        user.execute('SELECT money FROM users WHERE "discordID" = {}'.format(ctx.author.id))
        revers = int(user.fetchone()[0])
        msg[1] = int(msg[1])

        if revers < msg[1]:
            await ctx.send(more_than_have.format(ctx.author.mention, "реверсивок"))
            self.logger.info("{} entered a number more than have rating.")
            self.pgsql.close_conn(conn, user)
            return

        user.execute('UPDATE users SET money = money - {} WHERE "discordID" = {}'.
                     format(int(msg[1]), ctx.author.id))
        conn.commit()

        user.execute('UPDATE users SET goldMoney = goldMoney + {} WHERE "discordID" = {}'.
                     format(int(msg[1] / 4), ctx.author.id))
        conn.commit()

        await ctx.send(embed=await functions.embeds.swap(ctx, int(msg[1] / 4), msg[1], swaps))

    @commands.command(name="статистика", help="<префикс>статистика")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def static(self, ctx):
        if await MainCommands.profile_exist(self, ctx.author, ctx.channel):
            pass

        conn, user = self.pgsql.connect()
        database, gamer = self.mysql.connect()
        user.execute("SELECT steamid FROM users WHERE \"discordID\" = %s", [ctx.author.id])

        steamid, data = None, None

        try:
            steamid = user.fetchone()[0]
        except IndexError as error:
            self.logger.error(error)
            await ctx.send(embed=await functions.embeds.description(ctx.author.mention, you_not_synchronized))
            return

        if steamid != "None" and steamid:
            try:
                gamer.execute("SELECT * FROM statistics WHERE steamid = %s", [steamid])
                data = gamer.fetchall()[0]
            except IndexError:
                await ctx.send(statistic_went_wrong.format(ctx.author.mention))
            except Exception as error:
                self.logger.error(error)
                await ctx.send(something_went_wrong)
                return

            labels, all_time = await create_figure(data)

            if all_time == 0 and not labels:
                await ctx.send(embed=await functions.embeds.description(ctx.author.mention, for_statistics))
                return

            image = open("statistics.png", 'rb')
            await ctx.send(f"{ctx.author.mention}, вы провели за пультом {all_time}"
                           f"\nВот список составов, в которых вы находились:\n```" +
                           '\n'.join([x for x in labels]) + "```"
                           "\nГрафик ниже предоставит вам дополнительную информацию:",
                           file=discord.File(fp=image, filename="statistics.png"))
            image.close()
        else:
            await ctx.send(embed=await functions.embeds.description(ctx.author.mention, you_not_synchronized))
        try:
            os.remove("statistics.png")
        except PermissionError as error:
            self.logger.error(error)

    @commands.command(name="выбор", help="<префикс>выбор <вопрос> <+1> <+2>...<+9>.")
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def polls(self, ctx):
        message = ctx.message.content.split()
        answers = ctx.message.content.split("+")
        quest, time = "", 0
        for i in range(1, len(message)):
            if message[i].find("+") == -1:
                quest += message[i] + " "
            else:
                break

        if quest == "":
            await ctx.send(question_not_post.format(ctx.author.mention, self.client.command_prefix[0]))
            return

        answers = answers[1:len(answers)]
        if len(answers) > 9:
            await ctx.send(embed=await functions.embeds.description(ctx.author.mention, answers_out_of_range))
            return
        msg = await ctx.send(embed=await functions.embeds.poll(ctx, quest, time, answers))

        for i in range(1, len(answers) + 1):
            await msg.add_reaction(f"{i}\N{combining enclosing keycap}")

    @commands.command(name="выбор_на_время", help="<префикс>выбор_на_время <вопрос> <время (часы)> <+1> <+2>...<+9>")
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def polls_time(self, ctx):
        message = ctx.message.content.split()
        answers = ctx.message.content.split("+")
        quest, time = "", 0
        for i in range(1, len(message)):
            if message[i].find("+") == -1:
                quest += message[i] + " "
            else:
                break

        if quest == "":
            await ctx.send(question_not_post.format(ctx.author.mention, self.client.command_prefix[0]))
            return

        answers = answers[1:len(answers)]
        if len(answers) > 9:
            await ctx.send(embed=await functions.embeds.description(ctx.author.mention, answers_out_of_range))
            return
        msg = await ctx.send(embed=await functions.embeds.poll(ctx, quest, time, answers))

        for i in range(1, len(answers) + 1):
            await msg.add_reaction(f"{i}\N{combining enclosing keycap}")

    @commands.command(name="ботбан", help="<префикс>ботбан <хайлайт роли>")
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def botban(self, ctx):
        msg = ctx.message.content.split()

        if len(msg) > 2:
            await ctx.send(embed=await functions.embeds.description(ctx.author.mention, to_many_parametrs))
            return

        try:
            conn, user = self.pgsql.connect()
            id = ctx.message.role_mentions[0].id

            user.execute("INSERT INTO botban (id) VALUES({})".format(id))
            conn.commit()

            await ctx.send(successfully_added_to_botban.format(ctx.author.mention))
        except Exception as error:
            self.logger.error(error)
        finally:
            self.pgsql.close_conn(conn, user)

    @commands.command(name="ботразбан", help="<префикс>ботбан <хайлайт роли>")
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def botunban(self, ctx):
        msg = ctx.message.content.split()

        if len(msg) > 2:
            await ctx.send(embed=await functions.embeds.description(ctx.author.mention, to_many_parametrs))
            return

        try:
            conn, user = self.pgsql.connect()
            id = ctx.message.role_mentions[0].id

            user.execute("DELETE * FROM botban WHERE id = {}".format(id))
            conn.commit()

            await ctx.send(successfully_remove_to_botban.format(ctx.author.mention))
        except Exception as error:
            self.logger.error(error)
        finally:
            self.pgsql.close_conn(conn, user)

    # @commands.command(name="запрет_заявки", help="<префикс>запрет_заявки <хайлайт роли>")
    # @commands.has_permissions(administrator=True)
    # @commands.cooldown(1, 30, commands.BucketType.user)
    # async def ban_request(self, ctx):
    #     msg = ctx.message.content.split()
    #
    #     if len(msg) > 2:
    #         await ctx.send(embed=await functions.embeds.description(ctx.author.mention, to_many_parametrs))
    #         return
    #
    #     try:
    #         conn, user = self.pgsql.connect()
    #         id = ctx.message.role_mentions[0].id
    #
    #         user.execute("INSERT INTO botban (id) VALUES({})".format(id))
    #         conn.commit()
    #
    #         await ctx.send(successfully_added_to_botban.format(ctx.author.mention))
    #     except Exception as error:
    #         self.logger.error(error)
    #     finally:
    #         self.pgsql.close_conn(conn, user)
    #
    # @commands.command(name="отмена_запрета", help="<префикс>отмена_запрета <хайлайт роли>")
    # @commands.has_permissions(administrator=True)
    # @commands.cooldown(1, 30, commands.BucketType.user)
    # async def unban_request(self, ctx):
    #     msg = ctx.message.content.split()
    #
    #     if len(msg) > 2:
    #         await ctx.send(embed=await functions.embeds.description(ctx.author.mention, to_many_parametrs))
    #         return
    #
    #     try:
    #         conn, user = self.pgsql.connect()
    #         id = ctx.message.role_mentions[0].id
    #
    #         user.execute("DELETE * FROM botban WHERE id = {}".format(id))
    #         conn.commit()
    #
    #         await ctx.send(successfully_remove_to_botban.format(ctx.author.mention))
    #     except Exception as error:
    #         self.logger.error(error)
    #     finally:
    #         self.pgsql.close_conn(conn, user)

    @commands.command(name="сервер", help="<префикс>сервер")
    async def server_info(self, ctx):
        embed = await functions.embeds.server_info(ctx.guild)
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(missing_permission.format(ctx.author.mention))
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(not_enough_words.format(ctx.author.mention, ctx.message.content))
        elif isinstance(error, commands.CommandNotFound):
            msg = ctx.message.content.split()
            await ctx.send(command_not_found.format(ctx.author.mention, msg[0]))
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(cooldown.format(ctx.author.mention, int(error.retry_after)))
        else:
            self.logger.error(error)
