import discord
import random
from discord.ext import commands, tasks


class Fun_Gif(commands.Cog, name="Фигня, которая нужна!"):

    def __init__(self, client):
        self.client = client
        self.gif_status = False
        self.gif = "https://tenor.com/view/coronavirus-covid19-covid-do-the5-do-the-five-gif-16678450"

        self.channel = 0

        self.gif_send.start()


    @commands.command(name="вкл_гиф")
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    async def gif_on(self, ctx):
        await ctx.send("пaжNлой п0тоk BключеH на гифк3")
        self.gif_status = True
        self.channel = ctx.channel.id

    @commands.command(name="выкл_гиф")
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    async def gif_off(self, ctx):
        await ctx.send("вы отключили гифки")
        self.gif_status = False
        self.channel = 0

    @commands.command(name="гиф")
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    async def gif_url(self, ctx, *, gif_url: str):
        await ctx.send("вы чо делаете, нафига вам новая гифка?")
        self.gif = gif_url

    @tasks.loop(minutes=random.randint(25, 50))
    async def gif_send(self):
        if self.gif_status:
            phrase = ["А вы помните?\n{}", "А ты сегодня {}", "Не забываем!\n{}", "Как ты мог забыть?\n{}"]
            channel = self.client.get_channel(self.channel)
            await channel.send(random.choice(phrase).format(self.gif))

    @gif_send.before_loop
    async def ready(self):
        await self.client.wait_until_ready()

    @commands.Cog.listener()
    async def on_typing(self, channel, user, when):
        if random.randint(0, 3) == 2 and self.gif_status:
            phrase = ["{} ДЕРЖУ ВКУРСЕ\n{}", "{} кто тi\n{}", "{} nravitsa mem?\n{}"]
            channel = self.client.get_channel(self.channel)
            await channel.send(random.choice(phrase).format(user.mention, self.gif))
