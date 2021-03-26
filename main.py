# https://github.com/Quotion/ProjectKate

from discord.ext.commands import Bot
from modueles.status import Status
from modueles.main_commands import MainCommands
from modueles.ban_system import Ban
from models import *
import functions.embeds
import datetime
import discord
import logging
import logging.handlers
import json as js
import os
import sys
import io

client = Bot(command_prefix=['к!', 'К!', 'k!', 'K!'])

# client.remove_command('help')

logger = logging.getLogger("main")
logger.setLevel(logging.INFO)

log_format = "[%(asctime)s] %(levelname)s: %(filename)s(%(lineno)d) [%(funcName)s]: %(name)s: %(message)s"
formatter = logging.Formatter(log_format)

handler_file = logging.handlers.TimedRotatingFileHandler(filename="logs/kate.log", when="midnight", interval=1)
handler_file.suffix = "%d%Y%m"
handler_file.setFormatter(formatter)

handler_console = logging.StreamHandler(sys.stdout)
handler_console.setFormatter(formatter)

logger.addHandler(handler_file)
logger.addHandler(handler_console)


class Katherine(object):
    def __init__(self, client):
        self.client = client

        db.connect(reuse_if_open=True)
        db.create_tables([GmodPlayer,
                          GmodBan,
                          Rating,
                          UserDiscord,
                          RoleDiscord,
                          RoleUser,
                          Promocode,
                          StatusGMS,
                          DonateUser,
                          AllTimePlay,
                          StatisticsDriving,
                          RolesGmod,
                          NewYearPresents])

        with open("stuff/words", 'r', encoding='utf8') as file:
            self.words = file.read().split()

        self.on_ready()
        self.events()

        self.client.add_cog(MainCommands(client))
        self.client.add_cog(Status(client))
        self.client.add_cog(Ban(client))

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

            guild = self.client.get_guild(580768441279971338)
            for role in guild.roles:
                RoleDiscord.insert(role_id=role.id).on_conflict_ignore().execute()

    def events(self):
        @self.client.event
        async def on_guild_join(guild):
            logger.info('Someone added {} to guild "{}"'.format(self.client.user.name, guild.name))

        @self.client.event
        async def on_member_join(member):
            roles_higher = list() 

            UserDiscord.insert(discord_id=member.id).on_conflict_ignore().execute()
            roles = RoleUser.select(RoleUser, UserDiscord, RoleDiscord).join(RoleDiscord).switch(RoleUser) \
                .join(UserDiscord).where(UserDiscord.discord_id == member.id)

            for signature in roles:
                role = member.guild.get_role(signature.rolediscord.role_id)
                if role.name == "@everyone":
                    continue

                try:
                    await member.add_roles(role)
                except discord.Forbidden:
                    roles_higher.append(role)

            channel = discord.utils.get(self.client.get_all_channels(), name='⚡тех-записи⚡')
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
                query = RoleUser.delete().where(RoleUser.userdiscord_id == user.id)
                query.execute()
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

            channel = discord.utils.get(self.client.get_all_channels(), name='⚡тех-записи⚡')
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

            channel = discord.utils.get(self.client.get_all_channels(), name='⚡тех-записи⚡')
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

            guild_id, check, msg_delete = message.guild.id, None, None

            channel = discord.utils.get(self.client.get_all_channels(), name='⚡тех-записи⚡')
            if not channel:
                pass
            else:
                if message.content:
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
                else:
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
            if not channel_log:
                pass
            else:
                channel = self.client.get_channel(payload.channel_id)
                await channel_log.send(embed=await functions.embeds.raw_delete_message(user_info, channel,
                                                                                       payload.message_id))
                logger.info("Message was raw delete.")

        @self.client.event
        async def on_member_update(before_member, after_member):
            channel = discord.utils.get(self.client.get_all_channels(), name='⚡тех-записи⚡')
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
            guild = self.client.get_guild(payload.guild_id)
            role = guild.get_role(699898326698688542)
            if payload.message_id == 768536526207844372 and payload.emoji.name == "✅":
                await payload.member.add_roles(role)

        @self.client.event
        async def on_raw_reaction_remove(payload):
            guild = self.client.get_guild(payload.guild_id)
            member = discord.utils.get(guild.members, id=payload.user_id)
            role = guild.get_role(699898326698688542)
            if payload.message_id == 768536526207844372 and payload.emoji.name == "✅":
                await member.remove_roles(role)

        @self.client.event
        async def on_message(message):
            for role in message.author.roles:
                if role.id == 661271145089335306:
                    return
            for word in self.words:
                if word in [letters.lower() for letters in message.content.split()] and (
                        message.channel.name == "основной"
                        or message.channel.name == "бот"):
                    await message.channel.send(embed=
                                               await functions.embeds.description("Использование запрещенных слов.",
                                                                                  "Пожалуйста воздержитесь от "
                                                                                  "использования **запрещенных слов в "
                                                                                  "ваших предложениях**.\nЗапрет "
                                                                                  "распростроянется только на канал "
                                                                                  "#основной и #бот"))
                    await message.delete()

            if message.author.id == self.client.user.id:
                return
            # elif message.channel.name == "разработка-бота":
            #     await self.on_news(message)
            else:
                await self.client.process_commands(message)


Katherine(client)

with open("stuff/config.json", "r", encoding="utf8") as file:
    json = js.load(file)
    client.run(json['TOKEN'])
