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
                       "\n\n\n" +
                       "Сообщение после:\n" + after.content)

        file.close()

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
    embed = discord.Embed(colour=discord.Colour.from_rgb(54, 57, 63))
    embed.set_author(name=f"Профиль игрока {kwargs['name']}", icon_url=kwargs["icon_url"])
    embed.set_thumbnail(url=kwargs["avatar_url"])
    embed.add_field(name='Дискорд:', value=kwargs["mention"])
    embed.add_field(name='Реверсивки:', value=str(all_data['revers']))
    embed.add_field(name='Золотые реверсивки:', value=str(all_data['gold_revers']))
    embed.add_field(name='Рейтинг:', value=str(all_data['rating']))
    embed.add_field(name='Ваш SteamID:', value=str(all_data['steamid']), inline=False)
    embed.add_field(name='Ник:', value=str(all_data['nick']))
    embed.add_field(name='Ранг:', value=str(all_data['rank']))
    embed.set_footer(text="{} | {} | {}".format(kwargs['name'], kwargs['guild_name'], now.strftime('%d.%m.%Y')))
    return embed


async def delete_message(message):
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
    embed = discord.Embed(colour=discord.Colour.from_rgb(54, 57, 63))
    embed.set_author(name=f"В {now.strftime('%H:%M')} на сервере {message.guild.name} было удаленно сообщение, "
                          f"отправленное {message.author.name}.",
                     icon_url=message.guild.icon_url)
    embed.add_field(name='Текст сообщения:',
                    value=message.content,
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
                    value=f'**Текст сообщения:**`{message.content}`'
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
    embed.set_author(name=f"Сегодня ваш выигрышь составляет {win} {thing} ")
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
    embed.set_author(name="Информация по серверу {0.name}".format(guild))
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


async def bank_info(ctx, all_amount_off_money):
    embed = discord.Embed(colour=discord.Colour.from_rgb(54, 57, 63))
    embed.set_author(name="Информация по Тратбанку")
    embed.add_field(name="Директор банка: ", value=ctx.guild.owner.mention)
    embed.add_field(name="Нынешнее состояние: ", value=f"{all_amount_off_money}₽")
    embed.add_field(name="Курс: ", value="0")
    embed.set_footer(text=f"")
