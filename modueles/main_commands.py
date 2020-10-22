import asyncio
import datetime
import requests
import logging
import os
import json
from pprint import pprint

import discord
from discord.ext import commands, tasks
from models import *
import random

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from io import BytesIO

import functions.database
import functions.helper
from functions.create_plot import create_figure


class MainCommands(commands.Cog, name="Основные команды"):

    def __init__(self, client):
        self.poll_time = dict()
        self.client = client

        logger = logging.getLogger("main_commands")
        logger.setLevel(logging.INFO)

        self.logger = logger

        self.mysql = functions.database.MySQLConnection()
        self.pgsql = functions.database.PgSQLConnection()

        self.poll_time['choice_on'] = False
        self.poll_time['message'] = None

        self.generate_promo.start()

    async def profile_check(self, author):
        UserDiscord.insert(discord_id=author.id)

    @tasks.loop(minutes=random.randint(420, 900))
    async def generate_promo(self):
        conn, user = self.pgsql.connect()

        promo_event = ["Продам {} {}ок бесплатно.\nПромокод: `{}`",
                       "Тут мне администраторы нашептали, что стоит вам дать кое-что интересное на {} {}ок\nПромокод: "
                       "`{}`",

                       "3 сентебря прошло, а ты все еще переварачиваешь календарь, получая {} {}ок?\nПромокод: `{}`",

                       "А вы знали что на Sunrise есть бесплатное пиво? И мы не знали. "
                       "В прочем, еще есть промокод на {} {}ок\nПромокод: `{}`",

                       "Ало Галочка, ты сейчас умрешь. У меня есть промокод на {} {}ок\nПромокод: `{}`",

                       "Назовите слово из 8 букв начинающееся на П.\nНеправильно - прогресс.\n"
                       "Хотя и промокод сойдет...\n{} {}ок с промокодом `{}`",

                       "У меня ушел жир весь жир! Я просто втирал какоу-то дичь в лицо. Вот рецепт: надо всего лишь... "
                       "получить промокод на {} {}ок\nПромокод: `{}`",

                       "Однажды, парень рассказал, что нашёл {} {}ок\nПлакала половина маршрутки, "
                       "а этим парнем был Альберт Эйнштейн\nПромокод: `{}`",

                       "А ты готов прыгнуть в пучину отчаиния за {} {}ок? И я нет, поэтому и не надо.\nПромокод: `{}`"]

        user.execute("SELECT * FROM promocode WHERE id = 1 AND create_admin = False")
        promocode = user.fetchall()
        if not promocode:
            return

        promocode = promocode[0]

        channel = discord.utils.get(self.client.get_all_channels(), name='бот')
        comment = random.choice(promo_event)

        if promocode[1] > 1:
            code = promocode[1]
            amount = promocode[2]
            thing = promocode[3]
        elif promocode[1] == 1:
            amount, thing = await functions.helper.promo_win()
            code = str(random.randint(10000, 100000)) + str(thing + 4)

            user.execute(f"UPDATE promocode SET code = {code}, amount = {amount}, thing = {thing} "
                         f"WHERE create_admin = False")
            conn.commit()
        elif promocode[1] == 0:
            return

        await channel.send(embed=await functions.embeds.promocode("Новый промокод!",
                                                                  comment.format(
                                                                      amount,
                                                                      "реверсив" if thing == 1 else "зл. реверсив",
                                                                      code),
                                                                  promocode[4]))

        self.pgsql.close_conn(conn, user)

    @commands.command(name='промокоды',
                      help="Дополнительные аргументы в этой команде не нужны.",
                      brief="<префикс>промокоды",
                      description="Включает (или выключают) промокоды, которые отсылаются в системный канал сервера.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def promo_switch(self, ctx):
        def check(msg):
            return msg.content.lower() == "да" or msg.content.lower() == "нет" \
                   and msg.author.guild_permissions.administrator

        conn, user = self.pgsql.connect()
        user.execute("SELECT code FROM promocode WHERE id = 1 AND create_admin = False")
        code = user.fetchone()

        if not code:
            user.execute("INSERT INTO promocode (code, create_admin) VALUES (1, False)")
            conn.commit()
            await ctx.send(embed=await functions.embeds.description("Промокоды теперь ДОСТУПНЫ.",
                                                                    "В течении 8 часов должен прийти первый "
                                                                    "промокод, который можно активировать с "
                                                                    "помощью команды **{}промокод**"
                                                                    .format(self.client.command_prefix[0])))
        elif code[0] == 0:
            user.execute("UPDATE promocode SET code = 1 WHERE id = 1 AND create_admin = False")
            conn.commit()
            await ctx.send(embed=await functions.embeds.description("Промокоды теперь ДОСТУПНЫ.",
                                                                    "В течении 8 часов должен прийти первый "
                                                                    "промокод, который можно активировать с "
                                                                    "помощью команды **{}промокод**"
                                                                    .format(self.client.command_prefix[0])))
        elif code[0] != 0:
            await ctx.send(embed=await functions.embeds.description("Вы уверены, что хотите отключить промокоды?",
                                                                    "\nЕсли ДА, то введите слово **ДА**"
                                                                    "\nЕсли НЕТ, то введите слово НЕТ"),
                           delete_after=15.0)
            try:
                message = await self.client.wait_for('message', timeout=15.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send("Отключение промокодов отменено.", delete_after=5.0)
            else:
                if message.content.lower() == "да":
                    user.execute("UPDATE promocode SET code = 0, amount = 0 WHERE id = 1 AND create_admin = False")
                    conn.commit()
                    await ctx.send(embed=await functions.embeds.description("Промокоды теперь НЕ ДОСТУПНЫ.",
                                                                            "Чтобы опять включить промокоды введите ту "
                                                                            "же самую команду."))
                else:
                    await ctx.send("Отключение промокодов отменено.", delete_after=5.0)

        self.pgsql.close_conn(conn, user)

    @commands.command(name='создать_промокод',
                      help="Данные которые нужны для использования этой команды:"
                           "\n<amount>: Количество валюты"
                           "\n<thing>: Число, обозночающее что вы хотите использовать в качестве валюты "
                           "(10000 < число < 100000)"
                           "(1 - реверсивки, 2 - золотые реверсивки",
                      brief="<префикс>создать_промокод 20000 1",
                      description="С помощью этой команды вы можете создать промокод, который отсылается вам в ЛС.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def create_promocode(self, ctx, amount: int, thing: int):
        conn, user = self.pgsql.connect()

        user.execute("SELECT COUNT(*) FROM promocode")
        count = user.fetchone()[0]

        if count > 15:
            await ctx.send(embed=await functions.embeds.description("Промокодов уже достаточно.",
                                                                    "Больше 15 промокодов не может быть создано."))
            return

        if not 10000 <= amount <= 100000:
            await ctx.send(embed=await functions.embeds.description(f"Вы ввели слишком "
                                                                    f"{'большое' if amount > 100000 else 'маленькое'} "
                                                                    f"значение.",
                                                                    "Пожалуйста уменьшите значение в предел от "
                                                                    "**10000** до **100000**."))
            return

        if thing != 0 and thing != 1:
            await ctx.send(embed=await functions.embeds.description(f"Такой валюты не существует.",
                                                                    "То что вы ввели в качетсве аргумента валюты, "
                                                                    "не существует."
                                                                    "\n**0** - реверсивки"
                                                                    "\n**1** - золотые реверсивки"))
            return

        code = str(random.randint(10000, 100000)) + str(thing + 4)

        user.execute(f"INSERT INTO promocode (code, amount, thing, create_admin) "
                     f"VALUES ({code}, {amount}, {thing}, True)")
        conn.commit()

        try:
            await ctx.author.send(embed=
                                  await functions.embeds.promocode("Вы создали промокод.",
                                                                   f"Вы создали промокод на {amount} "
                                                                   f"{'реверсивок' if thing == 0 else 'зл. реверсивок'}",
                                                                   True))
        except discord.Forbidden:
            await ctx.send(embed=await functions.embeds.description(f"Невозможно отправить Вам промокод.",
                                                                    "Пожалуйста провертье, что Вам могут писать люди, "
                                                                    "даже если они не добавили Вас в друзья."))
            user.execute(f"DELETE * FROM promocode WHERE code = {code} AND create_admin = True")
            conn.commit()

        self.pgsql.close_conn(conn, user)

    @commands.command(name='просмотреть_промокоды',
                      help="Дополнительные аргументы в этой команде не нужны.",
                      brief="<префикс>просмотреть_промокоды",
                      description="С помощью этой команды вы можете узнать все промокоды, созданные Вами и не только.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def check_promocode(self, ctx):
        conn, user = self.pgsql.connect()

        user.execute("SELECT * FROM promocode")
        all_promocodes = user.fetchall()

        embed = discord.Embed(colour=discord.Colour.dark_green(), title="Все промокоды доступные на сервере.")
        embed.set_author(name=ctx.guild.name)

        text_promocode = list()

        if all_promocodes[0][1] == 0:
            embed.add_field(name="Промокод выводимый автоматически ВЫКЛЮЧЕНЫ",
                            value=f"Чтобы их включить введите команду {self.client.command_prefix[0]}промокод.")
        elif all_promocodes[0][1] == 1:
            embed.add_field(name="Промокод, создаваемый автоматически был использован.",
                            value=f"Промокод, создаваемый автоматически был использован.")
        elif all_promocodes[0][1] > 1:
            embed.add_field(name="Промокод, создаваемый автоматически:",
                            value=f"Промокод **{all_promocodes[0][1]}** состовляет **{all_promocodes[0][2]} "
                                  f"{'реверсивок' if all_promocodes[0][3] == 0 else 'зл. реверсивок'}**",
                            inline=False)

        if len(all_promocodes) > 1:
            for promocode in all_promocodes[1::]:
                text_promocode.append(f"Промокод **{promocode[1]}** состовляет "
                                      f"**{promocode[2]} {'реверсивок' if promocode[3] == 0 else 'зл. реверсивок'}**")

            embed.add_field(name="Промокоды, созданные Администрацией",
                            value="\n".join([x for x in text_promocode]),
                            inline=False)

        else:
            embed.add_field(name="Промокоды, созданные Администрацией, ОТСУТСТВУЮТ.",
                            value="Промокоды, созданные Администрацией, ОТСУТСТВУЮТ.")

        try:
            await ctx.author.send(embed=embed)
        except discord.Forbidden:
            await ctx.send(embed=await functions.embeds.description(f"Невозможно отправить Вам информацию по "
                                                                    f"промокодам.",
                                                                    "Пожалуйста провертье, что Вам могут писать люди, "
                                                                    "даже если они не добавили Вас в друзья."))

    @commands.command(name="промокод",
                      help="Данные которые нужны для использования этой команды:"
                           "\n<promo>: промокод.",
                      brief="<префикс>промокод 123456",
                      description="Команда, позволяющая активировать промокод.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def promocode(self, ctx, code: int):
        await MainCommands.profile_check(self, ctx.author)

        if code == 0 or code == 1:
            await ctx.send(embed=await functions.embeds.description("Запрещенные команды.",
                                                                    "Так делать нельзя."))
            return

        conn, user = self.pgsql.connect()

        user.execute(f"SELECT * FROM promocode WHERE code = {code}")
        promocode = user.fetchone()

        if not promocode:
            await ctx.send(embed=await functions.embeds.description("Такого промокода не существует.",
                                                                    "Перепроверте правильность введного вами"
                                                                    "промокода."))
            return

        if promocode[3] == 0:
            user.execute('UPDATE users SET money = money + {} WHERE "discordID" = {}'.format(promocode[2],
                                                                                             ctx.author.id))
            conn.commit()
            await ctx.send(
                embed=await functions.embeds.description("Промокод был активирован.",
                                                         f"Вы активировали промокод **{promocode[1]}** "
                                                         f"на **{promocode[2]}** реверсивок"))
        elif promocode[3] == 1:
            user.execute('UPDATE users SET goldmoney = goldmoney + {} WHERE "discordID" = {}'.format(promocode[2],
                                                                                                     ctx.author.id))
            conn.commit()
            await ctx.send(
                embed=await functions.embeds.description("Промокод был активирован.",
                                                         f"Вы активировали промокод **{promocode[1]}** "
                                                         f"на **{promocode[2]}** зл. реверсивок"))

        if promocode[0] == 1:
            user.execute("UPDATE promocode SET code = 1, amount = 0 WHERE id = 1")
            conn.commit()
        else:
            user.execute(f"DELETE FROM promocode WHERE code = {promocode[1]}")
            conn.commit()

        self.pgsql.close_conn(conn, user)

    @commands.command(name='профиль',
                      help="Дополнительные аргументы в этой команде могут быть использованы, только если вам нужно "
                           "узнать профиль другого участника сервера.",
                      brief="<префикс>профиль @Chell",
                      description="С помощью этой команды вы можете узнать всю информацию о себе, а также просмотреть "
                                  "информацию о другом участнике.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def profile(self, ctx, *args):
        await MainCommands.profile_check(self, ctx.author)

        if len(args) > 1:
            raise commands.TooManyArguments()

        conn, user = self.pgsql.connect()
        data = None

        async with ctx.typing():
            name_of_currency = "рев."

            if args:
                if not isinstance(args[0], discord.Member):
                    client = await commands.MemberConverter().convert(ctx, args[0])
                else:
                    client = args[0]
                if not client:
                    await ctx.send(embed=await functions.embeds.description(f"Пользователь не был найден.",
                                                                            "Профиль данного пользователя не может "
                                                                            "быть просмотрен в угоду того, что не был "
                                                                            "найден на этом сервере."))
                    return
                await MainCommands.profile_check(self, client)
                user.execute('SELECT * FROM users WHERE "discordID" = %s', [client.id])
                user_ctx = client
            elif len(ctx.message.content.split()) == 1:
                user.execute('SELECT * FROM users WHERE "discordID" = %s', [ctx.author.id])
                user_ctx = ctx.author

            try:
                data = user.fetchall()[0]
            except IndexError as error:
                self.logger.error(error)
            try:
                if data[6] and data[6] != "None":
                    conn_mysql, user_mysql = self.mysql.connect()
                    user_mysql.execute("SELECT * FROM users_steam WHERE steamid = '{}'".format(data[6]))
                    steam = user_mysql.fetchall()[0]

                    user_mysql.execute("SELECT all_time_on_server FROM statistics WHERE steamid = %s", [data[6]])
                    time = user_mysql.fetchone()

                    all_data = dict(rating=data[1], money=data[2], gold_money=data[3], steamid=data[6], nick=steam[1],
                                    time=time[0], rank=steam[2], name_of_currency=name_of_currency)

                    self.mysql.close_conn(conn_mysql, user_mysql)
                else:
                    all_data = dict(rating=data[1], money=data[2], gold_money=data[3], steamid='Не синхронизирован',
                                    nick='Не синхронизирован', time='Не синхронизирован', rank='Не синхронизирован',
                                    name_of_currency=name_of_currency)

                try:
                    img_profile = Image.open("stuff/profilehalloween.jpg")

                    fileRequest = requests.get(user_ctx.avatar_url)
                    img_avatar = Image.open(BytesIO(fileRequest.content))

                    img_avatar = img_avatar.resize((300, 300), Image.ANTIALIAS)

                    img_profile.paste(img_avatar, (120, 185))

                    draw = ImageDraw.Draw(img_profile)
                    nick_font = ImageFont.truetype("stuff/OpenSans.ttf", 80)
                    text_font = ImageFont.truetype("stuff/Arial AMU.ttf", 55)
                    nick_steam_font = ImageFont.truetype("stuff/OpenSans.ttf", 55)

                    draw.text((430, 325), user_ctx.name, (255, 255, 255), font=nick_font)

                    if str(user_ctx.status) == "online":
                        draw.text((430, 435), "Онлайн", (255, 255, 255), font=text_font)
                    elif str(user_ctx.status) == "idle":
                        draw.text((430, 435), "Отошел, но при это посмотрел профиль", (255, 255, 255), font=text_font)
                    elif str(user_ctx.status) == "dnd":
                        draw.text((430, 435), "Не беспокоить", (255, 255, 255), font=text_font)
                    elif str(user_ctx.status) == "offline":
                        draw.text((430, 435), "Не в сети, но мы то знаем...", (255, 255, 255), font=text_font)
                    else:
                        draw.text((430, 435), "Онлайн", (255, 255, 255), font=text_font)

                    draw.text((140, 510), f"Средства: {all_data['money']} {name_of_currency} | {all_data['gold_money']}"
                                          f" зол. {name_of_currency}", (255, 255, 255), font=text_font)

                    draw.text((140, 670), f"Имя на сервере: {all_data['nick']}", (255, 255, 255), font=nick_steam_font)

                    draw.text((140, 600), f"Рейтинг: {all_data['rating']}", (255, 255, 255), font=text_font)

                    if all_data['rank'] == "user":
                        draw.text((140, 770), "Ранг: Машинист", (255, 255, 255), font=text_font)
                    elif all_data['rank'] == "user+":
                        draw.text((140, 770), "Ранг: Машинист+", (255, 255, 255), font=text_font)
                    elif all_data['rank'] == "admin":
                        draw.text((140, 770), "Ранг: VIP", (255, 255, 255), font=text_font)
                    elif all_data['rank'] == "operator":
                        draw.text((140, 770), "Ранг: Модератор", (255, 255, 255), font=text_font)
                    elif all_data['rank'] == "moderator":
                        draw.text((140, 770), "Ранг: Ст. модератор", (255, 255, 255), font=text_font)
                    elif all_data['rank'] == "premium":
                        draw.text((140, 770), "Ранг: Премиум", (255, 255, 255), font=text_font)
                    elif all_data['rank'] == "moderator+":
                        draw.text((140, 770), "Ранг: Гл. модератор", (255, 255, 255), font=text_font)
                    elif all_data['rank'] == "superadmin":
                        draw.text((140, 770), "Ранг: Администратор", (255, 255, 255), font=text_font)
                    elif all_data['rank'] == "Не синхронизирован":
                        draw.text((140, 770), "Ранг: Не синхронизирован", (255, 255, 255), font=text_font)

                    draw.text((140, 845), f"SteamID: {all_data['steamid']}", (255, 255, 255), font=text_font)

                    all_time, embed = None, None

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

                        embed = discord.Embed(colour=discord.Colour.from_rgb(54, 57, 63))
                        embed.description = f"**__Информация для копирования:__**\n**SteamID**: {all_data['steamid']}" \
                                            f"\n**Ник**: {all_data['nick']}" \
                                            f"\n**Роль для изменения в базе данных**: {all_data['rank']}"
                        embed.set_footer(text="Зачем? Чтобы было.")

                    else:
                        all_time = "Не синхронизирован"

                    draw.text((140, 930), f"Время на сервере: {all_time}", (255, 255, 255), font=text_font)

                    img_profile.save("stuff/custom_profile.jpg")

                    fileRequest.close()
                    img_profile.close()

                    with open("stuff/custom_profile.jpg", "rb") as jpg:
                        file = discord.File(jpg, filename="profile.jpg")
                        if embed:
                            await ctx.send(embed=embed, file=file)
                        else:
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

    @commands.command(name='удалить',
                      help="Данные которые нужны для использования этой команды:"
                           "\n<count>: Количество сообщений для удаления.",
                      brief="<префикс>удалить 25",
                      description="Команда позволяет удалить сразу довольно большое количество сообщений. "
                                  "Чтобы не потерять данные они сохраняются в файл .txt")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def delete(self, ctx, count: int):
        if count > 100:
            await ctx.send(embed=await functions.embeds.description("Число удаляемых сообщений превышает 100",
                                                                    "Пожалуйста не надо удалять сразу так много "
                                                                    "сообщений."))
            return

        messages = await ctx.channel.history(limit=count + 1).flatten()
        messages = reversed(messages)

        with open("purgedeleted.txt", "w", encoding='utf8') as file:
            file.write("Удаленные сообщения:\n\n\n")
            for message in messages:
                file.write("\n" + str(message.author.name) + "#" + str(message.author.discriminator) + " (" + str(
                    message.created_at) + "): " + message.content)

        file = open("purgedeleted.txt", "rb")
        msgs_deleted = discord.File(file, filename="All_deleted_message.txt")

        await ctx.channel.purge(limit=count + 1)

        channel = discord.utils.get(self.client.get_all_channels(), name='око')
        await channel.send(embed=await functions.embeds.purge(ctx, count), file=msgs_deleted)

        file.close()
        msgs_deleted.close()
        os.remove("purgedeleted.txt")

    @commands.command(name='рулетка',
                      help="Дополнительные аргументы в этой команде не нужны.",
                      brief="<префикс>рулетка",
                      description="Команда для получения ежедневной прибыли.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def roulette(self, ctx):
        await MainCommands.profile_check(self, ctx.author)

        conn, user = self.pgsql.connect()

        user.execute('SELECT "dateRol" FROM users WHERE "discordID" = {}'.format(ctx.author.id))
        date = user.fetchone()[0]

        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
        if date == now.day:
            await ctx.send(embed=await functions.embeds.description("Рулетка для Вас на сегодня уже закончена.",
                                                                    f"Активировать команды вы смоежете через **"
                                                                    f"{24 - now.hour}:"
                                                                    f"{60 - now.minute}:"
                                                                    f"{60 - now.second}**."))
            return

        user.execute('UPDATE users SET "dateRol" = {} WHERE "discordID" = {}'.format(now.day, ctx.author.id))
        conn.commit()

        win, thing = await functions.helper.random_win()

        if thing == 0:
            user.execute('UPDATE users SET money = money + {} WHERE "discordID" = {}'.format(win, ctx.author.id))
            conn.commit()
            await ctx.send(embed=await functions.embeds.roulette(ctx, win, "реверсивок"))
        elif thing == 1:
            user.execute('UPDATE users SET goldMoney = goldMoney + {} WHERE "discordID" = {}'.
                         format(win, ctx.author.id))
            conn.commit()
            await ctx.send(embed=await functions.embeds.roulette(ctx, win, f"зл. реверсивок"))
        else:
            user.execute('UPDATE users SET rating = rating + {} WHERE "discordID" = {}'.
                         format(win, ctx.author.id))
            conn.commit()
            await ctx.send(embed=await functions.embeds.roulette(ctx, win, f"рейтинг"))

        self.pgsql.close_conn(conn, user)

    @commands.command(name='топ',
                      help="Дополнительные аргументы в этой команде не нужны.",
                      brief="<префикс>топ",
                      description="Команда для получения топа игроков сервера по часам.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def top(self, ctx):
        all_data = list()
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

        self.mysql.close_conn(database, gamer)

    @commands.command(name='продать',
                      help="Данные которые нужны для использования этой команды:"
                           "\n<rating>: Количетсво рейтинга для продажи.",
                      brief="<префикс>продать 20",
                      description="Команда, позволяющая продать рейтинг за 1000 обычной валюты.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def sale(self, ctx, rating: int):
        await MainCommands.profile_check(self, ctx.author)

        conn, user = self.pgsql.connect()

        user.execute('SELECT rating FROM users WHERE "discordID" = {}'.format(ctx.author.id))
        real_have_rating = user.fetchone()[0]

        if real_have_rating < rating or rating <= 0:
            await ctx.send(embed=await functions.embeds.description("Недостаточно рейтинга.",
                                                                    f"Вы хотите продать рейтинг, которого у Вас меньше,"
                                                                    f"чем вы ввели."))
            return

        user.execute('UPDATE users SET rating = rating - {}, money = money + {} WHERE "discordID" = {}'.
                     format(rating, rating * 1000, ctx.author.id))
        conn.commit()

        await ctx.send(embed=await functions.embeds.description("Рейтинг успешно продан.",
                                                                f"Вы продали {rating} рейтинга за "
                                                                f"{rating * 1000} реверсивок"))

        self.pgsql.close_conn(conn, user)

    @commands.command(name='обмен',
                      help="Данные которые нужны для использования этой команды:"
                           "\n<revers>: Количество реверсивок на обмен.",
                      brief="<префикс>обмен 2000",
                      description="Команда, позволяющая обменять 4 обычных реверсивки на 1 золотой реверсивки.")
    async def swap(self, ctx, revers: int):
        await MainCommands.profile_check(self, ctx.author)

        conn, user = self.pgsql.connect()

        user.execute('SELECT money FROM users WHERE "discordID" = {}'.format(ctx.author.id))
        real_have_revers = int(user.fetchone()[0])

        if real_have_revers < revers:
            await ctx.send(embed=await functions.embeds.description("Недостаточно реверсивок.",
                                                                    f"Вы хотите обменять реверсивки, которых у Вас "
                                                                    f"меньше, чем вы ввели."))
            return

        user.execute('UPDATE users SET money = money - {} WHERE "discordID" = {}'.
                     format(revers, ctx.author.id))
        conn.commit()

        user.execute('UPDATE users SET goldMoney = goldMoney + {} WHERE "discordID" = {}'.
                     format(int(revers / 4), ctx.author.id))
        conn.commit()

        await ctx.send(embed=await functions.embeds.description("Реверсивки успешно обменены.",
                                                                f"Вы обменяли {revers} реверсивок на "
                                                                f"{int(revers / 4)} золотых реверсивок"))

        self.pgsql.close_conn(conn, user)

    @commands.command(name="статистика",
                      help="Дополнительные аргументы в этой команде не нужны.",
                      brief="<префикс>статистика",
                      description="Команда, позволяющая посмотреть свою статистику по игре на сервере.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def static(self, ctx):
        await MainCommands.profile_check(self, ctx.author)

        conn, user = self.pgsql.connect()
        database, gamer = self.mysql.connect()
        user.execute("SELECT steamid FROM users WHERE \"discordID\" = %s", [ctx.author.id])

        steamid, data = None, None

        try:
            steamid = user.fetchone()[0]
        except IndexError as error:
            self.logger.error(error)
            await ctx.channel.send(embed=await functions.embeds.description("Вы не синхронизированы",
                                                                            "Чтобы просмотреть свою статистику вам "
                                                                            "нужно для начала синхронизировать свой "
                                                                            "аккаунт Garry's Mod и Discord с помощью"
                                                                            "команды **{}синхр** <ссылка на Steam "
                                                                            "аккаунт>"
                                                                            .format(self.client.command_prefix[0])))
            return

        if steamid != "None" and steamid:
            try:
                gamer.execute("SELECT * FROM statistics WHERE steamid = %s", [steamid])
                data = gamer.fetchall()[0]
            except IndexError:
                await ctx.send(embed=await functions.embeds.description("Статистика не может быть прогружена.",
                                                                        "Похоже, что статистика Вашей игры на сервере, "
                                                                        "либо не доступна, либо есть ещё несколько "
                                                                        "причин."))

            labels, all_time = await create_figure(data)

            if all_time == 0 and not labels:
                await ctx.send(embed=await functions.embeds.description("Вы проиграли слишком мало времени",
                                                                        "Вы проиграли на сервере меньше 10 минут."))
                return

            image = open("statistics.png", 'rb')
            await ctx.send(f"{ctx.author.mention}, вы провели за пультом {all_time}"
                           f"\nВот список составов, в которых вы находились:\n```" +
                           '\n'.join([x for x in labels]) + "```"
                                                            "\nГрафик ниже предоставит вам дополнительную информацию:",
                           file=discord.File(fp=image, filename="statistics.png"))
            image.close()
        else:
            await ctx.channel.send(embed=await functions.embeds.description("Игрок не синхронизирован",
                                                                            "Игрок с таким Discord-ом не "
                                                                            "синхронизирован. Введите его SteamID, "
                                                                            "чтобы забанить."))
            return
        try:
            os.remove("statistics.png")
        except PermissionError as error:
            self.logger.error(error)

    @commands.command(name="выбор",
                      help="Дополнительные аргументы в этой команде используются следующим образом:"
                           "\n1. Вы указываете вопрос сразу после команды ВЫБОР "
                           "(пример <префикс>выбор Стоит лм убрать меня с админки?)"
                           "\n2. Далее необходимо указать ответы, которые будут идти по порядку, через знак \"+\""
                           "(пример: <префикс>выбор <вопрос> +да +нет +что?",
                      brief="<префикс>выбор Стоит лм убрать меня с админки? +да +нет +что?",
                      description="Команда создает голосвание, которое можно использовать как угодно.")
    @commands.guild_only()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def polls(self, ctx, *, data: str):
        message = data.split()
        answers = data.split("+")
        quest = ""
        for i in range(1, len(message)):
            if message[i].find("+") == -1:
                quest += message[i] + " "
            else:
                break

        if quest == "":
            await ctx.channel.send(embed=await functions.embeds.description("Вы не поставили вопрос.",
                                                                            "Голосование не может быть создано, пока"
                                                                            "не будет поставлен вопрос голосования."))
            return

        answers = answers[1:len(answers)]
        if len(answers) > 9 or len(answers) < 1:
            await ctx.channel.send(
                embed=await functions.embeds.description(f"Ответ очень {'мало' if len(answers) < 1 else 'много'}.",
                                                         f"Голосование не может быть создано, потому что количетсво "
                                                         f"ответов {'меньше 1' if len(answers) < 1 else 'больше 9'}."))
            return

        msg = await ctx.send(embed=await functions.embeds.poll(ctx, quest, answers))

        for i in range(1, len(answers) + 1):
            await msg.add_reaction(f"{i}\N{combining enclosing keycap}")

    @commands.command(name="голосование",
                      help="Дополнительные аргументы в этой команде используются следующим образом:"
                           "\n1. Для начала нужно указать время, которое будет идти голосование, но не больше 60 минут"
                           " (пример: <префикс>голосование 60)."
                           "\n2. Вы указываете вопрос сразу после команды ГОЛОСОВАНИЕ"
                           " (пример: <префикс>голосование 60 Стоит лм убрать меня с админки?)"
                           "\n3. Далее необходимо указать ответы, которые будут идти по порядку, через знак \"+\""
                           " (пример: <префикс>голосование <время> <вопрос> +да +нет +что?",
                      brief="<префикс>голосование Стоит лм убрать меня с админки? +да +нет +что?",
                      description="Команда создает голосвание, но уже на определенное количетсво времени, "
                                  "которое можно использовать как угодно.")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def polls_time(self, ctx, time: int, *, data: str):
        message = data.split()
        answers = data.split("+")
        quest = ""
        for i in range(0, len(message)):
            if message[i].find("+") == -1:
                quest += message[i] + " "
            else:
                break

        if time > 60:
            await ctx.channel.send(embed=await functions.embeds.description("Нельзя ставить время на голосование "
                                                                            "больше 1 часа.",
                                                                            "Нельзя ставить время на голосование "
                                                                            "больше 1 часа из-за того что это может "
                                                                            "превисти к неожиданным последствиям."))
            return

        if quest == "":
            await ctx.channel.send(embed=await functions.embeds.description("Вы не поставили вопрос.",
                                                                            "Голосование не может быть создано, пока"
                                                                            "не будет поставлен вопрос голосования."))
            return

        answers = answers[1:len(answers)]

        if len(answers) > 9 or len(answers) < 1:
            await ctx.channel.send(
                embed=await functions.embeds.description(f"Ответ очень {'мало' if len(answers) < 1 else 'много'}.",
                                                         f"Голосование не может быть создано, потому что количетсво "
                                                         f"ответов {'меньше 1' if len(answers) < 1 else 'больше 9'}."))
            return

        emoji = self.client.get_emoji(690635964720087040)

        msg = await ctx.send(embed=await functions.embeds.poll_time(ctx, quest, time, answers, emoji))

        for i in range(1, len(answers) + 1):
            await msg.add_reaction(f"{i}\N{combining enclosing keycap}")

        self.poll_time = True
        message_id = msg.id
        del msg

        poll_time = {"emoji": 690635964720087040, "message": message_id, "voices": {}}

        with open("poll_time.json", "w", encoding='utf8') as file:
            json.dump(poll_time, file, indent=3)

        await asyncio.sleep(time * 60)

        try:
            msg = await ctx.channel.fetch_message(message_id)
        except discord.NotFound:
            await ctx.send(embed=await functions.embeds.description("Сообщение с голосвание не было найдено.",
                                                                    "Произошла ошибка и сообщение с голосвание не "
                                                                    "было найдено."))

        self.poll_time = False

        embed = msg.embeds[0].to_dict()

        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))

        pprint(embed)

        del embed['description']
        embed['author']['name'] = f"Результаты. {embed['author']['name'][0].title()}{embed['author']['name'][1::]}"
        embed['footer']['text'] = f"Голосвание завершено в {now.strftime('%H:%M %d.%m.%Y')} | Создал {ctx.author.name}"

        await msg.edit(embed=discord.Embed.from_dict(embed))

        try:
            os.remove("poll_time.json")
        except Exception as error:
            self.logger.error(error)

    @commands.command(name="шаблон",
                      help="Данные которые нужны для использования этой команды:"
                           "\n<channel>: канал куда будет отправлен шаблон"
                           "\n<заголовок>: должен быть написан на новой строке"
                           "\n<текст>: последуюие строки после заголовка",
                      brief="<префикс>шаблон #основной <ЗАГОЛОВОК> <Нов. строчка БЛА БЛА БЛА...>",
                      description="Команда, отправляющая в определенный канал шаблон, который можно использовать для "
                                  "чего угодно.")
    @commands.has_permissions(mention_everyone=True)
    @commands.guild_only()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def patterns(self, ctx, channel: discord.TextChannel, *, data: str):

        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))

        embed = discord.Embed(colour=discord.Colour.from_rgb(54, 57, 63))
        embed.description = ""

        lines = data.split("\n")

        if len(lines) == 1:
            await ctx.send(embed=await functions.embeds.description("Текст сообщения не был найден.",
                                                                    "Вы написали только заголовок, без текста."))
            return

        embed.set_author(name=lines[1].replace("_", "").replace("*", "").replace("~", ""))

        lines = lines[2:len(lines)]

        for line in lines:
            embed.description = embed.description + line + "\n"

        if channel:
            message = await channel.send(embed=embed)

            embed.set_footer(text=f"{ctx.author.name} | ID:{message.id} | {now.strftime('%d.%m.%Y')}")
            await message.edit(embed=embed)
        if not channel:
            message = await ctx.send(embed=embed)

            embed.set_footer(text=f"{ctx.author.name} | ID:{message.id} | {now.strftime('%d.%m.%Y')}")
            await message.edit(embed=embed)

        await ctx.send("Шаблон успешно отправлен!", delete_after=10.0)
        await ctx.message.delete()

    @commands.command(name="изменить_шаблон",
                      help="Данные которые нужны для использования этой команды:"
                           "\n<channel>: канал куда будет отправлен шаблон"
                           "\n<заголовок>: должен быть написан на новой строке"
                           "\n<текст>: последуюие строки после заголовка",
                      brief="<префикс>шаблон #основной <ЗАГОЛОВОК> <Нов. строчка БЛА БЛА БЛА...>",
                      description="Команда, отправляющая в определенный канал шаблон, который можно использовать для "
                                  "чего угодно.")
    @commands.has_permissions(mention_everyone=True)
    @commands.guild_only()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def change_patterns(self, ctx, channel: discord.TextChannel, *, data: str):
        command = ctx.message.content.split()
        channel, message, embed, info = None, None, None, None

        try:
            message = await channel.fetch_message(command[1])
        except discord.NotFound:
            await ctx.send("Сообщение не было найдено.")
            return
        except Exception as error:
            self.logger.error(error)
        else:
            if not message.embeds:
                await ctx.send("В сообщении не найдено шаблонов.")
                return
            else:
                embed = message.embeds[0]

        with open("changed_pattern.txt", "w", encoding="utf8") as file:
            dict = embed.to_dict()
            file.write(dict['author']['name'] + '\n' + dict['description'])

        file = open("changed_pattern.txt", "rb")
        temp = discord.File(file, filename="changed_pattern.txt")

        info = await ctx.send(content="Данный файл содержит все введенные автором символы.\n"
                                      "Скачайте и измените то что вам нужно, после чего отправте весь тест, "
                                      "даже если вы исправили 1 букву.\n"
                                      "Для отмены правки введите слово \"отмена\".\n"
                                      "Это сообщение будет удалено, через 2 минуты.\n"
                                      "***ВНИМАНИЕ! Если вы введете любое сообщение в этот канал, "
                                      "это автоматически посчитается за изменение!***",
                              file=temp,
                              delete_after=120.0)

        file.close()

        try:
            os.remove("changed_pattern.txt")
        except Exception as error:
            self.logger.error(error)

        def check(msg):
            return msg.channel.id == ctx.channel.id and msg.author.id == ctx.author.id

        try:
            new_embed = await self.client.wait_for('message', check=check, timeout=600)
        except asyncio.TimeoutError:
            await ctx.send(f"{ctx.author.mention}, время на изменения превышенно!")
        else:
            text = new_embed.content.split('\n')

            if text[0].lower() == "отмена":
                await ctx.send("Изменени отменено.")
                await info.delete()
                return

            if len(text) == 1:
                await ctx.send("Текст сообщения содержит всего лишь название. Этого недостаточно.")
                return

            embed = discord.Embed(colour=discord.Colour.from_rgb(54, 57, 63))
            embed.description = ""

            embed.set_author(name=text[0].replace("_", "").replace("*", "").replace("~", ""))

            text = text[1:len(text)]

            for line in text:
                embed.description = embed.description + line + "\n"

            now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))

            embed.set_footer(text=f"{ctx.author.name} | ID:{command[1]} | Изменено {now.strftime('%d.%m.%Y')} "
                                  f"в {now.strftime('%H.%M.%S')}")

            await message.edit(embed=embed)

            await ctx.send("Шаблон успешно изменен!")
            await info.delete()
            await new_embed.delete()

    @commands.command(name="ботбан", help="<префикс>ботбан <хайлайт роли>")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def botban(self, ctx, role: discord.Role):

        conn, user = self.pgsql.connect()

        user.execute("INSERT INTO botban (id) VALUES({})".format(role.id))
        conn.commit()

        await ctx.send(embed=await functions.embeds.description("Роль успешно добавлена в игнорируемые ботом.",
                                                                "Теперь участники с этой ролью будут игнорироваться "
                                                                "ботом во всех каналах."))

        self.pgsql.close_conn(conn, user)

    @commands.command(name="ботразбан", help="<префикс>ботбан <хайлайт роли>")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def botunban(self, ctx, role: discord.Role):

        conn, user = self.pgsql.connect()

        user.execute("DELETE * FROM botban WHERE id = {}".format(role.id))
        conn.commit()

        await ctx.send(embed=await functions.embeds.description("Роль успешно удалена из игнорируемых ботом.",
                                                                "Теперь участники с этой ролью НЕ будут игнорироваться "
                                                                "ботом во всех каналах."))

        self.pgsql.close_conn(conn, user)

    @commands.command(name="ShutDown", help="<префикс>ShutDown")
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.guild_only()
    async def botban(self, ctx, role: discord.Role):

        conn, user = self.pgsql.connect()

        user.execute("INSERT INTO botban (id) VALUES({})".format(role.id))
        conn.commit()

        await ctx.send(embed=await functions.embeds.description("Роль успешно добавлена в игнорируемые ботом.",
                                                                "Теперь участники с этой ролью будут игнорироваться "
                                                                "ботом во всех каналах."))

        self.pgsql.close_conn(conn, user)

    @commands.command(name="сервер")
    @commands.guild_only()
    async def server_info(self, ctx):
        embed = await functions.embeds.server_info(ctx.guild)
        await ctx.send(embed=embed)

    @generate_promo.before_loop
    async def ready(self):
        await self.client.wait_until_ready()

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):

        if not self.poll_time or user.id == self.client.user.id:
            return

        with open("poll_time.json", "r", encoding='utf8') as file:
            previously = json.load(file)

        message = reaction.message

        if message.id != previously['message']:
            return

        emoji = self.client.get_emoji(previously['emoji'])

        if str(user.id) not in previously['voices'].keys():
            embed = message.embeds[0].to_dict()
            embed["fields"][int(reaction.emoji[0]) - 1]['value'] += f" <:{emoji.name}:{emoji.id}>"
            await message.edit(embed=discord.Embed.from_dict(embed))
            await reaction.remove(user)
            previously['voices'][user.id] = int(reaction.emoji[0])
        else:
            await reaction.remove(user)

        with open("poll_time.json", "w", encoding='utf8') as file:
            json.dump(previously, file, indent=3)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(colour=discord.Colour.red())
            embed.set_author(name="Недостаточно прав.")
            embed.description = "У вас недостаточно прав для использования данной команды."
            await ctx.send(embed=embed)
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(colour=discord.Colour.dark_gold())
            embed.set_author(name="Нехватка аргументов в команде.")
            embed.description = f"{ctx.author.mention} недостаточно аргументов в команде, которую вы используете."
            embed.set_footer(text="Ниже представлена дополнительная информация")
            await ctx.send(embed=embed)
            await ctx.send_help(ctx.command)
        elif isinstance(error, commands.NoPrivateMessage):
            embed = discord.Embed(colour=discord.Colour.dark_gold())
            embed.set_author(name="Эта команда может быть использована только на сервере.")
            embed.description = f"{ctx.author.mention}, команда **{ctx.message.content.split()[0]}** не может быть " \
                                f"использована в `Личных Сообщениях`."
            await ctx.send(embed=embed)
        elif isinstance(error, commands.TooManyArguments):
            embed = discord.Embed(colour=discord.Colour.dark_gold())
            embed.set_author(name="Слишком много аргументов в команде.")
            embed.description = f"{ctx.author.mention} вы ввели аргументы, которые скорее всего не нужны здесь."
            embed.set_footer(text="Ниже представлена дополнительная информация")
            await ctx.send(embed=embed)
            await ctx.send_help(ctx.command)
        elif isinstance(error, commands.CommandNotFound):
            embed = discord.Embed(colour=discord.Colour.red())
            embed.set_author(name="Команда не найдена.")
            embed.description = f"Комадна **{ctx.message.content.split()[0]}** не существует или вы ошиблись в ее " \
                                f"написании."
            await ctx.send(embed=embed)
        elif isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(colour=discord.Colour.red())
            embed.set_author(name="Пожалуйста, не спешите.")
            if int(error.retry_after) == 1:
                cooldown = "{}, ожидайте ещё {} секунду перед тем как повторить команду."
            elif 2 <= int(error.retry_after) <= 4:
                cooldown = "{}, ожидайте ещё {} секунды перед тем как повторить команду."
            else:
                cooldown = "{}, ожидайте ещё {} секунд перед тем как повторить команду."
            embed.description = cooldown.format(ctx.author.mention, int(error.retry_after))
            await ctx.send(embed=embed)

        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(colour=discord.Colour.red())
            embed.set_author(name="Аргументы не соотсвуют нужным типам.")
            embed.description = f"Похоже, что тип данных, который вы ввели в качестве аргумента не соотсвутует " \
                                f"нужному. Доп. информация:\n **{error}**"
            await ctx.send(embed=embed)
            await ctx.send_help(ctx.command)
        else:
            embed = discord.Embed(colour=discord.Colour.dark_red())
            embed.set_author(name="Произошло непредвиденное исключение.")
            embed.description = str(error)
            await ctx.send(embed=embed)
