# https://github.com/Quotion/ProjectKate

from discord.ext.commands import Bot
from modueles.status import Status
from modueles.main_commands import MainCommands
from modueles.ban_system import Ban
from modueles.advert import Advert
from models import *
from discord_slash import SlashCommand
import functions.embeds
import requests
import datetime
import discord
import logging
import logging.handlers
import json as js
import os
import sys
import io

intents = discord.Intents.all()

client = Bot(command_prefix=['к!', 'К!', 'k!', 'K!'], intents=intents)
slash = SlashCommand(client, sync_commands=True, sync_on_cog_reload=True, override_type=True)

logger = logging.getLogger("main")
logger.setLevel(logging.INFO)

log_format = "[%(asctime)s] %(levelname)s: %(filename)s(%(lineno)d) [%(funcName)s]: %(name)s: %(message)s"
formatter = logging.Formatter(log_format)

handlers = logging.StreamHandler(sys.stdout)

handlers.setFormatter(formatter)

logger.addHandler(handlers)


class Katherine(object):
    def __init__(self, client):
        self.client = client

        db.connect(reuse_if_open=True)
        db.create_tables([GuildDiscord,
                          GmodPlayer,
                          GmodBan,
                          Rating,
                          UserDiscord,
                          RoleDiscord,
                          RoleUser,
                          Promocode,
                          StatusGMS,
                          DonateUser,
                          Group,
                          PlayerGroupTime,
                          NewYearPresents])

        with open("stuff/words", 'r', encoding='utf8') as file:
            self.words = file.read().split()

        with open('stuff/config.json', 'r', encoding='utf8') as config:
            json = js.load(config)
            self.join_role = json["madadev"]["join_role"]

        self.on_ready()
        self.events()

        self.client.add_cog(Status(client))
        self.client.add_cog(Ban(client))
        self.client.add_cog(Advert(client))
        self.client.load_extension("modueles.main_commands")

    @staticmethod
    async def on_news(message):
        embed = await functions.embeds.news(message)
        if message.mention_everyone:
            await message.channel.send(allowed_mentions=message.mentions[0],
                                       embed=embed)
        else:
            await message.channel.send(embed=embed)

    def on_ready(self):
        @self.client.event
        async def on_connect():
            logger.info('Bot {} ready on 50%.'.format(self.client.user.name))

        @self.client.event
        async def on_ready():
            logger.info('Bot {} now loaded for 100%.'.format(self.client.user.name))
            await self.client.change_presence(
                activity=discord.Game(name="{}help".format(self.client.command_prefix[0])))

            guilds = GuildDiscord.select(GuildDiscord.guild_id, GuildDiscord.guild)
            for guild_discord in guilds:
                guild = self.client.get_guild(guild_discord.guild)
                for role in guild.roles:
                    RoleDiscord.insert(role_id=role.id, guild_id=guild_discord.guild_id).on_conflict_ignore().execute()

    def events(self):
        @self.client.event
        async def on_guild_join(guild):
            GuildDiscord.insert(guild=guild.id).on_conflict_ignore().execute()
            logger.info('Someone added {} to guild "{}"'.format(self.client.user.name, guild.name))

        @self.client.event
        async def on_member_join(member):
            roles_higher = list()

            UserDiscord.insert(discord_id=member.id).on_conflict_ignore().execute()
            query = RoleUser \
                .select(RoleUser, UserDiscord, RoleDiscord) \
                .join(RoleDiscord) \
                .switch(RoleUser) \
                .join(UserDiscord) \
                .where(UserDiscord.discord_id == member.id)

            if not query.exists():
                join_role = member.guild.get_role(876374958190755850)
                await member.add_roles(join_role)

            for signature in query:
                role = member.guild.get_role(signature.rolediscord.role_id)
                if role.name == "@everyone":
                    continue
                try:
                    await member.add_roles(role)
                except discord.Forbidden:
                    roles_higher.append(role)

            guild_discord = GuildDiscord.select(GuildDiscord.tech_channel).where(
                GuildDiscord.guild == member.guild.id).get()
            channel = await self.client.fetch_channel(guild_discord.tech_channel)

            if not channel:
                pass
            else:
                await channel.send(embed=await functions.embeds.member_join(member))

                if len(roles_higher) == 0:
                    return

                embed = discord.Embed(colour=discord.Colour.red())
                if len(roles_higher) == 1:
                    embed.set_author(name="Недостаточно прав. Выдаваемая роль стоит выше, чем роль бота.")
                    embed.description = "Роль `{}` не может быть выдана `{}` " \
                                        "из-за недостатка прав.".format(roles_higher[0].name, member.name)
                else:
                    embed.set_author(name="Недостаточно прав. Выдаваемые роли стоят выше, чем роль бота.")
                    embed.description = "Роли `{}` не могут быть выданы `{}` " \
                                        "из-за недостатка прав.".format(', '.join(role.name for role in roles_higher),
                                                                        member.name)

                await channel.send(embed=embed)
                logger.info(f"{member.name} enter in {member.guild.name}")

        @self.client.event
        async def on_member_remove(member):
            if member.id == self.client.user.id:
                return

            user = UserDiscord.get(UserDiscord.discord_id == member.id)

            try:
                RoleUser.delete().where(RoleUser.userdiscord_id == user.id).execute()
            except peewee.DoesNotExist:
                pass

            for role in member.roles:
                if role.name == "@everyone":
                    continue

                role = RoleDiscord.get(RoleDiscord.role_id == role.id)

                try:
                    user.user_role.add(role)
                except peewee.PeeweeException as error:
                    logger.error(error)

            guild_discord = GuildDiscord.select(GuildDiscord.tech_channel).where(
                GuildDiscord.guild == member.guild.id).get()
            channel = await self.client.fetch_channel(guild_discord.tech_channel)

            if not channel:
                pass
            else:
                await channel.send(embed=await functions.embeds.member_exit(member))
                logger.info("Member remove from guild ({})".format(member.guild.name))

        @self.client.event
        async def on_message_edit(msg_before, msg_after):
            if msg_after.content == msg_before.content or msg_before.author.id == self.client.user.id:
                return

            for word in self.words:
                if word in [letters.lower() for letters in msg_after.content.split()] and (
                        msg_after.channel.name == "основной"
                        or msg_after.channel.name == "бот"):
                    await msg_after.channel.send(embed=
                                                 await functions.embeds.description("Использование запрещенных слов.",
                                                                                    "Пожалуйста воздержитесь от "
                                                                                    "использования **запрещенных слов в"
                                                                                    " ваших предложениях**.\nЗапрет "
                                                                                    "распростроянется только на канал "
                                                                                    "#основной и #бот"))
                    await msg_after.delete()

            guild_discord = GuildDiscord.select(GuildDiscord.tech_channel).where(
                GuildDiscord.guild == msg_before.guild.id).get()
            channel = await self.client.fetch_channel(guild_discord.tech_channel)

            if not channel:
                pass
            else:
                embed = await functions.embeds.message_edit(msg_before, msg_after)

                try:
                    plot = io.open("stuff/changelog.txt", "rb")
                except FileNotFoundError:
                    await channel.send(embed=embed)
                except Exception as error:
                    logging.error(error)
                else:
                    msg_changes = discord.File(plot, filename="Message_changes.txt")
                    await channel.send(embed=embed, file=msg_changes)
                    plot.close()
                    os.remove("stuff/changelog.txt")
                    msg_changes.close()

        @self.client.event
        async def on_message_delete(message):
            if message.author.id == self.client.user.id:
                return

            check, msg_delete = None, None

            guild_discord = GuildDiscord.select(GuildDiscord.tech_channel).where(
                GuildDiscord.guild == message.guild.id).get()
            channel = await self.client.fetch_channel(guild_discord.tech_channel)

            if channel and message.content:
                if len(message.content) > 50:
                    content = message.content[0:40] + "..."
                    check = True

                if check:
                    try:
                        with io.open("stuff/changelogdeleted.txt", "w", encoding='utf8') as file:
                            file.write("Удаленное сообщение:\n" + message.content)

                        file = io.open("stuff/changelogdeleted.txt", "rb")
                        msg_delete = discord.File(file, filename="Message_deleted.txt")

                        await channel.send(embed=await functions.embeds.delete_message(message, content),
                                           file=msg_delete)

                        file.close()
                        msg_delete.close()
                        os.remove("stuff/changelogdeleted.txt")
                    except Exception as error:
                        logging.error(error)
                else:
                    await channel.send(embed=await functions.embeds.delete_message(message, message.content))
            elif channel and not message.content:
                await channel.send(embed=await functions.embeds.delete_message(message, "`Пустое сообщение`"))

        @self.client.event
        async def on_raw_message_delete(payload):
            user_info = None
            if payload.cached_message:
                logger.info("Message was delete in cache.")
                return

            guild_id = payload.guild_id

            guild = self.client.get_guild(guild_id)
            try:
                audit_logs = await guild.audit_logs(limit=1).flatten()
                user_info = [info.user for info in audit_logs]
            except AttributeError as error:
                logger.error(error)

            channel_log = discord.utils.get(self.client.get_all_channels(), name='⚡тех-записи⚡')
            if channel_log:
                channel = self.client.get_channel(payload.channel_id)
                await channel_log.send(embed=await functions.embeds.raw_delete_message(user_info, channel,
                                                                                       payload.message_id))
                logger.info("Message was raw delete.")

        @self.client.event
        async def on_member_update(before_member, after_member):
            try:
                guild_discord = GuildDiscord.select(GuildDiscord.tech_channel).where(
                    GuildDiscord.guild == after_member.guild.id).get()
                channel = await self.client.fetch_channel(guild_discord.tech_channel)
            except peewee.DoesNotExist:
                return
            except Exception as error:
                logger.error(error)

            now = datetime.datetime.now()

            if before_member.roles != after_member.roles:
                embed = discord.Embed(colour=discord.Colour.from_rgb(54, 57, 63))
                embed.set_author(name="Роли пользователя {0.name} были изменины.".format(before_member))
                embed.add_field(name="Роли до:",
                                value=' '.join([role.mention for role in before_member.roles]),
                                inline=False)
                embed.add_field(name="Роли после:",
                                value=' '.join([role.mention for role in after_member.roles]),
                                inline=False)
                embed.set_footer(text=f"{before_member.name} | {before_member.guild.name} | {now.strftime('%d.%m.%Y')}")
                embed.set_thumbnail(url=before_member.avatar_url)
                await channel.send(embed=embed)

        @self.client.event
        async def on_raw_reaction_add(payload):
            if payload.member.id == self.client.user.id:
                return

            guild = self.client.get_guild(payload.guild_id)
            role = guild.get_role(699898326698688542)

            if payload.message_id == 768536526207844372 and payload.emoji.name == "✅":
                await payload.member.add_roles(role)

            with open("stuff/config.json", "r", encoding="utf8") as file:
                json = js.load(file)

                request_channel = guild.get_channel(json["madadev"]["request_channel"])
                channel = guild.get_channel(json["madadev"]["advert_channel"])
                message = await channel.fetch_message(json["madadev"]["message_advert"])

                if payload.message_id != json["madadev"]["message_advert"] or \
                        (not payload.member.permissions_in(request_channel).manage_channels and \
                         not payload.member.permissions_in(request_channel).administrator):
                    await message.remove_reaction(payload.emoji, payload.member)
                    return

                role_access = guild.get_role(json["madadev"]["join_role"])
                embed = discord.Embed()
                embed.timestamp = datetime.datetime.now() + datetime.timedelta(hours=3)

                if payload.emoji.name == json["madadev"]["reactions"]["open"]:

                    embed.colour = discord.Colour.dark_green()
                    embed.description = f"Заявки на [{json['madadev']['info']['name']} Мультиплеер]({message.jump_url})" \
                                        f" {json['madadev']['info']['date']} объявляются `ОТКРЫТЫМИ`!"

                    await request_channel.set_permissions(role_access, send_messages=True)

                if payload.emoji.name == json["madadev"]["reactions"]["close"]:
                    embed.colour = discord.Colour.red()
                    embed.description = f"Заявки на {json['madadev']['info']['name']} Мультиплеер " \
                                        f"{json['madadev']['info']['date']} объявляются `ЗАКРЫТЫМИ`!"

                    await request_channel.set_permissions(role_access, send_messages=False)

                if payload.emoji.name == json["madadev"]["reactions"]["finish"]:
                    embed.colour = discord.Colour.dark_red()
                    embed.description = f"{json['madadev']['info']['name']} Мультиплеер " \
                                        f"{json['madadev']['info']['date']} `ЗАВЕРШЕН`!"

                await request_channel.send(content=None, embed=embed)
                await message.remove_reaction(payload.emoji, payload.member)

        @self.client.event
        async def on_raw_reaction_remove(payload):
            if payload.user_id == self.client.user.id:
                return

            guild = self.client.get_guild(payload.guild_id)
            member = await guild.fetch_member(payload.user_id)
            role = guild.get_role(699898326698688542)
            if payload.message_id == 768536526207844372 and payload.emoji.name == "✅":
                await member.remove_roles(role)

        @self.client.event
        async def on_message(message):
            # for role in message.author.roles:
            #     if role.id == 661271145089335306:
            #         return
            # for word in self.words:
            #     if word in [letters.lower() for letters in message.content.split()] and (
            #             message.channel.name == "основной"
            #             or message.channel.name == "бот"):
            #         await message.channel.send(embed=
            #                                    await functions.embeds.description("Использование запрещенных слов.",
            #                                                                       "Пожалуйста воздержитесь от "
            #                                                                       "использования **запрещенных слов в "
            #                                                                       "ваших предложениях**.\nЗапрет "
            #                                                                       "распростроянется только на канал "
            #                                                                       "#основной и #бот"))
            #         await message.delete()

            if message.author.id == self.client.user.id:
                return
            else:
                await self.client.process_commands(message)

    # async def tables(self, message):
    #     def error_message(error):
    #         return f'Что-то пошло не так!' \
    #                f'\nОшибка: `{error}`' \
    #                f'\nПример как должена выглядить заявка:' \
    #                f'\nhttps://discord.com/channels/569627056707600389/863493204032618526/868803928379260938'

    #     with open('stuff/config.json', 'r', encoding='utf8') as file:
    #         config = js.load(file)
    #         api_key = config['gorails']['forum_api_key']
    #         roles_id = config['gorails']['roles_id']

    #     for role in message.author.roles:
    #         if role.id in list(map(int, roles_id.values())):
    #             print(True)
    #         print(role.id)

    #     if len(message.content.split()) < 7 or len(message.content.split()) > 9:
    #         await message.author.send(error_message('Провертье коррекность введеного вами сообщения'))
    #         return

    #     nick = message.content.split()[1]
    #     table_number = message.content.split()[3]
    #     column_number = message.content.split()[5]
    #     group = message.content.split()[7]

    #     request = requests.get('https://forum.gorails.org/api/core/members', params=dict(key=api_key, name=nick))

    #     result = request.json()['results']

    #     if result == []:
    #         await message.author.send(error_message('Ник, введеный вами, не соответсвует ни одному нику на форуме.'))
    #         return

    #     if result[0]['customFields']['2']['fields']['6']['value'] != str(table_number) and \
    #        result[0]['customFields']['2']['fields']['3']['value'] != str(table_number):
    #         await message.author.send(error_message('Табельный номер, указанный вами, не соответствует вашему табельному номеру на форуме.'))
    #         return

    #     if result[0]['customFields']['2']['fields']['9']['value'] != str(column_number):
    #         await message.author.send(error_message('Колонна, указанная вами, не соответствует колонне, указанной на форуме.'))
    #         return

    #     if group.lower() != 'тчмп' and group.lower() != 'тчм-3' and group.lower() != 'тчм-2' and group.lower() != 'тчм-1' and \
    #        group.lower() != 'дсп' and  group.lower() != 'дспц' and  group.lower() != 'днц':
    #         await message.author.send(error_message('Пожалуйста, укажите ваши погоны иным образом (пример: ТЧМИ/ДНЦ/ДСП/ТЧМ-2 и т.д.).'))
    #         return

    #     if group.upper() not in result[0]['customFields']['2']['fields']['2']['value'] and \
    #        group.upper() not in result[0]['customFields']['2']['fields']['5']['value']:
    #         await message.author.send(error_message('Погоны, введенные вами, не соответсвуют тем, что выданы вам на форуме.'))
    #         return

    #     column_role = discord.utils.get(message.guild.roles, id=roles_id[str(column_number)])
    #     user_role = discord.utils.get(message.guild.roles, id=roles_id['project_user'])

    #     await message.author.add_roles(column_role, user_role)


Katherine(client)

with open("stuff/config.json", "r", encoding="utf8") as file:
    json = js.load(file)
    client.run(json['TOKEN'])
