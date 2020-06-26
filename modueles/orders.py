import os
import discord
import datetime
import logging
from discord.ext import commands
from language.treatment_ru import *

class Orders(commands.Cog, name="Приказы рангового сервера"):
    def __init__(self, client):
        self.client = client
        self.check = True

        logger = logging.getLogger("orders")
        logger.setLevel(logging.INFO)

        self.logger = logger


    async def __send_message(self, reaction, ctx, message, embed):
        if reaction.emoji == "✅":
            await ctx.message.delete()
            await message.delete()
            embed.set_footer(text=order_check.format(ctx.author.name))
            await ctx.send(embed=embed)
            self.check = True
        elif reaction.emoji == "❌":
            await ctx.message.delete()
            with open("deleted_order.txt", "w", encoding="utf8") as file:
                file.write(ctx.message.content)

            file = open("deleted_order.txt", "rb")
            temp = discord.File(file, filename="deleted_order.txt")

            await ctx.send(file=temp)
            file.close()
            os.remove("deleted_order.txt")
            temp.close()

            await message.delete()

            self.check = True


    @commands.command(name="заступить", help="<префикс>заступить <№ приказа>")
    async def enter(self, ctx, *, number_of_order: int):
        if not self.check:
            await ctx.send(order_still_not_check.format(ctx.author.mention))
            return

        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))

        embed = discord.Embed(colour=discord.Colour.from_rgb(54, 57, 63))
        embed.set_author(name=f"Приказ №{number_of_order}")
        embed.description = f"\nДата: {now.strftime('%d.%m.%Y')}\nВремя: {now.strftime('%H:%M:%S')}\n\nПоездной диспетчер {ctx.author.mention} заступил на дежурство."
        embed.set_footer(text=order_not_check)

        message = await ctx.send(embed=embed, delete_after=60)
        await message.add_reaction("✅")
        await message.add_reaction("❌")

        self.check = False

        reaction, user = await self.client.wait_for('reaction_add', check=lambda r, u: u.id == ctx.author.id)

        await self.__send_message(reaction, ctx, message, embed)

    @commands.command(name="приказ", help="<префикс>приказ <№ приказа> <приказ>")
    async def order(self, ctx, *args):
        if not self.check:
            await ctx.send(order_still_not_check.format(ctx.author.mention))
            return

        if not args[0].isdigit():
            ctx.send(missing_parameters_orders.format(ctx.author.mention, self.client.command_prefix[0]))
            return

        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))

        embed = discord.Embed(colour=discord.Colour.from_rgb(54, 57, 63))
        embed.set_author(name=f"Приказ №{args[0]}")
        embed.description = f"\nДата: {now.strftime('%d.%m.%Y')}\nВремя: {now.strftime('%H:%M:%S')}\n\n**{' '.join(word for word in args[1:len(args)])}**\n\nПоездной диспетчер {ctx.author.mention}."
        embed.set_footer(text=order_not_check)

        message = await ctx.send(embed=embed, delete_after=60)
        await message.add_reaction("✅")
        await message.add_reaction("❌")

        self.check = False

        reaction, user = await self.client.wait_for('reaction_add', check=lambda r, u: u.id == ctx.author.id)

        await self.__send_message(reaction, ctx, message, embed)

    @commands.command(name="распоряжение", help="<префикс>распоряжение <распоряжение>")
    async def direction(self, ctx, *, direction: str):
        if not self.check:
            await ctx.send(order_still_not_check.format(ctx.author.mention))
            return

        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))

        embed = discord.Embed(colour=discord.Colour.from_rgb(54, 57, 63))
        embed.set_author(name=f"Распоряжение")
        embed.description = f"\nДата: {now.strftime('%d.%m.%Y')}\nВремя: {now.strftime('%H:%M:%S')}\n\n**{direction}**\n\nПоездной диспетчер {ctx.author.mention}."
        embed.set_footer(text=order_not_check)

        message = await ctx.send(embed=embed, delete_after=60)
        await message.add_reaction("✅")
        await message.add_reaction("❌")

        self.check = False

        reaction, user = await self.client.wait_for('reaction_add', check=lambda r, u: u.id == ctx.author.id)

        await self.__send_message(reaction, ctx, message, embed)

    @commands.command(name="сдать", help="<префикс>сдать <№ приказа>")
    async def hand_over(self, ctx, *, number_of_order: int):
        if not self.check:
            await ctx.send(order_still_not_check.format(ctx.author.mention))
            return
            
        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))

        embed = discord.Embed(colour=discord.Colour.from_rgb(54, 57, 63))
        embed.set_author(name=f"Приказ №{number_of_order}")
        embed.description = f"\nДата: {now.strftime('%d.%m.%Y')}\nВремя: {now.strftime('%H:%M:%S')}\n\nПоездной диспетчер {ctx.author.mention} сдал смену."
        embed.set_footer(text=order_not_check)

        message = await ctx.send(embed=embed, delete_after=60)
        await message.add_reaction("✅")
        await message.add_reaction("❌")

        self.check = False

        reaction, user = await self.client.wait_for('reaction_add', check=lambda r, u: u.id == ctx.author.id)

        await self.__send_message(reaction, ctx, message, embed)
