import asyncio
import datetime
import requests
import logging
import peewee
import os
import json as js
import steam.steamid
from valve.rcon import *

import discord
from discord.ext import commands, tasks
from models import *
from peewee import fn, JOIN
import random

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from io import BytesIO

import functions.helper
from functions.create_plot import create_figure


class MainCommands(commands.Cog, name="Основные команды"):

    def __init__(self, client):
        self.client = client

        logger = logging.getLogger("main_commands")
        logger.setLevel(logging.INFO)

        self.logger = logger

        self.choice_on = False

        self.generate_promo.start()

    async def open_connect(self):
        try:
            db.connect()
            return True
        except peewee.OperationalError:
            db.close()
            db.connect()
            return True

    @staticmethod
    @commands.check(open_connect)
    async def profile_check(author):
        UserDiscord.insert(discord_id=author.id).on_conflict_ignore().execute()

    @tasks.loop(minutes=random.randint(420, 900))
    @commands.check(open_connect)
    async def generate_promo(self):
        promo_event = ["Никогда раньше такого не было, чтобы **{} {}ок** давали за раз и вот опять."
                       "\nА все потому что инфляция, кризис и немного санкций.\nПромокод: `{}`",

                       "Тут мне администраторы нашептали, что стоит вам дать кое-что интересное."
                       "Как тебе такое Илон Маск?\n**{} {}ок**\nПромокод: `{}`",

                       "На улице снег? А может дождь? А может там **{} {}ок** лежит на дороге?"
                       "Не знаю, чего это вы на них смотрите, берите и бегите.\nПромокод: `{}`",

                       "А вы знали что на Sunrise есть бесплатное пиво? И мы не знали. "
                       "В прочем, еще есть промокод на **{} {}ок**\nПромокод: `{}`",

                       "Этот 2020 год был тяжелый. Да и предыдущий не проще, а что следующий?"
                       "\nБудет проще с **{} {}ок**.\nПромокод: `{}`",

                       "Однажды, парень рассказал, что нашёл **{} {}ок**\nПлакала половина маршрутки, "
                       "а этим парнем был Альберт инсайд.\nПромокод: `{}`",

                       "Ало, это я, с промокодом на **{} {}ок**, который можно активировать прямо сейчас."
                       "\nПромокод: `{}`"]

        promocode_info = Promocode.get(Promocode.id == 1)

        # channel = discord.utils.get(self.client.get_all_channels(), name='бот')
        comment = random.choice(promo_event)

        if promocode_info.code > 1:
            code = promocode_info.code
            amount = promocode_info.amount
            thing = promocode_info.thing
        elif promocode_info.code == 1:
            amount, thing = await functions.helper.promo_win()
            code = str(random.randint(10000, 100000)) + str(thing + 4)

            promocode_info.code = code
            promocode_info.amount = amount
            promocode_info.thing = thing
            promocode_info.save()
        elif promocode_info.code == 0:
            return 

        await channel.send(embed=await functions.embeds.promocode("Новый промокод!",
                                                                  comment.format(
                                                                      amount,
                                                                      "реверсив" if thing == 0 else "зл. реверсив",
                                                                      code),
                                                                  promocode_info.creating_admin,
                                                                  channel.guild.icon_url))

    @commands.command(name='промокоды',
                      help="Дополнительные аргументы в этой команде не нужны.",
                      brief="<префикс>промокоды",
                      description="Включает (или выключают) промокоды, которые отсылаются в системный канал сервера.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.check(open_connect)
    async def promo_switch(self, ctx):
        def check(msg):
            return msg.content.lower() == "да" or msg.content.lower() == "нет" \
                   and msg.author.guild_permissions.administrator

        promocode_info = Promocode.get(Promocode.id == 1)

        if promocode_info.code == 0:
            promocode_info.code = 1
            promocode_info.save()
            await ctx.send(embed=await functions.embeds.description("Промокоды теперь ДОСТУПНЫ.",
                                                                    "В течении 8 часов должен прийти первый "
                                                                    "промокод, который можно активировать с "
                                                                    "помощью команды **{}промокод**"
                                                                    .format(self.client.command_prefix[0])))
        elif promocode_info.code != 0:
            await ctx.send(embed=await functions.embeds.description("Вы уверены, что хотите отключить промокоды?",
                                                                    "\nЕсли ДА, то введите слово **ДА**"
                                                                    "\nЕсли НЕТ, то введите слово НЕТ"),
                           delete_after=15.0)
            try:
                message = await self.client.wait_for('message', timeout=15.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send("Отключение промокодов отменено.", delete_after=5.0)
                self.logger.warning("Time to disable promocodes codes is over.")
            else:
                if message.content.lower() == "да":
                    promocode_info.code = 0
                    promocode_info.amount = 0
                    promocode_info.thing = 0
                    promocode_info.save()
                    await ctx.send(embed=await functions.embeds.description("Промокоды теперь НЕ ДОСТУПНЫ.",
                                                                            "Чтобы опять включить промокоды введите ту "
                                                                            "же самую команду."))
                else:
                    await ctx.send("Отключение промокодов отменено.", delete_after=5.0)

    @commands.command(name='создать_промокод',
                      help="Данные которые нужны для использования этой команды:"
                           "\n<amount>: Количество валюты"
                           "\n<thing>: Число, обозночающее что вы хотите использовать в качестве валюты "
                           "(10000 < число < 100000)"
                           "(0 - реверсивки, 1 - золотые реверсивки",
                      brief="<префикс>создать_промокод 20000 1",
                      description="С помощью этой команды вы можете создать промокод, который отсылается вам в ЛС.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.check(open_connect)
    async def create_promocode(self, ctx, amount: int, thing: int):

        count = Promocode.select().count()

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

        promo = Promocode \
                    .insert(code=code, amount=amount, thing=thing, creating_admin=True) \
                    .on_conflict_ignore() \
                    .execute()

        try:
            await ctx.author.send(embed=
                                  await functions.embeds.promocode("Вы создали промокод.",
                                                                   f"Вы создали промокод на {amount} "
                                                                   f"{'реверсивок' if thing == 0 else 'зл. реверсивок'}",
                                                                   True,
                                                                   ctx.guild.icon_url))
        except discord.Forbidden:
            await ctx.send(embed=await functions.embeds.description(f"Невозможно отправить Вам промокод.",
                                                                    "Пожалуйста провертье, что Вам могут писать люди, "
                                                                    "даже если они не добавили Вас в друзья."))
            Promocode.delete().where(Promocode.id == promo.id)
            self.logger.warning("Unable to send message. Not enough rights. Forbidden.")

    @commands.command(name='просмотреть_промокоды',
                      help="Дополнительные аргументы в этой команде не нужны.",
                      brief="<префикс>просмотреть_промокоды",
                      description="С помощью этой команды вы можете узнать все промокоды, созданные Вами и не только.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.check(open_connect)
    async def check_promocode(self, ctx):
        all_promocodes = Promocode.select()

        embed = discord.Embed(colour=discord.Colour.dark_green(), title="Все промокоды доступные на сервере.")
        embed.set_author(name=ctx.guild.name)

        text_promocode = list()

        for promo in all_promocodes:
            if promo.code == 0 and promo.id == 1:
                embed.add_field(name="Промокод выводимый автоматически ВЫКЛЮЧЕНЫ",
                                value=f"Чтобы их включить введите команду {self.client.command_prefix[0]}промокод.",
                                inline=False)
            elif promo.code == 1 and promo.id == 1:
                embed.add_field(name="Промокод, создаваемый автоматически был использован.",
                                value=f"Промокод, создаваемый автоматически был использован.",
                                inline=False)
            elif promo.code > 1 and promo.id == 1:
                embed.add_field(name="Промокод, создаваемый автоматически:",
                                value=f"Промокод **{promo.code}** состовляет **{promo.amount} "
                                      f"{'реверсивок' if promo.thing == 0 else 'зл. реверсивок'}**",
                                inline=False)

            else:
                text_promocode.append(f"Промокод **{promo.code}** состовляет "
                                      f"**{promo.amount} {'реверсивок' if promo.thing == 0 else 'зл. реверсивок'}**")

        if len(text_promocode) == 0:
            embed.add_field(name="Промокоды, созданные Администрацией, ОТСУТСТВУЮТ.",
                            value="Промокоды, созданные Администрацией, ОТСУТСТВУЮТ.",
                            inline=False)
        else:
            embed.add_field(name="Промокоды, созданные Администрацией",
                            value="\n".join([x for x in text_promocode]),
                            inline=False)

        try:
            await ctx.author.send(embed=embed)
        except discord.Forbidden:
            await ctx.send(embed=await functions.embeds.description(f"Невозможно отправить Вам информацию по "
                                                                    f"промокодам.",
                                                                    "Пожалуйста провертье, что Вам могут писать люди, "
                                                                    "даже если они не добавили Вас в друзья."))
            self.logger.warning("Unable to send message. Not enough rights. Forbidden.")

    @commands.command(name="промокод",
                      help="Данные которые нужны для использования этой команды:"
                           "\n<promo>: промокод.",
                      brief="<префикс>промокод или <префикс>промокод 123456",
                      description="Команда, позволяющая активировать промокод.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.check(open_connect)
    async def promocode(self, ctx, *code):
        await self.profile_check(ctx.author)

        if code:
            code = code[0]
            if not code.isdigit():
                await ctx.send(embed=await functions.embeds.description("Промокод введен неверно.",
                                                                        "Проверьте нет ли символов или иных"
                                                                        "знаков в числе обозначющим промокод."))
                return

            if code == 0 or code == 1:
                await ctx.send(embed=await functions.embeds.description("Запрещенные команды.",
                                                                        "Так делать нельзя."))
                return

            try:
                promocode_info = Promocode.get(Promocode.code == code)
            except peewee.DoesNotExist:
                await ctx.send(embed=await functions.embeds.description("Такого промокода не существует.",
                                                                        "Перепроверте правильность введного вами "
                                                                        "промокода."))
                return
        else:
            try:
                promocode_info = Promocode.get(Promocode.id == 1)
            except peewee.DoesNotExist:
                await ctx.send(embed=await functions.embeds.description("Что-то пошло не так",
                                                                        "Простите, но похоже сегодня промокода не "
                                                                        "будет"))
                return

        if promocode_info.code == 1:
            await ctx.send(embed=await functions.embeds.description("Пока промокодов нету.",
                                                                    "Простите, но похоже, что всевозможные промокоды "
                                                                    "были уже активированы."))
            return

        user = UserDiscord.get(UserDiscord.discord_id == ctx.author.id)

        if promocode_info.thing == 0:
            user.money = user.money + promocode_info.amount
            user.save()
            await ctx.send(
                embed=await functions.embeds.use_promo("Промокод был активирован.",
                                                       f"Вы активировали промокод **{promocode_info.code}** "
                                                       f"на **{promocode_info.amount}** реверсивок",
                                                       ctx.guild.icon_url))
        elif promocode_info.thing == 1:
            user.gold_money = user.gold_money + promocode_info.amount
            user.save()
            await ctx.send(
                embed=await functions.embeds.use_promo("Промокод был активирован.",
                                                       f"Вы активировали промокод **{promocode_info.code}** "
                                                       f"на **{promocode_info.amount}** зл. реверсивок",
                                                       ctx.guild.icon_url))

        if promocode_info.id == 1:
            promocode_info.code = 1
            promocode_info.amount = 0
            promocode_info.save()
        else:
            promocode_info.delete_instance()

    @commands.command(name='профиль',
                      help="Дополнительные аргументы в этой команде могут быть использованы, только если вам нужно "
                           "узнать профиль другого участника сервера.",
                      brief="<префикс>профиль @Chell",
                      description="С помощью этой команды вы можете узнать всю информацию о себе, а также просмотреть "
                                  "информацию о другом участнике.")
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.check(open_connect)
    async def profile(self, ctx, *args):
        await self.profile_check(ctx.author)

        now = datetime.datetime.now()

        if len(args) > 1:
            raise commands.TooManyArguments()

        data, client = None, None

        async with ctx.typing():
            name_of_currency = "рев."

            if args:
                user = args[0]
                if not isinstance(user, discord.Member):
                    client = await commands.MemberConverter().convert(ctx, user)
                else:
                    client = user

                if not client:
                    await ctx.send(embed=await functions.embeds.description(f"Пользователь не был найден.",
                                                                            "Профиль данного пользователя не может "
                                                                            "быть просмотрен в угоду того, что не был "
                                                                            "найден на этом сервере."))
                    return
                await self.profile_check(client)
                data = UserDiscord.get(UserDiscord.discord_id == client.id)
                user_ctx = client
            elif len(ctx.message.content.split()) == 1:
                data = UserDiscord.get(UserDiscord.discord_id == ctx.author.id)
                user_ctx = ctx.author  
            
            rat = int(Rating \
                        .select() \
                        .where((Rating.discord == user_ctx.id) & (Rating.rating == True)) \
                        .count()) \
                - int(Rating \
                        .select() \
                        .where((Rating.discord == user_ctx.id) & (Rating.rating == False)) \
                        .count()) 

            if data.SID != None and data.SID != "None":
                try:
                    steam = GmodPlayer.get(GmodPlayer.SID == data.SID)
                except peewee.DoesNotExist:
                    await ctx.send(embed=await functions.embeds.description(f"{user_ctx.name} ни разу не "
                                                                            f"заходил на сервер.",
                                                                            "После нашего переноса баз данных, "
                                                                            "информация по игрокам была обновлена."
                                                                            " Пожалуйста, зайдите на сервер, чтобы"
                                                                            " пройти окончательную синхронизацию."
                                                                            "\nПриносим свои извинения."))
                    all_data = dict(rating=rat, money=data.money, gold_money=data.gold_money,
                                    steamid='Данные отсутствуют', nick='Данные отсутствуют', time='Данные отсутствуют',
                                    rank='Данные отсутствуют', name_of_currency=name_of_currency)
                else:
                    try:
                        time = PlayerGroupTime \
                                    .select(fn.SUM(PlayerGroupTime.time).alias('sum_time')) \
                                    .where(PlayerGroupTime.player_id == steam.id) \
                                    .get()
                        all_data = dict(rating=rat, money=data.money, gold_money=data.gold_money,
                                        steamid=data.SID,
                                        nick=steam.nick, time=0 if not time.sum_time else time.sum_time, rank=steam.group,
                                        name_of_currency=name_of_currency)
                    except peewee.DoesNotExist:
                        all_data = dict(rating=rat, money=data.money, gold_money=data.gold_money,
                                        steamid=data.SID,
                                        nick=steam.nick, time=0, rank=steam.group,
                                        name_of_currency=name_of_currency)
            else:
                try:
                    steam = GmodPlayer.get(GmodPlayer == data.SID)
                except peewee.DoesNotExist:
                    all_data = dict(rating=rat, money=data.money, gold_money=data.gold_money,
                                steamid='Не синхронизирован', nick='Не синхронизирован', time='Не синхронизирован',
                                rank='Не синхронизирован', name_of_currency=name_of_currency)
                else:
                    try:
                        time = PlayerGroupTime \
                                    .select(fn.SUM(PlayerGroupTime.time).alias('sum_time')) \
                                    .where(PlayerGroupTime.player_id == steam.id) \
                                    .get()
                        all_data = dict(rating=rat, money=data.money, gold_money=data.gold_money,
                                        steamid=data.SID,
                                        nick=steam.nick, time=0 if not time.sum_time else time.sum_time, rank=steam.group,
                                        name_of_currency=name_of_currency)
                    except peewee.DoesNotExist:
                        all_data = dict(rating=rat, money=data.money, gold_money=data.gold_money,
                                        steamid=data.SID,
                                        nick=steam.nick, time=0, rank=steam.group,
                                        name_of_currency=name_of_currency)

            try:
                if ctx.guild.id == 569627056707600389:
                    img_profile = Image.open("stuff/profile_gorails.jpg")
                else:
                    img_profile = Image.open("stuff/profile_sunrails.jpg")

                fileRequest = requests.get(user_ctx.avatar_url)
                img_avatar = Image.open(BytesIO(fileRequest.content))

                img_avatar = img_avatar.resize((300, 300), Image.ANTIALIAS)

                img_profile.paste(img_avatar, (120, 185))

                draw = ImageDraw.Draw(img_profile)
                nick_font = ImageFont.truetype("stuff/Enigmatic.ttf", 80)
                text_font = ImageFont.truetype("stuff/Arial AMU.ttf", 55)
                nick_steam_font = ImageFont.truetype("stuff/OpenSans.ttf", 55)

                if user_ctx.display_name == user_ctx.name:
                    draw.text((430, 325), u"%s" % user_ctx.name, (255, 255, 255), font=nick_font)
                else:
                    draw.text((430, 225), u"%s" % user_ctx.display_name, (255, 255, 255), font=nick_font)
                    draw.text((430, 325), u"%s" % user_ctx.name, (255, 255, 255), font=nick_font)
                

                if str(user_ctx.status) == "online":
                    draw.text((435, 435), "Онлайн", (255, 255, 255), font=text_font)
                elif str(user_ctx.status) == "idle":
                    draw.text((435, 435), "Отошел, но при это посмотрел профиль", (255, 255, 255), font=text_font)
                elif str(user_ctx.status) == "dnd":
                    draw.text((435, 435), "Не беспокоить", (255, 255, 255), font=text_font)
                elif str(user_ctx.status) == "offline":
                    draw.text((435, 435), "Не в сети, но мы то знаем...", (255, 255, 255), font=text_font)
                else:
                    draw.text((435, 435), "Онлайн", (255, 255, 255), font=text_font)

                if now.strftime("%m.%d") == "04.01":
                    draw.text((140, 510), f"Средства: {all_data['money'] + 100000000} {name_of_currency} | {all_data['gold_money']}"
                                          f" зол. {name_of_currency}", (255, 255, 255), font=text_font)
                else:
                    draw.text((140, 510), f"Средства: {all_data['money']} {name_of_currency} | {all_data['gold_money']}"
                                          f" зол. {name_of_currency}", (255, 255, 255), font=text_font)

                draw.text((140, 670), f"Имя на сервере: {all_data['nick']}", (255, 255, 255), font=nick_steam_font)

                draw.text((140, 600), f"Рейтинг: {all_data['rating']} (Стрелочки ниже повышают или понижают его)", (255, 255, 255), font=text_font)

                if all_data['rank'] == "user":
                    draw.text((140, 770), "Ранг: Помощник машиниста", (255, 255, 255), font=text_font)
                elif all_data['rank'] == "driver":
                    draw.text((140, 770), "Ранг: Машинист Б/К", (255, 255, 255), font=text_font)
                elif all_data['rank'] == "driver3class":
                    draw.text((140, 770), "Ранг: Машинист 3 класса", (255, 255, 255), font=text_font)
                elif all_data['rank'] == "driver2class":
                    draw.text((140, 770), "Ранг: Машинист 2 класса", (255, 255, 255), font=text_font)
                elif all_data['rank'] == "driver1class":
                    draw.text((140, 770), "Ранг: Машинист 1 класса", (255, 255, 255), font=text_font)
                elif all_data['rank'] == "stationdispather":
                    draw.text((140, 770), "Ранг: Премиум", (255, 255, 255), font=text_font)
                elif all_data['rank'] == "actinstructor":
                    draw.text((140, 770), "Ранг: И.О. машинист-инструктор", (255, 255, 255), font=text_font)
                elif all_data['rank'] == "traindispather":
                    draw.text((140, 770), "Ранг: Диспетчер", (255, 255, 255), font=text_font)
                elif all_data['rank'] == "instructor":
                    draw.text((140, 770), "Ранг: Машинист-инструктор", (255, 255, 255), font=text_font)
                elif all_data['rank'] == "chieftraindispather":
                    draw.text((140, 770), "Ранг: Гл. Диспетчер", (255, 255, 255), font=text_font)
                elif all_data['rank'] == "chiefinstructor":
                    draw.text((140, 770), "Ранг: Гл. Машинист-инструктор", (255, 255, 255), font=text_font)
                elif all_data['rank'] == "operator":
                    draw.text((140, 770), "Ранг: Модератор", (255, 255, 255), font=text_font)
                elif all_data['rank'] == "chiefoperator":
                    draw.text((140, 770), "Ранг: Гл. Модератор", (255, 255, 255), font=text_font)
                elif all_data['rank'] == "auditor":
                    draw.text((140, 770), "Ранг: Ревизор", (255, 255, 255), font=text_font)
                elif all_data['rank'] == "developer":
                    draw.text((140, 770), "Ранг: Разработчик", (255, 255, 255), font=text_font)
                elif all_data['rank'] == "admin":
                    draw.text((140, 770), "Ранг: Руководящий состав", (255, 255, 255), font=text_font)
                elif all_data['rank'] == "superadmin":
                    draw.text((140, 770), "Ранг: Начальник метрополитена", (255, 255, 255), font=text_font)

                elif all_data['rank'] == "Не синхронизирован":
                    draw.text((140, 770), "Ранг: Не синхронизирован", (255, 255, 255), font=text_font)
                elif all_data['rank'] == "Данные отсутствуют":
                    draw.text((140, 770), "Ранг: Данные отсутствуют", (255, 255, 255), font=text_font)

                draw.text((140, 845), f"SteamID: {all_data['steamid']}", (255, 255, 255), font=text_font)

                all_time, embed = None, None

                if all_data['time'] != "Не синхронизирован" and all_data['time'] != "Данные отсутствуют":

                    all_time = str(datetime.timedelta(seconds=int(all_data['time'])))

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
                    all_time = "Данных нет"

                draw.text((140, 930), f"Время на сервере: {all_time}", (255, 255, 255), font=text_font)

                img_profile.save("stuff/custom_profile.jpg")

                fileRequest.close()
                img_profile.close()

                message = None

                with open("stuff/custom_profile.jpg", "rb") as jpg:
                    file = discord.File(jpg, filename="profile.jpg")
                    if embed:
                        message = await ctx.send(embed=embed, file=file)
                    else:
                        message = await ctx.send(file=file)
                os.remove("stuff/custom_profile.jpg")

                await message.add_reaction("⬆️")
                await message.add_reaction("⬇️")

                def check(reaction, user):
                    if user.id == self.client.user.id:
                        return False

                    try:
                        rating = Rating.get((Rating.discord == user_ctx.id) & (Rating.user == user.id))
                    except peewee.DoesNotExist:
                        if str(reaction.emoji) == "⬆️":
                            Rating.insert(discord=user_ctx.id, user=user.id, rating=True, date=now).execute()
                        elif str(reaction.emoji == "⬇️"):
                            Rating.insert(discord=user_ctx.id, user=user.id, rating=False, date=now).execute()
                    else:
                        if rating.rating == True and str(reaction.emoji) == "⬇️":
                            rating.rating = False
                        elif rating.rating == False and str(reaction.emoji) == "⬆️":
                            rating.rating = True
                        rating.date = now
                        rating.save()
                    return False
                
                try:
                    reaction, user = await self.client.wait_for('reaction_add', timeout=30.0, check=check)
                except asyncio.TimeoutError:
                    pass

                await message.clear_reactions()

            except Exception as er:
                self.logger.error(er)

    # @commands.command(name='подарок',
    #                   help="Дополнительные аргументы в этой команде не нужны.",
    #                   brief="<префикс>подарок",
    #                   description="Что это?")
    # @commands.cooldown(1, 5, commands.BucketType.user)
    # @commands.guild_only()
    # @commands.has_permissions(administrator=True)
    # @commands.check(open_connect)
    # async def present(self, ctx):
    #     if True:
    #         return
    #     user, present = UserDiscord.get(discord_id=ctx.author.id), None
    #     try:
    #         present = NewYearPresents.get(discord_id=user.discord_id)
    #     except peewee.DoesNotExist:
    #         NewYearPresents.insert(discord_id=user.discord_id, present=0).execute()
    #         new_year = NewYearPresents.get(discord_id=user.discord_id)
    #         if random.choices([True, False]):
    #             user.money = random.randrange(50000, 100001, 10000)
    #             user.save()
    #             new_year.present = user.money
    #             new_year.save()
    #             await ctx.send(embed=await functions.embeds
    #                            .present("реверсивок", user.money, ctx.author.avatar_url))
    #         else:
    #             user.gold_money = random.randrange(100000, 500000, 50000)
    #             user.save()
    #             new_year.present = user.gold_money
    #             new_year.save()
    #             await ctx.send(embed=await functions.embeds
    #                            .present("зл. реверсивок", user.money, ctx.author.avatar_url))
    #     else:
    #         await ctx.send(embed=await functions.embeds.description("Вы уже получили свой новогодний подарок.",
    #                                                                 "Попытайте удачу в следующем году.\n\nС наступающим"
    #                                                                 "новым 2021 годом.\nВаш Sunrails Metrostroi."))

    @commands.command(name='тех_канал',
                      help="Данные которые нужны для использования этой команды:"
                           "\n<channel>: Канал для тех. информации",
                      brief="<префикс>удалить #канал-для-тех-сообщений",
                      description="Команда позволяет видеть текст удаленный/измененных сообщений, кто ушел/пришел на ваш сервер.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.check(open_connect)
    async def add_tech_channel(self, ctx, channel: discord.TextChannel):
        query = GuildDiscord.update({GuildDiscord.tech_channel: channel.id}).where(GuildDiscord.guild == ctx.guild.id)
        query.execute()
        await ctx.send(embed=await functions.embeds.description(f"Канал {channel.name} назначен",
                                                                f"Пожалуйста, провертье чтобы этот канал был доступен для {self.client.user.mention}"))


    @commands.command(name='удалить',
                      help="Данные которые нужны для использования этой команды:"
                           "\n<count>: Количество сообщений для удаления.",
                      brief="<префикс>удалить 25",
                      description="Команда позволяет удалить сразу довольно большое количество сообщений. "
                                  "Чтобы не потерять данные они сохраняются в файл .txt")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.check(open_connect)
    async def delete(self, ctx, count: int):
        if count > 100:
            await ctx.send(embed=await functions.embeds.description("Число удаляемых сообщений превышает 100",
                                                                    "Пожалуйста не надо удалять сразу так много "
                                                                    "сообщений."))
            return

        messages = await ctx.channel.history(limit=count + 1).flatten()
        messages = reversed(messages)

        with open("stuff/purgedeleted.txt", "w", encoding='utf8') as file:
            file.write("Удаленные сообщения:\n\n\n")
            for message in messages:
                file.write(
                    "\n" + str(message.author.name) + "#" + str(message.author.discriminator) + " (" + str(
                        message.created_at) + "): " + message.content)

        file = open("stuff/purgedeleted.txt", "rb")
        msgs_deleted = discord.File(file, filename="All_deleted_message.txt")

        await ctx.channel.purge(limit=count + 1)

        channel = discord.utils.get(self.client.get_all_channels(), name='⚡тех-записи⚡')
        await channel.send(embed=await functions.embeds.purge(ctx, count), file=msgs_deleted)

        file.close()
        msgs_deleted.close()
        os.remove("stuff/purgedeleted.txt")

    @commands.command(name='шанс',
                      help="Дополнительные аргументы в этой команде не нужны.",
                      brief="<префикс>шанс",
                      description="Команда для получения ежедневной прибыли (3 раза в день).")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.check(open_connect)
    async def chance(self, ctx):
        await self.profile_check(ctx.author)

        now = datetime.datetime.now()
        with open("stuff/config.json", "r", encoding="utf8") as file:
            json = js.load(file)

        if json['now_date'] != now.strftime("%d.%m.%Y"):
            json['now_date'] = now.strftime("%d.%m.%Y")
            query = UserDiscord.update({UserDiscord.chance_roulette: 3}).where(not UserDiscord.chance_roulette).execute()

        with open("stuff/config.json", "w", encoding="utf8") as file:
            js.dump(json, file, indent=4)

        user = UserDiscord.get(UserDiscord.discord_id == ctx.author.id)

        hours = 24 - now.hour if 24 - now.hour >= 10 else "0" + str(24 - now.hour)
        minutes = 60 - now.minute if 60 - now.minute >= 10 else "0" + str(60 - now.minute)
        seconds = 60 - now.second if 60 - now.second >= 10 else "0" + str(60 - now.second)

        if not user.chance_roulette:
            await ctx.send(embed=await functions.embeds.description("Активанция шанса уже была использована полность.",
                                                                    f"Активировать команду повторно вы смоежете через "
                                                                    f"**{hours}:{minutes}:{seconds}**."))
            return 

        user.chance_roulette = user.chance_roulette - 1
        user.save()

        times =  f"{user.chance_roulette} раза" if user.chance_roulette > 1 else f"{user.chance_roulette} раз"

        win, thing = await functions.helper.random_win()

        if thing == 0:
            user.money = user.money + win
            user.save()
            await ctx.send(embed=await functions.embeds.chance(ctx, win, "реверсивок", times))
        elif thing == 1:
            user.gold_money = user.gold_money + win
            user.save()
            await ctx.send(embed=await functions.embeds.chance(ctx, win, f"зл. реверсивок", times))
    
    # @commands.command(name='VIP',
    #                   help="Дополнительные аргументы в этой команде не нужны.",
    #                   brief="<префикс>VIP",
    #                   description="Команда для увеличения шанса на получения ")
    # @commands.cooldown(1, 5, commands.BucketType.user)
    # @commands.check(open_connect)

    @commands.command(name='рулетка',
                      help="Данные которые нужны для использования этой команды:"
                           "\n<rate>: Количество зл. реверсивок для использования команды.",
                      brief="<префикс>рулетка 1000",
                      description="Команда для получения рандомного выигрыша, в зафисимости от коэффициента")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.check(open_connect)
    async def roulette(self, ctx, rate: int):
        if rate > 1000000:
            await ctx.send(embed=await functions.embeds.description("Превышена ставка для рулетки",
                                                                    "Пожалуйста уменьшите ставку до **1 000 000 зл. реверсивок**"))
            return

        user = UserDiscord.get(UserDiscord.discord_id == ctx.author.id)

        if user.gold_money < rate:
            await ctx.send(embed=await functions.embeds.description("Недостаточно зл. реверсивок!",
                                                                     "Количество введеной суммы реверсивок недостаточно для выполнения данной команды."))
            return

        win = int(await functions.helper.factor_win() * rate)
        gif = "https://cdn.dribbble.com/users/2206179/screenshots/8185041/roulette_ball_v2_compress.gif"
 
        if 0 < win / rate < 0.2:
            text = f"{ctx.author.mention} проиграл всю поставленную сумму, как прискорбно.\n" \
                   f"\n**Остаточная сумма: {win} зл. реверсивок**" \
                   f"\n\nВаш SunRails Metrostroi"
            gif = "https://j.gifs.com/rRo702.gif"
        elif 0.2 < win / rate < 0.5:
            text = f"{ctx.author.mention} неповезло и он получил всего ничего.\n" \
                   f"\n**Остаточная сумма: {win} зл. реверсивок**" \
                   f"\n\nВаш SunRails Metrostroi"
        elif 1.1 < win / rate < 2:
            text = f"{ctx.author.mention} выиграл в рулетке и получил назад не только сумму ставки, но еще и кэш.\n" \
                   f"\n**Сумма выиграша: {win} зл. реверсивок**" \
                   f"\n\nВаш SunRails Metrostroi"
        elif 2 < win / rate < 3:
            text = f"{ctx.author.mention} сорвал куш и победил саму судьбу в игре под названием Фортуна. Как вам такое Борис Сергеевич?\n" \
                   f"\n**Сумма выиграша: {win} зл. реверсивок**" \
                   f"\n\nВаш SunRails Metrostroi"
        else:
            text = f"{ctx.author.mention}, страшно. Очень страшно.\nЕсли бы мы знали, мы не знаем что это такое, если бы мы знали что это такое, мы не знаем что это такое."\
                   f"\n**Остаточная сумма: {win} зл. реверсивок**" \
                   f"\n\nВаш SunRails Metrostroi"
            gif = "https://j.gifs.com/rRo702.gif"

        user.gold_money = user.gold_money - rate + win
        user.save()

        await ctx.send(embed=await functions.embeds.roullete(ctx, text, gif))


    @commands.command(name='топ',
                      help="Дополнительные аргументы в этой команде не нужны.",
                      brief="<префикс>топ",
                      description="Команда для получения топа игроков сервера по часам.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.check(open_connect)
    async def top(self, ctx):
        all_data = list()

        data = PlayerGroupTime \
                .select(PlayerGroupTime.player_id, fn.SUM(PlayerGroupTime.time).alias('sum_time')) \
                .join(GmodPlayer, JOIN.LEFT_OUTER) \
                .group_by(PlayerGroupTime.player_id) \
                .order_by(fn.SUM(PlayerGroupTime.time).desc()) \
                .limit(10)

        embed = discord.Embed(colour=discord.Colour.dark_gold())
        embed.set_author(name="ТОП 10 игроков сервера {}".format(ctx.guild.name))

        for info, count in zip(data, range(10)):
            link = steam.steamid.SteamID(info.player_id.SID)

            time = str(datetime.timedelta(seconds=int(info.sum_time)))
            if time.find("days") != -1:
                time = time.replace("days", "дн")
            else:
                time = time.replace("day", "дн")

            if time.find("weeks") != -1:
                time = time.replace("weeks", "нед")
            else:
                time = time.replace("week", "нед")
            all_data.append(f"{count + 1}. [{info.player_id.nick}]({link.community_url}) ({info.player_id.SID}) - {time}")

        embed.description = '\n'.join([one_man for one_man in all_data])

        await ctx.send(embed=embed)

    @commands.command(name='обмен',
                      help="Данные которые нужны для использования этой команды:"
                           "\n<revers>: Количество реверсивок на обмен.",
                      brief="<префикс>обмен 2000",
                      description="Команда, позволяющая обменять 4 обычных реверсивки на 1 золотой реверсивки.")
    @commands.check(open_connect)
    async def swap(self, ctx, money: int):
        await self.profile_check(ctx.author)

        data = UserDiscord.get(UserDiscord.discord_id == ctx.author.id)

        now = datetime.datetime.now()

        word = u'1́̒ͪͧ҉̫̞̫̤͕͡ ̤͉̱̦͂̂а̫̜̬͚͔̠͂ͭ̾̾̎̅п͈͈̏̑̆͂ͥ̓ͮ͘͢͝р̲̮̑͂́ͬ͌̒́͡е̗͓̩̣̲̥̑ͭ̅л̥̒ͥ̋͑̽я̴̖̫̘̺̙̉̈́̀͝ '

        if now.strftime("%m.%d") == "04.01":
            await ctx.send(embed=await functions.embeds.description(f"{word.decode('utf8')} реверсивок.",
                                                                    f"Смейся над шуткой до тех пор, пока не поймешь её смысла.\n- Михаил Генин"))
            return

        if data.money < money:
            await ctx.send(embed=await functions.embeds.description("Недостаточно реверсивок.",
                                                                    f"Вы хотите обменять реверсивки, которых у Вас "
                                                                    f"меньше, чем вы ввели."))
            return

        data.money -= money
        data.gold_money = data.gold_money + (money // 4)
        data.save()

        await ctx.send(embed=await functions.embeds.description("Реверсивки успешно обменены.",
                                                                f"Вы обменяли {money} реверсивок на "
                                                                f"{int(money / 4)} золотых реверсивок"))

    @commands.command(name="статистика",
                      help="Дополнительные аргументы в этой команде не нужны.",
                      brief="<префикс>статистика",
                      description="Выводит сайт для статистики")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.check(open_connect)
    async def static(self, ctx):
        await ctx.send("У нас появился свой сайт со статистикой! Прошу вас: https://statisticsunrails.ru")

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
        for i in range(0, len(message)):
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
                embed=await functions.embeds.description(
                    f"Ответов очень {'мало' if len(answers) < 1 else 'много'}.",
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

        self.choice_on = True
        message_id = msg.id
        del msg

        poll_time = {"emoji": 690635964720087040, "message": message_id, "voices": {}}

        with open("stuff/poll_time.json", "w", encoding='utf8') as file:
            js.dump(poll_time, file, indent=3)

        await asyncio.sleep(time * 60)

        try:
            msg = await ctx.channel.fetch_message(message_id)
        except discord.NotFound:
            await ctx.send(embed=await functions.embeds.description("Сообщение с голосвание не было найдено.",
                                                                    "Произошла ошибка и сообщение с голосвание не "
                                                                    "было найдено."))

        self.choice_on = False

        embed = msg.embeds[0].to_dict()

        now = datetime.datetime.now()

        pprint(embed)

        del embed['description']
        embed['author']['name'] = f"Результаты. {embed['author']['name'][0].title()}{embed['author']['name'][1::]}"
        embed['footer'][
            'text'] = f"Голосвание завершено в {now.strftime('%H:%M %d.%m.%Y')} | Создал {ctx.author.name}"

        await msg.edit(embed=discord.Embed.from_dict(embed))

        try:
            os.remove("stuff/poll_time.json")
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

        now = datetime.datetime.now()

        embed = discord.Embed(colour=discord.Colour.from_rgb(54, 57, 63))
        embed.description = ""

        lines = data.split("\n")

        if len(lines) == 1:
            await ctx.send(embed=await functions.embeds.description("Текст сообщения не был найден.",
                                                                    "Вы написали только заголовок, без текста."))
            return

        embed.set_author(name=lines[0].replace("_", "").replace("*", "").replace("~", ""))

        lines = lines[1:len(lines)]

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
                           "\n<channel>: канал где был отправлен шаблон"
                           "\n<message_id>: должен быть написан на новой строке"
                           "\n<текст>: последуюие строки после заголовка",
                      brief="<префикс>шаблон #основной <ID, которое написано в шаблоне>",
                      description="Команда, для изменение существующего шаблона.")
    @commands.has_permissions(mention_everyone=True)
    @commands.guild_only()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def change_patterns(self, ctx, channel: discord.TextChannel, message_id: int):
        command = ctx.message.content.split()
        message, embed, info = None, None, None

        try:
            message = await channel.fetch_message(message_id)
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

        with open("stuff/changed_pattern.txt", "w", encoding="utf8") as file:
            dict = embed.to_dict()
            file.write(dict['author']['name'] + '\n' + dict['description'])

        file = open("stuff/changed_pattern.txt", "rb")
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
            os.remove("stuff/changed_pattern.txt")
        except Exception as error:
            self.logger.error(error)

        def check(msg):
            return msg.channel.id == ctx.channel.id and msg.author.id == ctx.author.id

        try:
            new_embed = await self.client.wait_for('message', check=check, timeout=600)
        except asyncio.TimeoutError:
            await ctx.send(f"{ctx.author.mention}, время на изменения превышено!")
        else:
            text = new_embed.content.split('\n')

            if text[0].lower() == "отмена":
                await ctx.send("Изменение отменено.")
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

            now = datetime.datetime.now()

            embed.set_footer(text=f"{ctx.author.name} | ID:{command[2]} | Изменено {now.strftime('%d.%m.%Y')} "
                                  f"в {now.strftime('%H.%M.%S')}")

            await message.edit(embed=embed)

            await ctx.send("Шаблон успешно изменен!")
            await info.delete()
            await new_embed.delete()

    @commands.command(name="сервер")
    @commands.guild_only()
    async def server_info(self, ctx):
        embed = await functions.embeds.server_info(ctx.guild)
        await ctx.send(embed=embed)

    @generate_promo.before_loop
    async def ready(self):
        await self.client.wait_until_ready()

    @commands.Cog.listener()
    @commands.check(open_connect)
    async def on_reaction_add(self, reaction, user):
        if user.id == self.client.user.id:
            return
        if self.choice_on:
            with open("stuff/poll_time.json", "r", encoding='utf8') as file:
                previously = js.load(file)

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

            with open("stuff/poll_time.json", "w", encoding='utf8') as file:
                js.dump(previously, file, indent=3)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            self.logger.debug(error)
            embed = discord.Embed(colour=discord.Colour.red())
            embed.set_author(name="Недостаточно прав.")
            embed.description = "У вас недостаточно прав для использования данной команды."
            await ctx.send(embed=embed)
        elif isinstance(error, commands.MissingRequiredArgument):
            self.logger.debug(error)
            embed = discord.Embed(colour=discord.Colour.dark_gold())
            embed.set_author(name="Нехватка аргументов в команде.")
            embed.description = f"{ctx.author.mention} недостаточно аргументов в команде, которую вы используете."
            embed.set_footer(text="Ниже представлена дополнительная информация")
            await ctx.send(embed=embed)
            await ctx.send_help(ctx.command)
        elif isinstance(error, commands.NoPrivateMessage):
            self.logger.debug(error)
            embed = discord.Embed(colour=discord.Colour.dark_gold())
            embed.set_author(name="Эта команда может быть использована только на сервере.")
            embed.description = f"{ctx.author.mention}, команда **{ctx.message.content.split()[0]}** не может быть " \
                                f"использована в `Личных Сообщениях`."
            await ctx.send(embed=embed)
        elif isinstance(error, commands.TooManyArguments):
            self.logger.debug(error)
            embed = discord.Embed(colour=discord.Colour.dark_gold())
            embed.set_author(name="Слишком много аргументов в команде.")
            embed.description = f"{ctx.author.mention} вы ввели аргументы, которые скорее всего не нужны здесь."
            embed.set_footer(text="Ниже представлена дополнительная информация")
            await ctx.send(embed=embed)
            await ctx.send_help(ctx.command)
        elif isinstance(error, commands.CommandNotFound):
            self.logger.debug(error)
            embed = discord.Embed(colour=discord.Colour.red())
            embed.set_author(name="Команда не найдена.")
            embed.description = f"Комадна **{ctx.message.content.split()[0]}** не существует или вы ошиблись в ее " \
                                f"написании."
            await ctx.send(embed=embed)
        elif isinstance(error, commands.CommandOnCooldown):
            self.logger.debug(error)
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
            self.logger.debug(error)
            embed = discord.Embed(colour=discord.Colour.red())
            embed.set_author(name="Аргументы не соотсвуют нужным типам.")
            embed.description = f"Похоже, что тип данных, который вы ввели в качестве аргумента не соотсвутует " \
                                f"нужному. Доп. информация:\n **{error}**"
            await ctx.send(embed=embed)
            await ctx.send_help(ctx.command)
        else:
            self.logger.debug(error)
            embed = discord.Embed(colour=discord.Colour.dark_red())
            embed.set_author(name="Произошло непредвиденное исключение.")
            embed.description = str(error)
            await ctx.send(embed=embed)
