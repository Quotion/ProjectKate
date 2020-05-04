import discord
import datetime
import io
import time


async def member_join(member):
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
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
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
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
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
    embed = discord.Embed(colour=discord.Colour.from_rgb(54, 57, 63))
    content_before = before.content
    content_after = after.content
    check = False

    if len(before.content) > 50:
        content_before = before.content[0:40] + "..."
        check = True
    if len(after.content) > 50:
        content_after = after.content[0:40] + "..."
        check = True

    if check:
        with io.open("changelog.txt", "w", encoding='utf8') as file:
            file.write("Сообщение до:\n" + before.content +
                       "\n\n\n\n" +
                       "Сообщение после:\n" + after.content)

    embed.set_author(name=f"В {now.strftime('%H:%M')} было изменено сообщение, отправленное {before.author.name}.",
                     icon_url=before.guild.icon_url)
    embed.add_field(name='Сообщение до и после:',
                    value=f'**До**: {content_before}'
                          f'\n**После**: {content_after}',
                    inline=False)
    embed.set_thumbnail(url=before.author.avatar_url)
    embed.set_footer(text=f"{before.guild.name} | {before.channel.name} | {now.strftime('%d.%m.%Y')}")
    return embed


async def profile(all_data, **kwargs):
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))

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
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
    embed = discord.Embed(colour=discord.Colour.from_rgb(54, 57, 63))
    embed.set_author(name=f"В {now.strftime('%H:%M')} на сервере {message.guild.name} было удаленно сообщение, "
                          f"отправленное {message.author.name}.",
                     icon_url=message.guild.icon_url)
    embed.add_field(name='Текст сообщения:',
                    value=content,
                    inline=False)
    embed.set_thumbnail(url=message.author.avatar_url)
    embed.set_footer(text=f"{message.author.name} | {message.channel.name} | {now.strftime('%d.%m.%Y')}")
    return embed


async def raw_delete_message(user, channel, id):
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))

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
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))

    embed = discord.Embed(colour=discord.Colour.from_rgb(54, 57, 63))
    embed.set_author(name=f"В {now.strftime('%H:%M')} на сервере {message.guild.name} было изменено сообщение, "
                          f"отправленное в канале {message.channel.name}.",
                     icon_url=message.guild.icon_url)
    embed.add_field(name='Информация:',
                    value=f'**Текст сообщения:**`{message.content[0:100] + "..."}`'
                          f'\n**ID сообщения:**`{message.id}`',
                    inline=False)
    embed.set_thumbnail(url='http://cdn.onlinewebfonts.com/svg/img_355098.png')
    embed.set_footer(text=f"{message.guild.name} | {message.channel.name} | {now.strftime('%d.%m.%Y')}")
    return embed


async def purge(ctx, amount):
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
    embed = discord.Embed(colour=discord.Colour.from_rgb(54, 57, 63))
    embed.set_author(name=f"{ctx.author.name} воспользовался командой <удали> и удалил сообщения в количестве "
                          f"{amount} шт.")
    embed.set_thumbnail(url='http://cdn.onlinewebfonts.com/svg/img_229056.png')
    embed.set_footer(text=f"{ctx.guild.name} | {ctx.channel.name} | {now.strftime('%H:%M %d.%m.%Y')}")
    return embed


async def roulette(ctx, win, thing):
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
    embed = discord.Embed(colour=discord.Colour.from_rgb(65, 115, 0))
    embed.set_author(name=f"Сегодня ваш выигрыш составляет {win} {thing} ")
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


async def description(author, content):
    embed = discord.Embed(
        colour=discord.Colour.purple()
    )
    embed.description = content.format(author)
    return embed


async def swap(ctx, gold, revers, swaps):
    embed = discord.Embed(
        colour=discord.Colour.lighter_grey()
    )
    embed.description = swaps.format(ctx.author.mention, revers, "ревесивок", gold, "золотых реверсивок")
    return embed


async def ban_message(message, author, steamid, time, reason):
    embed = discord.Embed(
        colour=discord.Colour.magenta()
    )
    embed.description = message.format(author, steamid, time, reason)
    return embed


async def check_ban(ban):
    embed = discord.Embed(
        colour=discord.Colour.red()
    )
    embed.set_author(name=f'Информация по бану игрока с ником {ban[1]}')
    embed.add_field(name='Ник забаненого:',
                    value=ban[1], inline=False)
    embed.add_field(name='Точная дата бана: ',
                    value=time.ctime(int(ban[7])), inline=True)
    embed.add_field(name='Время, через сколько бан окончится: ',
                    value=f'{(int(ban[6]) - int(time.time())) // 60} мин.', inline=False)
    embed.add_field(name='Причина бана: ',
                    value=ban[5], inline=False)
    embed.add_field(name='Администратор, выписавыший бан: ',
                    value=ban[4], inline=False)
    return embed


async def discord_check_ban(ban, player):
    embed = discord.Embed(
        colour=discord.Colour.red()
    )
    embed.set_author(name=f'Информация по бану игрока {player}')
    embed.add_field(name='Ник забаненого:',
                    value=ban[1], inline=False)
    embed.add_field(name='Точная дата бана: ',
                    value=time.ctime(int(ban[7])), inline=False)
    embed.add_field(name='Время, через сколько бан окончится: ',
                    value=f'{(int(ban[6]) - int(time.time())) // 60} мин.', inline=False)
    embed.add_field(name='Причина бана: ',
                    value=ban[5], inline=False)
    embed.add_field(name='Администратор, выписавыший бан: ',
                    value=ban[4], inline=False)
    return embed


async def server_info(guild):
    time_date = datetime.datetime.strptime(str(guild.created_at), "%Y-%m-%d %H:%M:%S.%f")

    embed = discord.Embed(colour=discord.Colour.from_rgb(54, 57, 63))
    embed.set_author(name="{0.name}".format(guild))
    embed.add_field(name="Регион: ", value=str(guild.region).title())
    embed.add_field(name="ID гильдии: ", value=guild.id)
    embed.add_field(name="Владелец: ", value=guild.owner.mention)
    embed.add_field(name="Количество участиков: ", value=guild.member_count)
    embed.add_field(name="Уровень верификации: ", value=guild.verification_level)
    embed.add_field(name="Роль по умолчанию: ", value=guild.default_role)
    embed.add_field(name="Дата создание", value=time_date.strftime("%d.%m.%Y %H:%M:%S"))
    embed.add_field(name="Лимит emoji: ", value=guild.emoji_limit)
    embed.add_field(name="Лимит участников: ", value="Безлимитно" if not guild.max_members else guild.max_members)
    embed.set_thumbnail(url=guild.icon_url)
    return embed


async def invest_help(ctx):
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
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
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
    embed = discord.Embed(colour=discord.Colour.from_rgb(54, 57, 63))
    embed.set_author(name="{} банк".format(name_of_bank.title()))
    embed.add_field(name="Директор банка: ", value=ctx.guild.owner.mention, inline=False)
    embed.add_field(name="Нынешнее состояние: ", value=f"{all_amount} NEO", inline=False)
    embed.add_field(name="Курс: ", value=f"{course} NEO", inline=False)
    embed.set_footer(text=f"{ctx.guild.name} | {ctx.channel.name} | {now.strftime('%H:%M %d.%m.%Y')}")
    return embed


async def bill(ctx, info, bank):
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
    embed = discord.Embed(colour=discord.Colour.from_rgb(54, 57, 63))
    embed.set_author(name="Счёт №{}".format(info[0]))
    embed.add_field(name="Нынешнее состояние: ", value=f"{str(info[2])} NEO", inline=False)
    embed.add_field(name="Имя банка, в котором открыть счёт: ", value=bank['name'], inline=False)
    embed.add_field(name="Дата создания счёта: ", value=str(time.ctime(int(info[3]))), inline=False)
    embed.set_footer(text=f"{ctx.guild.name} | {ctx.channel.name} | {now.strftime('%H:%M %d.%m.%Y')}")
    return embed


async def invests_status(ctx, info):
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
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
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
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

async def poll(ctx, quest, all_time, answers):
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))

    simbols = [":one:", ":two:", ":three:", ":four:", ":five:", ":six:", ":seven:", ":eight:", ":nine:", ":ten:"]
    things = list()

    for answer, i in zip(answers, range(0, 9)):
        things.append(f"{simbols[i]} {answer}")

    embed = discord.Embed(colour=discord.Colour.from_rgb(54, 57, 63))
    embed.set_author(name=quest)
    embed.description = '\n'.join([thing for thing in things])
    embed.set_footer(text=f"Время создания: {now.strftime('%H:%M %d.%m.%Y')} | Сделал: {ctx.author.nick}")
    return embed

async def all_members(ctx, all_data):
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))

    embed = discord.Embed(colour=discord.Colour.from_rgb(54, 57, 63))
    embed.set_author(name="Участники РП-сессии")

    if len(all_data) == 1:
        embed.description = "Здесь моглы бы быть ваша реклама, но тут её нет."
        embed.set_footer(text=f"{ctx.guild.name} | {ctx.channel.name} | {now.strftime('%H:%M %d.%m.%Y')}")
        return embed

    things = list()
    for data in all_data:
        if "дцх" in data:
            things.append(f"`ДЦХ` {data[0]} по {data[5]}-й линии")
    for data in all_data:
        if "дсцп" in data:
            things.append(f"`ДСЦП` {data[0]} по станции `{data[4]}`")
    for data in all_data:
        if "маневровый" in data:
            things.append(f"`Маневровый машинист` {data[0]} по станции `{data[4]}`")

    drivers = list(list())
    for data in all_data:
        if "машинист" in data:
            drivers.append([int(data[3]), data[0]])

    drivers = sorted(drivers, key=lambda driver: driver[0])
    print(drivers)

    for i in range(0, len(drivers)):
        things.append(f"`Машинист` {drivers[i][1]}. Номер маршрута `{drivers[i][0]}`")

    embed.description = '\n'.join([thing for thing in things])
    embed.set_footer(text=f"{ctx.guild.name} | {ctx.channel.name} | {now.strftime('%H:%M %d.%m.%Y')}")
    return embed
