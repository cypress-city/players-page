import requests
import discord
from discord.ext import commands

from modules.core import Bot, GeneralConnectionError
from modules.embeds import blue_embed, red_embed
from modules.players import get_player


class MiscCog(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @discord.app_commands.command(
        name="links",
        description="Links to the Players' Page and related sites."
    )
    async def links_command(self, inter: discord.Interaction):
        await inter.response.send_message(embed=blue_embed(
            desc="🔗 [MKWorld Players' Page](https://www.mariokart64.com/mkworld) | "
                 "[MKWorld Time Trials Discord](https://discord.gg/6gDAPxvqh7) | "
                 "[Source code](https://github.com/cypress-city/players-page)"
        ))

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


async def setup(bot: Bot):
    await bot.add_cog(MiscCog(bot))
