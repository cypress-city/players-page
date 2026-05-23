import discord
from discord.ext import commands

from modules.core import Bot


class AdminCog(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(name="about", hidden=True)
    async def about_command(self, ctx: commands.Context):
        if ctx.author.id == self.bot.owner_id:
            await ctx.send(f"🏠 Servers: {len(self.bot.guilds)} | 👤 Registered users: {len(self.bot.tokens)}")

    @commands.command(name="close", aliases=["stop"], hidden=True)
    async def close_command(self, ctx: commands.Context):
        if ctx.author.id == self.bot.owner_id:
            await ctx.send("😴 Stopping bot.")
            await self.bot.close()

    @commands.command(name="sync", hidden=True)
    async def sync_command(self, ctx: commands.Context):
        if ctx.author.id == self.bot.owner_id:
            await self.bot.tree.sync()
            await ctx.send("✅ Command tree re-synced.")

    @commands.command(name="export", hidden=True)
    async def export_command(self, ctx: commands.Context):
        if ctx.author.id == self.bot.owner_id:
            with open("data/tokens.json", "r") as fp:
                await ctx.send(file=discord.File(fp))


async def setup(bot: Bot):
    await bot.add_cog(AdminCog(bot))
