import requests
import discord
from discord.ext import commands
import time

from modules.core import Bot, GeneralConnectionError
from modules.embeds import blue_embed, red_embed
from modules.players import get_player


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

    @discord.app_commands.command(
        name="ping",
        description="Check the bot's ping and the Players' Page site status."
    )
    async def ping_command(self, inter: discord.Interaction):
        await inter.response.defer()
        try:
            response = requests.get("https://www.mariokart64.com/mkworld/player.php?pid=252")
            get_player(252)
        except GeneralConnectionError:
            return await inter.edit_original_response(embed=red_embed(
                title="⚠️ Could not connect to Players' Page"
            ))
        pp_latency = round(response.elapsed.total_seconds() * 1000)
        if response.status_code == 200:
            return await inter.edit_original_response(embed=blue_embed(
                title=f"🏓 Players' Page latency: {pp_latency} ms"
            ))
        else:
            return await inter.edit_original_response(embed=red_embed(
                title=f"⚠️ Error {response.status_code}: Could not connect to Players' Page"
            ))

    @commands.command(name="sync", hidden=True)
    async def sync_command(self, ctx: commands.Context):
        if ctx.author.id == self.bot.owner_id:
            await self.bot.tree.sync()
            return await ctx.send("✅ Command tree re-synced.")


async def setup(bot: Bot):
    await bot.add_cog(AdminCog(bot))
