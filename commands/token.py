import discord
import re
import uuid
from discord.ext import commands

from modules.core import Bot
from modules.embeds import red_embed, green_embed, blue_embed
from modules.views import Confirm, ConfirmDelete


class TokenCog(commands.Cog):
    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot

    options = discord.app_commands.Group(name="token", description="Info about the token used to submit records.")

    async def set_token(self, inter: discord.Interaction, token: str):
        if not re.fullmatch(r"[0-9a-f]{32}", token):
            return await inter.response.send_message(embed=red_embed(
                title="⚠️ This doesn't look right.",
                desc="Your update token should be a 32-character string made up of only the digits 0-9 "
                     "and the letters a-f, in lowercase. "
                     "Make sure you've got the right token and try again.\n\n"
                     "If you don't know what an update token is, check `/help Registering`."
            ), ephemeral=True)
        if current_token := self.bot.get_token(inter.user):
            if token == current_token:
                return await inter.response.send_message(embed=blue_embed(
                    title="🔑 This is already your current token.",
                    desc="No change was made."
                ), ephemeral=True)
            view = Confirm(inter.user)
            await inter.response.send_message(embed=blue_embed(
                title="⚠️ Are you sure?",
                desc=f"You already have an update token registered with the bot.\n"
                     f"Press **Confirm** to change to the new token:\n```{token}```"
                     f"Press **Cancel** to keep your current token:\n```{current_token}```"
            ), view=view, ephemeral=True)
            await view.wait()
            if view.value is True:
                self.bot.set_token(inter.user, token)
                await inter.edit_original_response(embed=green_embed(
                    title="✅ New update token registered!",
                    desc="You can continue using `/submit` as usual."
                ), view=None)
            else:
                await inter.edit_original_response(embed=blue_embed(
                    title="🔑 No change was made.",
                    desc="Interaction timed out." if view.value is None else None
                ), view=None)
        else:
            self.bot.set_token(inter.user, token)
            await inter.response.send_message(embed=green_embed(
                title="✅ Update token registered!",
                desc="You can now begin submitting records with the `/submit` command."
            ), ephemeral=True)

    @options.command(
        name="set",
        description="Register or change your update token."
    )
    @discord.app_commands.describe(token="Player's Page update token")
    async def set_command(self, inter: discord.Interaction, token: str):
        await self.set_token(inter, token.strip(" \n`"))

    @options.command(
        name="view",
        description="View the update token you have registered with the bot. Other users won't see it."
    )
    async def view_command(self, inter: discord.Interaction):
        if token := self.bot.get_token(inter.user):
            await inter.response.send_message(embed=blue_embed(
                title="🔑 Your update token:",
                desc=f"```\n{token}\n```"
            ), ephemeral=True)
        else:
            await inter.response.send_message(embed=red_embed(
                title="⚠️ No update token registered.",
                desc="Use `/register` to register your update token with the bot.\n\n"
                     "If you don't know what an update token is, check `/help Registering`."
            ), ephemeral=True)

    @options.command(
        name="delete",
        description="Remove your update token from the bot's registry."
    )
    async def delete_command(self, inter: discord.Interaction):
        if self.bot.get_token(inter.user):
            view = ConfirmDelete(inter.user)
            await inter.response.send_message(embed=blue_embed(
                title="⚠️ Are you sure?",
                desc="Deleting your update token will prevent you from submitting records via the bot until you set "
                     "another token. Press **`Delete`** to continue."
            ), view=view, ephemeral=True)
            await view.wait()
            if view.value is True:
                self.bot.remove_token(inter.user)
                await inter.edit_original_response(embed=green_embed(title="✅ Token deleted."), view=None)
            else:
                await inter.edit_original_response(embed=blue_embed(title="🔑 Token was not deleted."), view=None)
        else:
            await inter.response.send_message(embed=red_embed(
                title="⚠️ No update token registered.",
                desc="Use `/register` to register your update token with the bot.\n\n"
                     "If you don't know what an update token is, check `/help Registering`."
            ), ephemeral=True)

    @discord.app_commands.command(
        name="register",
        description="Register an update token with the bot, so you can submit records. Other users won't see it."
    )
    async def standalone_register_command(self, inter: discord.Interaction, token: str):
        await self.set_token(inter, token.strip(" \n`"))


async def setup(bot: Bot):
    await bot.add_cog(TokenCog(bot))
