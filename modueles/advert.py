import random
import json

import logger
import logging
import discord
import httplib2
import googleapiclient.discovery

from collections import namedtuple
from discord.ext import commands
from oauth2client.service_account import ServiceAccountCredentials


logger = logging.getLogger("main_commands")
logger.setLevel(logging.INFO)


class Advert(commands.Cog, name="Объявления"):

    def __init__(self, client):

        self.client = client
        self.simbols = [":one:", ":two:", ":three:", ":four:", ":five:", ":six:", ":seven:", ":eight:", ":nine:", ":ten:"]

        with open('stuff/config.json', 'r', encoding='utf8') as config:
            js = json.load(config)
            self.SPREADSHEET_ID = js['spreadsheetid']
            # self.TOKEN_VK = js['madadev']['TOKEN_VK']
            # self.public = js['madadev']['public']
            # self.chat_id = js['madadev']['chat_id']

        self.CREDENTIALS_FILE = 'stuff/credentials.json'
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets',
                       'https://www.googleapis.com/auth/drive']

        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.CREDENTIALS_FILE,
                                                                       self.SCOPES)

        httpAuth = credentials.authorize(httplib2.Http())

        self.service = googleapiclient.discovery.build(
            'sheets', 'v4', http=httpAuth, cache_discovery=False)

        # self.session = vk_api.VkApi(token=self.TOKEN_VK)
        # self.vk = self.session.get_api()

        Images = namedtuple('Images', 'multiplayer meeting techwork update')
        self.images = Images(
            "https://i.ibb.co/t2fRcX6/multiplayer.jpg",
            "https://i.ibb.co/vVbwfpm/sobranie.jpg",
            "https://i.ibb.co/Vq5jd2w/techwork.jpg",
            "https://i.ibb.co/411Szyc/update.jpg"
        )

        self.random_images = {
            "https://i.ibb.co/Sn0Dbgt/photo-2021-08-22-11-08-02.jpg",
            "https://i.ibb.co/xsx59fZ/photo-2021-08-22-11-07-22.jpg",
            "https://i.ibb.co/2nX58S5/photo-2021-08-22-11-07-40.jpg",
            "https://i.ibb.co/kHWj12p/photo-2021-08-22-11-08-19.jpg"
        }

    def multiplayer(self):
        embed = discord.Embed(colour=discord.Colour.from_rgb(97, 152, 255),
                              title=f'{self.data[1]} Мультиплеер {self.data[2]}',
                              url=self.data[5])
        
        embed.add_field(name='Общие положения:',
                        value=f'`Время сбора`: **{self.data[3]}** по МСК' \
                              f'\n`Время начала`: **{self.data[4]}** по МСК',
                        inline=False)

        embed.add_field(name='Основная информация:',
                        value=f'`ТЧД`: **{self.data[6]}**\n`Маршрут`: **{self.data[7]}**' \
                              f'\n`Участок`: **{self.data[8]}**\n`Электрификация`: **{self.data[9]}**' \
                              f'\n`Время`: **{self.data[10]}**',
                        inline=False)
        
        if self.extra:
            embed.add_field(name='Дополнительная информация:',
                            value=self.extra[0],
                            inline=False)

        embed.set_image(url=self.images.multiplayer)

        embed.set_footer(text="Приятной игры!")

        return embed
    
    # def multiplayer_vk(self):
    #     text = f'🚂{self.data[1]} Мультиплеер {self.data[2]}🚂' \
    #            f'\nВремя сбора: {self.data[3]} по МСК' \
    #            f'\nВремя начала: {self.data[4]} по МСК' \
    #            f'\n\nИнформация о смене:' \
    #            f'\nТЧД: {self.data[6]}' \
    #            f'\nМаршрут: {self.data[7]}' \
    #            f'\nУчасток: {self.data[8]}' \
    #            f'\nЭлектрификация: {self.data[9]}' \
    #            f'\nВремя: {self.data[10]}' \
    #            f'\n\n{self.data[5]}'
    #
    #     if self.extra:
    #         extra = f'\n\nДополнительно:' \
    #                 f'\n{self.extra[0]}'
    #     else:
    #         extra = ''
    #
    #     post_id = self.vk.wall.post(owner_id=-183054359,
    #                                 from_group=1,
    #                                 message=text + extra,
    #                                 attachments="photo-183054359_457239021")

    def user_multiplayer(self):
        embed = discord.Embed(colour=discord.Colour.from_rgb(23, 0, 235),
                              title=f'{self.data[1]} Пользовательский Мультиплеер {self.data[2]}',
                              url=self.data[5])
        
        embed.add_field(name='Общие положения:',
                        value=f'`Время сбора`: **{self.data[3]}** по МСК' \
                              f'\n`Время начала`: **{self.data[4]}** по МСК',
                        inline=False)

        embed.add_field(name='Основная информация:',
                        value=f'`ТЧД`: **{self.data[6]}**\n`Маршрут`: **{self.data[7]}**' \
                              f'\n`Участок`: **{self.data[8]}**\n`Электрификация`: **{self.data[9]}**' \
                              f'\n`Время`: **{self.data[10]}**',
                        inline=False)
        
        if self.extra:
            embed.add_field(name='Дополнительная информация:',
                            value=self.extra[0],
                            inline=False)

        embed.set_image(url=random.choices(self.random_images)[0])

        embed.set_footer(text="Приятной игры!")

        return embed

    
    # def user_multiplayer_vk(self):
    #     text = f'🚞{self.data[1]} Пользовательский Мультиплеер {self.data[2]}🚞' \
    #            f'\nВремя сбора: {self.data[3]} по МСК' \
    #            f'\nВремя начала: {self.data[4]} по МСК' \
    #            f'\n\nИнформация о смене:' \
    #            f'\nТЧД: {self.data[6]}' \
    #            f'\nМаршрут: {self.data[7]}' \
    #            f'\nУчасток: {self.data[8]}' \
    #            f'\nЭлектрификация: {self.data[9]}' \
    #            f'\nВремя: {self.data[10]}' \
    #            f'\n\n{self.data[5]}'
    #
    #     if self.extra:
    #         extra = f'\n\nДополнительно:' \
    #                 f'\n{self.extra[0]}'
    #     else:
    #         extra = ''
    #
    #     post_id = self.vk.wall.post(owner_id=-183054359,
    #                                 from_group=1,
    #                                 message=text + extra,
    #                                 attachments="photo-183054359_457239037")
    #
    #     post = f'wall-{self.public}_{post_id}'
    #
    #     self.vk.messages.send(chat_id=self.chat_id,
    #                           random=12,
    #                           attachments=post)
    
    def metro_multiplayer(self):
        embed = discord.Embed(colour=discord.Colour.from_rgb(0, 238, 255),
                              title=f'{self.data[1]} Мультиплеер Метрополитена {self.data[2]}',
                              url=self.data[5])
        
        embed.add_field(name='Общие положения:',
                        value=f'`Время сбора`: **{self.data[3]}** по МСК' \
                              f'\n`Время начала`: **{self.data[4]}** по МСК',
                        inline=False)

        embed.add_field(name='Основная информация:',
                        value=f'`Организатор`: **{self.data[6]}**\n`Карта`: **{self.data[7]}**' \
                              f'\n`Участок`: **{self.data[8]}**\n`Частота дешифратор`: **{self.data[9]}**' \
                              f'\n`Вагонов на человека`: **{self.data[10]}**',
                        inline=False)
        
        if self.extra:
            embed.add_field(name='Дополнительная информация:',
                            value=self.extra[0],
                            inline=False)

        embed.set_image(url="http://transport-games.ru/uploads/monthly_2018_07/6JMdhKPfo3c.jpg.6d0e9eb9cf28d4eb8e4e13bce3af78ed.jpg")

        embed.set_footer(text="Приятной игры!")

        return embed

    # def metro_multiplayer_vk(self):
    #     text = f'🚞{self.data[1]} Мультиплеер Метрополитена {self.data[2]}🚞' \
    #            f'\nВремя сбора: {self.data[3]} по МСК' \
    #            f'\nВремя начала: {self.data[4]} по МСК' \
    #            f'\n\nИнформация о смене:' \
    #            f'\nОрганизатор: {self.data[6]}' \
    #            f'\nКарта: {self.data[7]}' \
    #            f'\nУчасток: {self.data[8]}' \
    #            f'\nЧастота дешифратор: {self.data[9]}' \
    #            f'\nВагонов на человека: {self.data[10]}' \
    #            f'\n\n{self.data[5]}'
    #
    #     if self.extra:
    #         extra = f'\n\nДополнительно:' \
    #                 f'\n{self.extra[0]}'
    #     else:
    #         extra = ''
    #
    #     post_id = self.vk.wall.post(owner_id=-183054359,
    #                                 from_group=1,
    #                                 message=text + extra,
    #                                 attachments="photo-183054359_457239030")
    #
    #     post = f'wall-{self.public}_{post_id}'
    #
    #     self.vk.messages.send(chat_id=self.chat_id,
    #                           random=12,
    #                           attachments=post)
    
    def meeting(self):
        embed = discord.Embed(colour=discord.Colour.from_rgb(81, 255, 0),
                              title=f'Собрание пользователей {self.data[2]}')
        
        embed.add_field(name='Общее положение:',
                        value=f'`Время начала`: **{self.data[3]}** по МСК',
                        inline=False)

        themes = self.data[4].split('*')

        embed.add_field(name='Темы для обсуждения:',
                        value=''.join(f'{simbol}. {theme}\n' for simbol, theme in zip(self.simbols, themes)),
                        inline=False)

        if self.extra:
            embed.add_field(name='Дополнительно:',
                            value=self.extra[0],
                            inline=False)

        embed.set_image(url=self.images.meeting)

        embed.set_footer(text="Ждём Вас!")

        return embed
    
    # def meeting_vk(self):
    #     text = f'Дорогие участники проекта MaDaDev RTS!📢' \
    #            f'\n\n{self.data[2]} в {self.data[3]} по МСК на нашем Discord сервере состоится '\
    #            f'общее собрание участников. Сделаем пару объявлений, а так же ответим на все ваши вопросы!👥' \
    #            f'\nЖдём всех!❤' \
    #            f'\n\nкНаш Discord - https://discord.gg/Uhs5zbF5uQ ☎'
    #
    #     if self.extra:
    #         extra = f'\n\nДополнительно:' \
    #                 f'\n{self.extra[0]}'
    #     else:
    #         extra = ''
    #
    #     post_id = self.vk.wall.post(owner_id=-183054359,
    #                                 from_group=1,
    #                                 message=text + extra,
    #                                 attachments="photo-183054359_457239029")
    #
    #     post = f'wall-{self.public}_{post_id}'
    #
    #     self.vk.messages.send(chat_id=self.chat_id,
    #                           random=12,
    #                           attachments=post)

    def tech_work(self):
        embed = discord.Embed(colour=discord.Colour.from_rgb(255, 0, 81),
                              title=f'Технические работы')
        
        embed.add_field(name='Основная информация по техническим работам:',
                        value=f'`Причина`: **{self.data[2]}**' \
                              f'\n`Начало - конец`: **{self.data[3]}**' \
                              f'\n\nПриносим извинения за предоставленные неудобства.',
                        inline=False)

        if self.extra:
            embed.add_field(name='Дополнительно:',
                            value=self.extra[0],
                            inline=False)

        embed.description = 'Приносим свои извинения за предоставленные неудобства.'

        embed.set_image(url=self.images.techwork)

        embed.set_footer(text="Скоро все починим!")

        return embed
    
    # def tech_work_vk(self):
    #     text = f'‼Уважаемые пользователи‼' \
    #            f'\nПроводятся технические работы, сервисы MaDaDev RTS могут быть недоступны.'\
    #            f'\n\nПричина: {self.data[2]}' \
    #            f'\nПримерное время начала-конца: {self.data[3]}' \
    #            f'\n\nПриносим извинения за предоставленные неудобства.' \
    #            f'\nС Уважением, Руководитель проекта Louis La Roshelle'
    #
    #     if self.extra:
    #         extra = f'\n\nДополнительно:' \
    #                 f'\n{self.extra[0]}'
    #     else:
    #         extra = ''
    #
    #
    #     post_id = self.vk.wall.post(owner_id=-183054359,
    #                                 from_group=1,
    #                                 message=text + extra,
    #                                 attachments="photo-183054359_457239022")
    #
    #     post = f'wall-{self.public}_{post_id}'
    #
    #     self.vk.messages.send(chat_id=self.chat_id,
    #                           random=12,
    #                           attachments=post)

    def update_game(self):
        embed = discord.Embed(colour=discord.Colour.from_rgb(238, 255, 0),
                              title=f'Обновление сборки',\
                              url=self.data[3])
        
        embed.add_field(name='Дата:',
                        value=f'**{self.data[2]}**',
                        inline=False)
        
        themes = self.data[4].split('*')

        # embed.add_field(name='Изменение в обновлении:',
        #                 value=''.join(f'{i + 1} {theme}\n' for i, theme in zip(range(0, len(themes)), themes)),
        #                 inline=False)
        
        embed.add_field(name='Изменение в обновлении:',
                        value=''.join(f'{simbol} {theme}\n' for simbol, theme in zip(self.simbols, themes)),
                        inline=False)
        
        if self.extra:
            embed.add_field(name='Дополнительно:',
                            value=self.extra[0],
                            inline=False)


        embed.set_image(url=self.images.update)

        embed.set_footer(text="Приятной игры!")

        return embed
    
    # def update_game_vk(self):
    #
    #     themes = self.data[4].split('*')
    #
    #     start_text = f'Доброго времени суток!👋🏻' \
    #            f'\n✅Обновление сборки от {self.data[2]} года!🎉' \
    #            f'\n\nНа данный момент были сделаны следующие изменения сборки:\n'
    #
    #     middle_text = ''.join(f'{i + 1}. {theme}\n' for i, theme in zip(range(0, len(themes)), themes))
    #
    #     end_text = f'\n\nОбновление:\n{self.data[3]}' \
    #                f'\n\nС уважением, команда MaDaDev❤'
    #
    #     if self.extra:
    #         extra = f'\n\nДополнительно:' \
    #                 f'\n{self.extra[0]}'
    #     else:
    #         extra = ''
    #
    #     text = start_text + middle_text + end_text + extra
    #
    #     post_id = self.vk.wall.post(owner_id=-183054359,
    #                                 from_group=1,
    #                                 message=text,
    #                                 attachments="photo-183054359_457239024")
    #
    #     post = f'wall-{self.public}_{post_id}'
    #
    #     self.vk.messages.send(chat_id=self.chat_id,
    #                           random=12,
    #                           attachments=post)

    def request(self):
        embed = discord.Embed(colour=discord.Colour.from_rgb(255, 0, 81),
                              title=f'Заявки на должности!')
        
        embed.add_field(name='Основная информация по заявка на должность работам:',
                        value=f'Дорогие участники проекта MaDaDev RTS!🎉',
                        inline=False)

        vacancies = self.data[2].split('*')
        links = self.data[3].split('*')
        
        embed.add_field(name='Вакансии:',
                        value=''.join(f'{simbol} [{theme}]({link})\n' for simbol, theme, link in zip(self.simbols, vacancies, links)),
                        inline=False)
    
        if self.extra:
            embed.add_field(name='Дополнительно:',
                            value=self.extra[0],
                            inline=False)

        embed.set_image(url=self.data[4] if (4 < len(self.data)) else random.choices(self.random_images)[0])

        embed.set_footer(text="Удачи!")

        return embed

    # def request_vk(self):
    #
    #     vacancies = self.data[2].split('*')
    #     links = self.data[3].split('*')
    #
    #     start_text = f'Доброго времени суток!👋🏻' \
    #                  f'\n✅Объявляются открытими заявки на следующие должности:\n\n'
    #
    #     middle_text = ''.join(f'{i + 1}. [{theme}|{link}]\n' for i, theme, link in zip(range(0, len(vacancies)), vacancies, links))
    #
    #     if self.extra:
    #         extra = f'\n\nДополнительно:' \
    #                 f'\n{self.extra[0]}'
    #     else:
    #         extra = ''
    #
    #     text = start_text + middle_text + extra
    #
    #     post_id = self.vk.wall.post(owner_id=-183054359,
    #                                 from_group=1,
    #                                 message=text,
    #                                 attachments="photo-183054359_457239024")
    #
    #     post = f'wall-{self.public}_{post_id}'
    #
    #     self.vk.messages.send(chat_id=self.chat_id,
    #                           random=12,
    #                           attachments=post)
                
    def stream(self):
        embed = discord.Embed(colour=discord.Colour.from_rgb(255, 0, 81),
                              title=self.data[4],
                              url=self.data[6])
        
        embed.add_field(name='Дата и время:',
                        value=f'{self.data[2]} в {self.data[3]}')
        
        embed.description = self.data[5]
    
        if self.extra:
            embed.add_field(name='Дополнительно:',
                            value=self.extra[0],
                            inline=False)

        embed.set_image(url=self.data[7] if (7 < len(self.data)) else random.choices(self.random_images)[0])

        embed.set_footer(text="Ждем Вас!")

        return embed
    
    def another(self):
        embed = discord.Embed(colour=discord.Colour.from_rgb(255, 255, 255),
                              title=self.data[1],
                              url=self.data[2] if self.data[2] else None)
    
        if self.extra:
            embed.add_field(name='Основная информация:',
                            value=self.extra[0],
                            inline=False)

        embed.set_image(url=self.data[3] if (3 < len(self.data)) else random.choices(self.random_images)[0])

        embed.set_footer(text="Ваш MaDaDev RTS!")
        

        return embed

    @commands.command(name='объявление',
                      help="Дополнительные аргументы в этой команде не нужны.",
                      brief="<префикс>объявление",
                      description="Берет из Google таблицы доступную информацию и делает по ней объявление.")
    @commands.cooldown(1, 20, commands.BucketType.user)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def advert(self, ctx, is_multiplayer = False):
        await ctx.message.delete()

        main_values = self.service.spreadsheets().values().get(spreadsheetId=self.SPREADSHEET_ID,
                                                               range="adverts!D1:D11",
                                                               majorDimension="COLUMNS").execute()
    
        extra_values = self.service.spreadsheets().values().get(spreadsheetId=self.SPREADSHEET_ID,
                                                                range="adverts!C13:E13",
                                                                majorDimension="COLUMNS").execute()
        
        embed = None

        self.data = main_values['values'][0]
        try:
            self.extra = extra_values['values'][0]
        except Exception:
            self.extra = None

        if main_values['values'][0][0] == 'Мультиплеер':
            embed = self.multiplayer()
            # self.multiplayer_vk()
            is_multiplayer = True
        elif main_values['values'][0][0] == 'Пользовательский мультиплеер':
            embed = self.user_multiplayer()
            # self.user_multiplayer_vk()
            is_multiplayer = True
        elif main_values['values'][0][0] == 'Мультиплеер Метрополитена':
            embed = self.metro_multiplayer()
            # self.metro_multiplayer_vk()
            is_multiplayer = True
        elif main_values['values'][0][0] == 'Собрание пользователей':
            embed = self.meeting()
            # self.meeting_vk()
        elif main_values['values'][0][0] == 'Технические работы':
            embed = self.tech_work()
            # self.tech_work_vk()
        elif main_values['values'][0][0] == 'Обновление сборки':
            embed = self.update_game()
            # self.update_game_vk()
        elif main_values['values'][0][0] == 'Заявка на должности':
            embed = self.request()
            # self.request_vk()
        elif main_values['values'][0][0] == 'Стрим':
            embed = self.stream()
        elif main_values['values'][0][0] == 'Другое':
            embed = self.another()

        message = await ctx.send(embed=embed)

        if not is_multiplayer:
            return

        with open("stuff/config.json", "r+", encoding="utf8") as file:
            try:
                js = json.load(file)

                await message.add_reaction(js["madadev"]["reactions"]["open"])
                await message.add_reaction(js["madadev"]["reactions"]["close"])
                await message.add_reaction(js["madadev"]["reactions"]["finish"])

                js["madadev"]["message_advert"] = message.id
                js["madadev"]["advert_channel"] = ctx.channel.id
                js["madadev"]["info"]["date"] = self.data[2]
                js["madadev"]["info"]["name"] = self.data[1]

            except Exception as error:
                logger.error(error)
                await message.delete()
            else:
                file.seek(0)
                file.truncate(0)
            finally:
                json.dump(js, file, indent=4)
