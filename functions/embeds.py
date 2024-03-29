import discord
import datetime
import io
import time
import random
import requests


async def member_join(member):
    now = datetime.datetime.now()
    embed = discord.Embed(
        colour=discord.Colour.from_rgb(52, 163, 0)
    )
    embed.set_author(name=f"В {now.strftime('%H:%M')} на сервер {member.guild.name} зашёл {member.name}.",
                     icon_url=member.guild.icon_url)
    embed.add_field(name='Информация:',
                    value=f'DiscordID:`{member.id}`'
                          f'\nDiscordTag:`{member.name}#{member.discriminator}`',
                          inline=False)
    embed.set_thumbnail(url=member.avatar_url)
    embed.set_footer(text=f"{member.name} | {member.guild.name} | {now.strftime('%d.%m.%Y')}")
    return embed


async def member_exit(member):
    now = datetime.datetime.now()
    embed = discord.Embed(colour=discord.Colour.from_rgb(54, 57, 63))
    embed.set_author(name=f"В {now.strftime('%H:%M')} с сервера {member.guild.name} ушёл {member.name}.",
                     icon_url=member.guild.icon_url)
    embed.add_field(name='Информация на момент выхода:',
                    value=f'DiscordID:`{member.id}`'
                          f'\nDiscordTag:`{member.name}#{member.discriminator}`',
                    inline=False)
    embed.set_thumbnail(url=member.avatar_url)
    embed.set_footer(text=f"{member.name} | {member.guild.name} | {now.strftime('%d.%m.%Y')}")
    return embed


async def message_edit(before, after):
    now = datetime.datetime.now()
    embed = discord.Embed(colour=discord.Colour.from_rgb(54, 57, 63))
    content_before = before.content
    content_after = after.content
    check = False

    if len(before.content) > 100:
        content_before = before.content[0:100] + "..."
        check = True
    if len(after.content) > 100:
        content_after = after.content[0:100] + "..."
        check = True

    if check:
        with io.open("stuff/changelog.txt", "w", encoding='utf8') as file:
            file.write("Сообщение до:\n" + before.content +
                       "\n\n\n\n" +
                       "Сообщение после:\n" + after.content)

    embed.set_author(name="Изменение в контексте сообщения.", icon_url=before.guild.icon_url)
    embed.add_field(name="Время изменения", value=now.strftime('%H:%M'))
    embed.add_field(name="Канал", value=before.channel.mention)
    embed.add_field(name="Пользователь", value=before.author.name)
    embed.add_field(name='Сообщение до и после:',
                    value=f'**До**: {content_before}'
                          f'\n**После**: {content_after}',
                    inline=False)
    embed.set_thumbnail(url=before.author.avatar_url)
    embed.set_footer(text=f"{before.guild.name} | {before.channel.name} | {now.strftime('%d.%m.%Y')}")
    return embed


async def profile(all_data, **kwargs):
    now = datetime.datetime.now()

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

    embed = discord.Embed(colour=discord.Colour.from_rgb(54, 57, 63))
    embed.set_author(name=f"Профиль игрока {kwargs['name']}", icon_url=kwargs["icon_url"])
    embed.set_thumbnail(url=kwargs["avatar_url"])
    embed.add_field(name='Дискорд:', value=kwargs["mention"])
    embed.add_field(name=all_data['name_of_currency'].title(), value=str(all_data['money']))
    embed.add_field(name=f"Зол. {all_data['name_of_currency'].title()}:", value=str(all_data['gold_money']))
    embed.add_field(name='Рейтинг:', value=str(all_data['rating']))
    embed.add_field(name='Ваш SteamID:', value=str(all_data['steamid']), inline=False)
    embed.add_field(name='Всё время игры:', value=str(all_time))
    embed.add_field(name='Ник:', value=str(all_data['nick']))
    embed.add_field(name='Ранг:', value=str(all_data['rank']))
    embed.set_footer(text="{} | {} | {}".format(kwargs['name'], kwargs['guild_name'], now.strftime('%d.%m.%Y')))
    return embed


async def delete_message(message, content):
    now = datetime.datetime.now()
    embed = discord.Embed(colour=discord.Colour.from_rgb(54, 57, 63))
    embed.set_author(name="Удаление сообщения из канала.", icon_url=message.guild.icon_url)
    embed.add_field(name="Время изменения", value=now.strftime('%H:%M'))
    embed.add_field(name="Канал", value=message.channel.mention)
    embed.add_field(name="Пользователь", value=message.author.name)
    embed.add_field(name='Текст сообщения:', value=content, inline=False)
    if message.attachments:
        if requests.head(message.attachments[0].proxy_url) == 200:
            embed.add_field(name='Вложение:', value=message.attachments[0].proxy_url, inline=False)
    embed.set_thumbnail(url=message.author.avatar_url)
    embed.set_footer(text=f"{message.author.name} | {message.channel.name} | {now.strftime('%d.%m.%Y')}")
    return embed


async def raw_delete_message(user, channel, id):
    now = datetime.datetime.now()

    embed = discord.Embed(colour=discord.Colour.from_rgb(54, 57, 63))
    embed.set_author(name=f"В {now.strftime('%H:%M')} на сервере {channel.guild.name} было удаленно сообщение "
                          f"в канале {channel.name}.",
                     icon_url=channel.guild.icon_url)
    embed.description = "Удалил: {}\n" \
                        "ID пользователя: `{}`\n" \
                        "ID сообщения: `{}`".format(user[0].mention, user[0].id, id)
    embed.set_thumbnail(url='https://www.pngarts.com/files/1/X-Shape-Free-PNG-Image.png')
    embed.set_footer(text=f"{channel.guild.name} | {channel.name} | {now.strftime('%d.%m.%Y | %H:%M')}")
    return embed


async def raw_edit_message(message):
    now = datetime.datetime.now()

    embed = discord.Embed(colour=discord.Colour.from_rgb(54, 57, 63))
    embed.set_author(name="Изменение в контексте сообщения.", icon_url=message.guild.icon_url)
    embed.add_field(name="Время изменения", value=now.strftime('%H:%M'))
    embed.add_field(name="Канал", value=message.channel.mention)
    embed.add_field(name="Пользователь", value=message.author.name)
    embed.add_field(name='Информация:',
                    value=f'**Текст сообщения:**`{message.content[0:100] + "..."}`'
                          f'\n**ID сообщения:**`{message.id}`',
                    inline=False)
    embed.set_thumbnail(url='http://cdn.onlinewebfonts.com/svg/img_355098.png')
    embed.set_footer(text=f"{message.guild.name} | {message.channel.name} | {now.strftime('%d.%m.%Y')}")
    return embed


async def purge(ctx, amount):
    now = datetime.datetime.now()
    embed = discord.Embed(colour=discord.Colour.from_rgb(54, 57, 63))
    embed.set_author(name=f"{ctx.author.name} воспользовался командой <удали> и удалил сообщения в количестве "
                          f"{amount} шт.")
    embed.set_thumbnail(url='http://cdn.onlinewebfonts.com/svg/img_229056.png')
    embed.set_footer(text=f"{ctx.guild.name} | {ctx.channel.name} | {now.strftime('%H:%M %d.%m.%Y')}")
    return embed
 

async def chance(ctx, win, thing, times):
    now = datetime.datetime.now()
    embed = discord.Embed(colour=discord.Colour.from_rgb(random.randint(0, 256),
                                                         random.randint(0, 256),
                                                         random.randint(0, 256)))
    embed.set_author(name=f"Шанс использован. Осталось {times}.")
    embed.description = f"Сегодня ваш куш составил **{win} {thing}**. " \
                        f"Но мы уверены, что в следующий раз вы получите больше!\n\n" \
                        f"Ваш Sunrails Metrostroi."
    embed.set_thumbnail(url=ctx.guild.icon_url)
    embed.set_footer(text=f"{ctx.guild.name} | {ctx.channel.name} | {now.strftime('%H:%M %d.%m.%Y')}")
    return embed


async def roullete(ctx, text, gif):
    now = datetime.datetime.now()
    embed = discord.Embed(colour=discord.Colour.from_rgb(random.randint(0, 256),
                                                         random.randint(0, 256),
                                                         random.randint(0, 256)))
    embed.set_author(name=f"Рулетка активированна.")
    embed.description = text
    embed.set_image(url=gif)
    embed.set_footer(text=f"{ctx.guild.name} | {ctx.channel.name} | {now.strftime('%H:%M %d.%m.%Y')}")
    return embed


async def invest(ctx, win, lose, sum, message):
    if win:
        embed = discord.Embed(
            colour=discord.Colour.dark_green()
        )
        embed.description = message.format(ctx.author.mention, sum, win)
    elif lose:
        embed = discord.Embed(
            colour=discord.Colour.dark_orange()
        )
        embed.description = message.format(ctx.author.mention, sum, lose)
    else:
        embed = discord.Embed(
            colour=discord.Colour.dark_red()
        )
        embed.description = message.format(ctx.author.mention)

    return embed


async def description(title, content):
    embed = discord.Embed(
        colour=discord.Colour.purple()
    )
    embed.set_author(name=title)
    embed.description = content
    return embed


async def promocode(title, content, create_admin, guild_icon):
    embed = discord.Embed(
        colour=discord.Colour.from_rgb(random.randint(0, 256),
                                       random.randint(0, 256),
                                       random.randint(0, 256))
    )

    gif_choice = [
        "https://i.gifer.com/jdI.gif",
        "https://i.gifer.com/1Fa4.gif",
        "https://i.gifer.com/3743.gif",
        "https://i.gifer.com/6mb.gif",
        "https://www.neizvestniy-geniy.ru/images/works/photo/2012/01/507550_1.gif",
        "https://i.gifer.com/4un.gif"
    ]

    gif = random.choice(gif_choice)

    embed.set_author(name=title)
    embed.description = content
    embed.set_image(url=gif)
    embed.set_thumbnail(url=guild_icon)
    embed.set_footer(text="Создано Администрацией Sunrails Metrostroi" if create_admin else "Создано автоматически")
    return embed


async def use_promo(title, content, guild_icon):
    embed = discord.Embed(colour=discord.Colour.from_rgb(240, 240, 240))

    embed.set_author(name=title)
    embed.description = content
    embed.set_image(url="https://i.gifer.com/3zt8.gif")
    embed.set_thumbnail(url=guild_icon)
    embed.set_footer(text="Приятной игры!\nВаш Sunrails Metrostroi.")

    return embed


async def swap(ctx, gold, revers, swaps):
    embed = discord.Embed(
        colour=discord.Colour.lighter_grey()
    )
    embed.description = swaps.format(ctx.author.mention, revers, "ревесивок", gold, "золотых реверсивок")
    return embed


async def ban_message(data_gamer):
    embed = discord.Embed(
        colour=discord.Colour.red()
    )
    embed.set_author(name=f'Информация по бану игрока с ником {data_gamer.SID.nick}')
    embed.add_field(name='SteamID:',
                    value=data_gamer.SID_id, inline=False)
    embed.add_field(name='Номер сервера: ',
                    value=data_gamer.server, inline=False)
    embed.add_field(name='Точная дата бана: ',
                    value=time.ctime(int(data_gamer.ban_date)), inline=True)
    embed.add_field(name='Дата разбана: ',
                    value='Примерно через ∞ мин.' if data_gamer.unban_date == 0 else time.ctime(int(data_gamer.unban_date)), inline=False)
    embed.add_field(name='Причина бана: ',
                    value=data_gamer.ban_reason, inline=False)
    embed.add_field(name='Администратор, выписавыший бан: ',
                    value=data_gamer.ban_admin, inline=False)
    return embed


async def check_ban(ban, client):
    embed = discord.Embed(
        colour=discord.Colour.red()
    )
    embed.set_author(name=f'Информация по бану игрока с ником {client.name}')
    embed.add_field(name='Ник забаненого:',
                    value=client.name, inline=False)
    embed.add_field(name='Дата разбана: ',
                    value='Примерно через ∞ мин.' if data_gamer.unban_date == 0 else time.ctime(int(data_gamer.unban_date)), inline=False)
    embed.add_field(name='Время, через сколько бан окончится: ',
                    value=f'{(int(time.time()) - ban.unban_date) // 60} мин.', inline=False)
    embed.add_field(name='Причина бана: ',
                    value=ban.reason, inline=False)
    embed.add_field(name='Администратор, выписавыший бан: ',
                    value=ban.ban_admin, inline=False)
    return embed


async def discord_check_ban(data_gamer):
    embed = discord.Embed(
        colour=discord.Colour.red()
    )
    embed.set_author(name=f'Информация по бану игрока {data_gamer.SID.nick}')
    embed.add_field(name='Точная дата бана: ',
                    value=time.ctime(int(data_gamer.ban_date)), inline=False)
    embed.add_field(name='Дата разбана: ',
                    value='Примерно через ∞ мин.' if data_gamer.unban_date == 0 else time.ctime(int(data_gamer.unban_date)), inline=False)
    embed.add_field(name='Причина бана: ',
                    value=data_gamer.ban_reason, inline=False)
    embed.add_field(name='Администратор, выписавыший бан: ',
                    value=data_gamer.ban_admin, inline=False)
    return embed


async def server_info(guild):
    time_date = datetime.datetime.strptime(str(guild.created_at), "%Y-%m-%d %H:%M:%S.%f")

    embed = discord.Embed(colour=discord.Colour.from_rgb(54, 57, 63))
    embed.set_author(name="{0.name}".format(guild))
    embed.add_field(name="Регион: ", value=str(guild.region).title())
    embed.add_field(name="ID гильдии: ", value=guild.id)
    embed.add_field(name="Системный канал: ", value="Не назначени" if not guild.system_channel
    else guild.system_channel.mention)
    embed.add_field(name="Количество участиков: ", value=guild.member_count)
    embed.add_field(name="Уровень верификации: ", value=guild.verification_level)
    embed.add_field(name="Роль по умолчанию: ", value=guild.default_role)
    embed.add_field(name="Дата создание", value=time_date.strftime("%d.%m.%Y %H:%M:%S"))
    embed.add_field(name="Лимит emoji: ", value=guild.emoji_limit)
    embed.add_field(name="Лимит участников: ", value="Безлимитно" if not guild.max_members else guild.max_members)
    embed.set_thumbnail(url=guild.icon_url)
    return embed


async def invest_help(ctx):
    now = datetime.datetime.now()
    embed = discord.Embed(colour=discord.Colour.from_rgb(54, 57, 63))
    embed.set_author(name="Некоторая информация о инвистициях и банке.",
                     icon_url=ctx.guild.icon_url)
    embed.add_field(name="Основная информация",
                    value="⠀⠀⠀⠀На каждом сервере, где есть бот, существует свой банк у которого есть свой курс и "
                          "название. Чтобы узнать курс или информацию о банке, можно воспользоваться командами "
                          "`к!курс` и `к!банк` соответсвенно.\n"
                          "⠀⠀⠀⠀Также на сервере существует своя валюта: <имя валюты> и зл. <имя валюты>. Первая "
                          "обычная, которую можно положить в банк, согласно курсу (обычно 1 ВС (валюта сервера) = "
                          "курсу банка), вторая, с приставкой \"зл.\", т.е. золотая, за которую админы могут продовать "
                          "роли на сервере. Также их можно кастомизировать, изменяя названия.\n"
                          "⠀⠀⠀⠀P.S. за курс взято отношение криптовалюты NEO к доллару",
                    inline=False)
    embed.add_field(name="Счёт в банке",
                    value="⠀⠀⠀⠀Само собой хранить деньги в воздухе - это не лучшая идея, поэтому в банке существует "
                          "счёт, который вам сначало нужно открыть, воспользовавшись командой `к!открыть_счёт` "
                          "(с буквой ё). Как только вы её ввели, поздравляю, счёт открыть. Дальше, можно совершать "
                          "операции с ним. Т.к. перевод денег возможен только с счёта на счёт, то вы можете "
                          "предоставить вашему другу номер своего счёта (номер счёта - это ваш discord id), на который "
                          "он может перевести деньги, если требуется.\n"
                          "⠀⠀⠀⠀Раз счёт можно отркыть, следственно закрыть его тоже возможно. НО закрывая счёт вы "
                          "теряете все свои деньги.\n"
                          "⠀⠀⠀⠀\"Зачем закрывать счёт?\" - спросите вы, а я отвечу: \"Не знаю.\"",
                    inline=False)
    embed.add_field(name="Инвистиции",
                    value="⠀⠀⠀⠀Наконец, подошли к самому главному, это инвистиции. Итак, для начало, нужно выбрать "
                          "куда вкладывать, иначе, смысла в получении прибыли нет. При вводе команды `к!ивест_статус`, "
                          "вам выводится состояние компаний и некоторая дополнительная информация, которая может "
                          "подсказать вам, куда лучше всего направить свой капитал. Далее вы просто вводите "
                          "команду `к!купить_акции` <название компании/количество акций> и просто ждёте увелечения "
                          "стоимости акций. Если вы всё сделали правильно, то прибыл не заставит себя долго ждать. "
                          "НО учите, также что вы можете всё поетрять.",
                    inline=False)
    embed.description = f"При появлении проблем, писать -> Rise#3047"
    embed.set_footer(text=f"{ctx.guild.name} | {ctx.channel.name} | {now.strftime('%H:%M %d.%m.%Y')}")
    return embed


async def bank_info(ctx, all_amount, course, name_of_bank):
    now = datetime.datetime.now()
    embed = discord.Embed(colour=discord.Colour.from_rgb(54, 57, 63))
    embed.set_author(name="{} банк".format(name_of_bank.title()))
    embed.add_field(name="Директор банка: ", value=ctx.guild.owner.mention, inline=False)
    embed.add_field(name="Нынешнее состояние: ", value=f"{all_amount} NEO", inline=False)
    embed.add_field(name="Курс: ", value=f"{course} NEO", inline=False)
    embed.set_footer(text=f"{ctx.guild.name} | {ctx.channel.name} | {now.strftime('%H:%M %d.%m.%Y')}")
    return embed


async def bill(ctx, info, bank):
    now = datetime.datetime.now()
    embed = discord.Embed(colour=discord.Colour.from_rgb(54, 57, 63))
    embed.set_author(name="Счёт №{}".format(info[0]))
    embed.add_field(name="Нынешнее состояние: ", value=f"{str(info[2])} NEO", inline=False)
    embed.add_field(name="Имя банка, в котором открыть счёт: ", value=bank['name'], inline=False)
    embed.add_field(name="Дата создания счёта: ", value=str(time.ctime(int(info[3]))), inline=False)
    embed.set_footer(text=f"{ctx.guild.name} | {ctx.channel.name} | {now.strftime('%H:%M %d.%m.%Y')}")
    return embed


async def invests_status(ctx, info):
    now = datetime.datetime.now()
    embed = discord.Embed(colour=discord.Colour.from_rgb(54, 57, 63))
    embed.set_author(name="Статус компаний")
    embed.add_field(name="Первая компания: ",
                    value=f"Название: **{info['first_company']['name']}**"
                          f"\nСтоимость акций: **{info['first_company']['share_price']} NEO**"
                          f"\nПроцент повышения стоимости: **{info['first_company']['percent_of_lucky']}%**",
                    inline=False)
    embed.add_field(name="Вторая компания: ",
                    value=f"Название: **{info['second_company']['name']}**"
                          f"\nСтоимость акций: **{info['second_company']['share_price']} NEO**"
                          f"\nПроцент повышения стоимости: **{info['second_company']['percent_of_lucky']}%**",
                    inline=False)
    embed.add_field(name="Третья компания: ",
                    value=f"Название: **{info['third_company']['name']}**"
                          f"\nСтоимость акций: **{info['third_company']['share_price']} NEO**"
                          f"\nПроцент повышения стоимости: **{info['third_company']['percent_of_lucky']}%**",
                    inline=False)
    embed.set_footer(text=f"{ctx.guild.name} | {ctx.channel.name} | {now.strftime('%H:%M %d.%m.%Y')}")
    return embed


async def share(ctx, info):
    now = datetime.datetime.now()
    embed = discord.Embed(colour=discord.Colour.from_rgb(54, 57, 63))
    embed.set_author(name="Приобретенные акции")
    try:
        info['first_company_count']
    except:
        info['first_company_count'] = 0

    try:
        info['second_company_count']
    except:
        info['second_company_count'] = 0

    try:
        info['third_company_count']
    except:
        info['third_company_count'] = 0
    embed.add_field(name="Первая компания: ",
                    value=f"Количество акций: **{info['first_company']}** шт.\n"
                          f"Цена приобретения: **{info['first_company_count']}** NEO",
                    inline=False)
    embed.add_field(name="Вторая компания: ",
                    value=f"Количество акций: **{info['second_company']}** шт.\n"
                          f"Цена приобретения: **{info['second_company_count']}** NEO",
                    inline=False)
    embed.add_field(name="Третья компания: ",
                    value=f"Количество акций: **{info['third_company']}** шт.\n"
                          f"Цена приобретения: **{info['third_company_count']}** NEO",
                    inline=False)
    embed.set_footer(text=f"{ctx.guild.name} | {ctx.channel.name} | {now.strftime('%H:%M %d.%m.%Y')}")
    return embed


async def poll(ctx, quest, answers):
    now = datetime.datetime.now()

    simbols = [":one:", ":two:", ":three:", ":four:", ":five:", ":six:", ":seven:", ":eight:", ":nine:", ":ten:"]
    things = list()

    for answer, i in zip(answers, range(0, 9)):
        things.append(f"{simbols[i]} {answer}")

    embed = discord.Embed(colour=discord.Colour.from_rgb(54, 57, 63))
    embed.set_author(name=quest)
    embed.description = '\n'.join([thing for thing in things])
    embed.set_footer(text=f"Время создания: {now.strftime('%H:%M %d.%m.%Y')} | Сделал: {ctx.author.nick}")
    return embed


async def poll_time(ctx, quest, time, answers, emoji):
    now = datetime.datetime.now()
    time_end = datetime.datetime.now(datetime.timezone(datetime.timedelta(minutes=time + 180)))

    simbols = [":one:", ":two:", ":three:", ":four:", ":five:", ":six:", ":seven:", ":eight:", ":nine:", ":ten:"]
    things = list()

    for answer, i in zip(answers, range(0, 9)):
        things.append(f"{simbols[i]} - {answer[0].title() + answer[1::]}")

    embed = discord.Embed(colour=discord.Colour.from_rgb(54, 57, 63))
    embed.set_author(name=quest)
    for answer in answers:
        embed.add_field(name=answer[0].title() + answer[1::],
                        value=emoji,
                        inline=False)
    embed.description = '\n'.join([thing for thing in things])
    embed.set_footer(text=f"Время создания: {now.strftime('%H:%M %d.%m.%Y')} | "
                          f"Сделал: {ctx.author.name} | "
                          f"Время до окончания {time_end.strftime('%H:%M %d.%m.%Y')}")
    return embed


async def all_members(ctx, all_data):
    now = datetime.datetime.now()

    embed = discord.Embed(colour=discord.Colour.from_rgb(54, 57, 63))
    embed.set_author(name="Участники РП-сессии")

    if len(all_data) == 1:
        embed.description = "Не смотри сюда. Здесь нет ничего."
        embed.set_footer(text=f"{ctx.guild.name} | {ctx.channel.name} | {now.strftime('%H:%M %d.%m.%Y')}")
        return embed

    things = list()
    for data in all_data:
        if "дцх" in data:
            things.append(f"`ДЦХ` **__{data[0]}__** по {data[5]}-й линии")
    for data in all_data:
        if "дсцп" in data:
            things.append(f"`ДСЦП` **__{data[0]}__** по станции `{data[4]}`")
    for data in all_data:
        if "маневровый" in data:
            things.append(f"`Маневровый машинист` **__{data[0]}__** по станции `{data[4]}`")

    drivers = list(list())
    for data in all_data:
        if "машинист" in data:
            drivers.append([int(data[3]), data[0]])

    drivers = sorted(drivers, key=lambda driver: driver[0])

    for i in range(0, len(drivers)):
        things.append(f"`Машинист` **__{drivers[i][1]}__**. Номер маршрута `{drivers[i][0]}`")

    embed.description = '\n'.join([thing for thing in things])
    embed.set_footer(text=f"{ctx.guild.name} | {ctx.channel.name} | {now.strftime('%H:%M %d.%m.%Y')}")
    return embed


async def present(thing, amount, user_icon):
    gif = "https://i.gifer.com/2EL.gif"

    embed = discord.Embed(
        colour=discord.Colour.from_rgb(random.randint(0, 256),
                                       random.randint(0, 256),
                                       random.randint(0, 256))
    )

    embed.set_author(name="Поздравляем с наступающим Новым Годом!")
    embed.description = f"Вот Ваш подарок на **{amount} {thing}**. Мы рады что вы с нами и хотели бы, " \
                        f"чтобы новый год прошел для вас намного лучше!"
    embed.set_image(url=gif)
    embed.set_thumbnail(url=user_icon)
    embed.set_footer(text="С новым 2021 годо!\nВаш Sunrails Metrostroi.")
    return embed


async def news(message):
    now = datetime.datetime.now()

    embed = discord.Embed(
        colour=discord.Colour.from_rgb(60, 66, 241),
        title=f"Sunrails Metrostroi"
    )

    embed.set_author(name=message.author.name)
    embed.description = message.content

    embed.set_footer(text=f"Новость опубликована в {now.strftime('%H:%M %d.%m.%Y')}",
                     icon_url=message.guild.icon_url)

    return embed

# async def achievement(member, achievement, guild):
#     now = datetime.datetime.now()
#
#     embed = discord.Embed(colour=discord.Colour.from_rgb(0, 33, 55))
#
#     with open("language/achievements.json", "r", encoding="utf8") as file:
#         info = json.load(file)
#         embed.set_author(name=f"{member.name} выполнил достижение!\n{info[achievement]['title']}")
#         embed.set_image(url=info[achievement]["image"])
#         embed.description = f'{info[achievement]["text"]}\nОн получит `{info[achievement]["reward"]} рейтинга!`'
#         embed.set_footer(text=f"{guild.name} | {guild.system_channel.name} | {now.strftime('%H:%M %d.%m.%Y')}")
#
#     return embed, info[achievement]["reward"]


async def first_april(ctx, win, thing):
    phraze = {
        297421866828693505: "О, Борис Сергеевич, как неожиданно и приятно. Вот ваши 100 000 000 реверсивок.",
        269452196104372225: "ЧСВ? Ну и ладно. Вот твои 100 000 000 реверсивок.",
        413783383215177728: "Системный администратор Луис Ля Рошель, как вам такой подарок? Ваши 100 000 000 реверсивок.",
        302047054182612993: "Станислав Андреевич, позвольте увеличить ваш бюджет на 100 000 000 реверсивок.",
        199120058797129728: "Ista011 когда светофоры? Вот аванс в размере 100 000 000 реверсивок на всякий.",
        721308476709535775: "Яуза лучший поезд не так ли? Поэтому я считаю, что вы должны спонсировать его. Вот ваши 100 000 000 реверсивок.",
        314813205148991489: "Голубь? Зачем? Почему не орел? Почему не ястреб? Почему Голубь? Вот твои 100 000 000 реверсивок.",
        702105550514814987: "Л.К.М.С.З.Д - Люди Которые Могут Сажать Зеленые Деревья. Что? Ничего. Вот ваши 100 000 000 реверсивок.",
        326983105472888833: "Посейдон, посиди пожалуйста. Вот твои 100 000 000 реверсивок.",
        653309782987505695: "АХАХАХ ТУПОЙ ГРАШИК НИЧЕГО ТЕБЕ ОПЯТЬ НЕ ДА... О ладно, так уж и быть - 100 000 000 реверсивок твои.",
        256875988992917505: "Привет, как дела? Надеюсь хорошо. 100 000 000 реверсивок для поднятия настроения.",
        610803012754997288: "РЖД Егор - Российский железнодорожный Егор - звучит хайпово, поэтому лови 100 000 000 реверсивок.",
        484004162246279169: "Люблю волков, до момента где они тебя едят. Не ешь мены, держи 100 000 000 реверсивок.",
        323157479968210974: "Капитолик, Эндрю, Капитошка, Тонна Агентов Смитов - так кто ты? Лови 100 000 000 реверсивок и не страдай от биполярочки.",
        613479283473645568: "Боль в душе или боль в ногах? Нурофен (это не реклама) - решит твои проблемы. А он стоит 100 000 000 реверсивок.",
        349648699976318987: "Ржака та в том, что рисик то и придумал меня а в итоге получает столько сколько и все остальные.",
        349561004172115979: "Хаааай Дани, когда отдашь сотку? Ладно я тут подумала, вот тебе 100 000 000 реверсивок.",
        355035186297044992: "Блуфи фокс, как перевести твой ник? Фокс - лиса, а Блуфи? Ладно сам разберешься, вот тебе 100 000 000 реверсивок для размышления.",
        176241484465438721: "Инструктор 3 коллоны или мужчина с сексуальным голосом? Наконец-то мы начали задавать правильные вопросы. Лови 100 000 000 реверсивок.",
        580080770870411275: "Ягада малинка, укуси меня пчала А это твои 100 000 000 реверсивок.",
        566579942285115392: "Paula von Luzgen, we are losing him! Take your 100 000 000 revers and help!",
        637752353780662272: "Слыш аватарку вернул. Верни сделанного в бездне быстра. Вот тебе 100 000 000 реверсивок чтобы вернул."
    }

    now = datetime.datetime.now()
    embed = discord.Embed(colour=discord.Colour.from_rgb(random.randint(0, 256),
                                                         random.randint(0, 256),
                                                         random.randint(0, 256)))
    if ctx.author.id in phraze.keys():
        embed.set_author(name=f"Вау что это?")
        embed.description = phraze[ctx.author.id]
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.set_footer(text=f"{ctx.guild.name} | {ctx.channel.name} | {now.strftime('%H:%M %d.%m.%Y')}")
    else:
        embed.set_author(name=f"Рулетка активировона. {win} {thing}.")
        embed.description = f"Сегодня ваш куш составил **{win} {thing}**. " \
                            f"Но мы уверены, что в следующий раз вы получите больше!\n\n" \
                            f"Ваш Sunrails Metrostroi."
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.set_footer(text=f"{ctx.guild.name} | {ctx.channel.name} | {now.strftime('%H:%M %d.%m.%Y')}")
    return embed
