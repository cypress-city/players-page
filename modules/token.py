import discord
import re
from discord.ext import commands

from modules.bot import Bot, Confirm
from modules.embeds import red_embed, green_embed, blue_embed


class ConfirmDelete(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.value = None

    @discord.ui.button(label='Delete', style=discord.ButtonStyle.red)
    async def confirm(self, inter: discord.Interaction, button: discord.ui.Button):
        await inter.response.defer()
        self.value = True
        self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.gray)
    async def cancel(self, inter: discord.Interaction, button: discord.ui.Button):
        await inter.response.defer()
        self.value = False
        self.stop()


class TokenCog(commands.Cog):
    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot

    options = discord.app_commands.Group(name="token", description="Info about the token used to submit times.")

    @options.command(
        name="set",
        description="Register a self-submit token with the bot, so you can submit times. Other users won't see it."
    )
    @discord.app_commands.describe(token="Player's Page self-submit token")
    async def register_command(self, inter: discord.Interaction, token: str):
        token = token.strip(" \n")
        if current_token := self.bot.get_token(inter.user):
            if token == current_token:
                return await inter.response.send_message(embed=blue_embed(
                    title="🔑 This is already your current token.",
                    desc="No change was made."
                ), ephemeral=True)
            view = Confirm()
            await inter.response.send_message(embed=blue_embed(
                title="⚠️ Are you sure?",
                desc=f"You already have the following token registered with the bot:\n```\n{current_token}\n```\n"
                     f"Press **`Confirm`** to overwrite this token and set a new one. "
                     f"Press **`Cancel`** to keep your current token."
            ), view=view, ephemeral=True)
            await view.wait()
            if view.value is True:
                if not re.fullmatch(r"[0-9a-f]{32}", token):
                    await inter.edit_original_response(embed=red_embed(
                        title="⚠️ This doesn't look right.",
                        desc="Your self-submit token should be a 32-character string made up of only the digits 0-9 "
                             "and the letters a-f, in lowercase. Make sure you've got the right token and try again."
                    ), view=None)
                else:
                    self.bot.set_token(inter.user, token)
                    await inter.edit_original_response(embed=green_embed(title="✅ New token registered!"), view=None)
            else:
                await inter.edit_original_response(embed=blue_embed(
                    title="🔑 No change was made.",
                    desc="Interaction timed out." if view.value is None else None
                ), view=None)
        else:
            if not re.fullmatch(r"[0-9a-f]{32}", token):
                await inter.response.send_message(embed=red_embed(
                    title="⚠️ This doesn't look right.",
                    desc="Your self-submit token should be a 32-character string made up of only the digits 0-9 "
                         "and the letters a-f, in lowercase. "
                         "Make sure you've got the right token and try again.\n\n"
                         "If you don't know what a self-submit token is, start by [making an account]"
                         "(https://www.mariokart64.com/mkworld/signup.php) on the Players' Page."
                ), ephemeral=True)
            else:
                self.bot.set_token(inter.user, token)
                await inter.response.send_message(embed=green_embed(
                    title="✅ Token registered!",
                    desc="You can now begin submitting times with the `/submit` command."
                ), ephemeral=True)

    @options.command(
        name="view",
        description="View the token you have registered with the bot. Other users won't see it."
    )
    async def view_command(self, inter: discord.Interaction):
        if token := self.bot.get_token(inter.user):
            await inter.response.send_message(embed=blue_embed(
                title="🔑 Your token:",
                desc=f"```\n{token}\n```"
            ), ephemeral=True)
        else:
            await inter.response.send_message(embed=red_embed(
                title="⚠️ No token registered.",
                desc="Use `/token set` to register your self-submit token with the bot.\n\n"
                     "If you don't know what a self-submit token is, start by [making an account]"
                     "(https://www.mariokart64.com/mkworld/signup.php) on the Players' Page."
            ), ephemeral=True)

    @options.command(
        name="delete",
        description="Remove your token from the bot's registry."
    )
    async def delete_command(self, inter: discord.Interaction):
        if self.bot.get_token(inter.user):
            view = ConfirmDelete()
            await inter.response.send_message(embed=blue_embed(
                title="⚠️ Are you sure?",
                desc="Deleting your token will prevent you from submitting times via the bot until you set "
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
                title="⚠️ No token registered.",
                desc="Use `/token set` to register your self-submit token with the bot.\n\n"
                     "If you don't know what a self-submit token is, start by [making an account]"
                     "(https://www.mariokart64.com/mkworld/signup.php) on the Players' Page."
            ), ephemeral=True)


async def setup(bot: Bot):
    await bot.add_cog(TokenCog(bot))
