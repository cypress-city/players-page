import requests
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

    @commands.command(name="ping")
    async def ping_command(self, ctx: commands.Context):
        message = await ctx.send(
            "🏓 Discord latency: ...\n"
            "🏓 Players' Page latency: ..."
        )
        discord_latency = round((message.created_at - ctx.message.created_at).total_seconds() * 1000)
        await message.edit(
            content=f"🏓 Discord latency: {discord_latency} ms\n"
                    f"🏓 Players' Page latency: ..."
        )
        response = requests.get("https://www.mariokart64.com/mkworld/player.php?pid=252")
        pp_latency = round(response.elapsed.total_seconds() * 1000)
        if response.status_code == 200:
            await message.edit(
                content=f"🏓 Discord latency: {discord_latency} ms\n"
                        f"🏓 Players' Page latency: {pp_latency} ms"
            )
        else:
            await message.edit(
                content=f"🏓 Discord latency: {discord_latency} ms\n"
                        f"🏓 Players' Page latency: ⚠️ `Error {response.status_code}`"
            )

    @commands.command(name="sync", hidden=True)
    async def sync_command(self, ctx: commands.Context):
        if ctx.author.id == self.bot.owner_id:
            await self.bot.tree.sync()
            return await ctx.send("✅ Command tree re-synced.")


async def setup(bot: Bot):
    await bot.add_cog(AdminCog(bot))
