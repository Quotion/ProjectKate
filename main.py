# https://github.com/Quotion/ProjectKate

from discord.ext.commands import Bot
from modueles.status import Status
from modueles.main_commands import MainCommands
from modueles.ban_system import Ban
from modueles.rprequest import RPrequest
from modueles.orders import Orders
from models import *
import functions.embeds
import datetime
import discord
import logging
import os
import io

client = Bot(command_prefix=['к!', 'К!', 'k!', 'K!'])

logging.basicConfig(format="%(levelname)s: %(funcName)s (%(lineno)d): %(name)s: %(message)s",
                    level=logging.INFO)
logger = logging.getLogger("main")
logger.setLevel(logging.INFO)


class Katherine(object):
    def __init__(self, client):
        self.client = client

        db.connect(reuse_if_open=True)
        db.create_tables([GmodPlayer,
                          GmodBan,
                          UserDiscord,
                          RoleDiscord,
                          RoleUser,
                          BanRole,
                          Promocode,
                          StatusGMS,
                          DonateUser,
                          DriveStatistic,
                          RolesGmod])

        with open("stuff/words", 'r', encoding='utf8') as file:
            self.words = file.read().split()

        self.on_ready()
        self.events()

        self.client.add_cog(MainCommands(client))
        self.client.add_cog(Status(client))
        self.client.add_cog(Ban(client))
        self.client.add_cog(Orders(client))

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
            roles = RoleUser \
                .select(RoleUser, UserDiscord, RoleDiscord) \
                .join(RoleDiscord).switch(RoleUser) \
                .join(UserDiscord)

            for signature in roles:
                print(signature.rolediscord.role_id)
                role = member.guild.get_role(signature.rolediscord.role_id)
                if role.name == "@everyone":
                    continue

                try:
                    await member.add_roles(role)
                except discord.Forbidden:
                    roles_higher.append(role)

            channel = discord.utils.get(self.client.get_all_channels(), name='око')
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

        @self.client.event
        async def on_member_remove(member):
            if member.id == self.client.user.id:
                return

            for role in member.roles:
                if role.name == "@everyone":
                    continue

                user = UserDiscord.get(UserDiscord.discord_id == member.id)
                role = RoleDiscord.get(RoleDiscord.role_id == role.id)
                try:
                    user.user_role.add(role)
                except peewee.PeeweeException:
                    pass

            channel = discord.utils.get(self.client.get_all_channels(), name='око')
            if not channel:
                pass
            else:
                await channel.send(embed=await functions.embeds.member_exit(member))
                logger.info("Member remove from guild ({})".format(member.guild.name))

        @self.client.event
        async def on_message_edit(msg_before, msg_after):
            if msg_after.content == msg_before.content or msg_before.author.id == self.client.user.id:
                return

            channel = discord.utils.get(self.client.get_all_channels(), name='око')
            if not channel:
                pass
            else:
                embed = await functions.embeds.message_edit(msg_before, msg_after)

                try:
                    plot = io.open("changelog.txt", "rb")
                except FileNotFoundError:
                    await channel.send(embed=embed)
                except Exception as error:
                    logging.error(error)
                else:
                    msg_changes = discord.File(plot, filename="Message_changes.txt")
                    await channel.send(embed=embed, file=msg_changes)
                    plot.close()
                    os.remove("changelog.txt")
                    msg_changes.close()

        @self.client.event
        async def on_message_delete(message):
            if message.author.id == self.client.user.id:
                return

            guild_id, check, msg_delete = message.guild.id, None, None

            channel = discord.utils.get(self.client.get_all_channels(), name='око')
            if not channel:
                pass
            else:
                if message.content:
                    if len(message.content) > 50:
                        content = message.content[0:40] + "..."
                        check = True

                    if check:
                        try:
                            with io.open("changelogdeleted.txt", "w", encoding='utf8') as file:
                                file.write("Удаленное сообщение:\n" + message.content)

                            file = io.open("changelogdeleted.txt", "rb")
                            msg_delete = discord.File(file, filename="Message_deleted.txt")

                            await channel.send(embed=await functions.embeds.delete_message(message, content),
                                               file=msg_delete)

                            file.close()
                            msg_delete.close()
                            os.remove("changelogdeleted.txt")
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

            channel_log = discord.utils.get(self.client.get_all_channels(), name='око')
            if not channel_log:
                pass
            else:
                channel = self.client.get_channel(payload.channel_id)
                await channel_log.send(embed=await functions.embeds.raw_delete_message(user_info, channel,
                                                                                       payload.message_id))
                logger.info("Message was raw delete.")

        @self.client.event
        async def on_member_update(before_member, after_member):
            channel = discord.utils.get(self.client.get_all_channels(), name='око')
            now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))

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
        async def on_message(message):
            for role in message.author.roles:
                if role.id == 661271145089335306:
                    return
            for word in self.words:
                if word in message.content.split():
                    await message.channel.send(embed=
                                               await functions.embeds.description("Использование запрещенных слов.",
                                                                                  "Пожалуйста воздержитесь от "
                                                                                  "использования **запрещенных слов в "
                                                                                  "ваших предложениях**.\nЗапрет "
                                                                                  "распростроянется только на канал "
                                                                                  "#основной"))
                    await message.delete()

            if message.author.id == self.client.user.id:
                return
            else:
                await self.client.process_commands(message)


Katherine(client)

with open("TOKEN", "r", encoding="utf8") as file:
    client.run(file.read().splitlines()[0])
