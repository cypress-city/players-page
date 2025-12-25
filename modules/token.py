import discord
import re
import uuid
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

    options = discord.app_commands.Group(name="token", description="Info about the token used to submit records.")

    @options.command(
        name="help",
        description="Help with update tokens."
    )
    async def help_command(self, inter: discord.Interaction):
        return await inter.response.send_message(embed=blue_embed(
            title="ℹ️ Update Tokens",
            desc="In order to submit a record directly to the Players' Page, you need an **update token:** a "
                 "unique identifier that acts as a \"passkey\" for your account. It's given to you after you "
                 "[make an account](https://www.mariokart64.com/mkworld/signup.php) on the Players' Page and verify "
                 "your email. After verifying, **don't close the tab** - this webpage contains your token. "
                 f"It'll look something like this:\n```\n{str(uuid.uuid4()).replace('-', '')}\n```\n"
                 "-# (There's about a [1 in 340,282,366,920,938,463,463,374,607,431,768,211,456 chance]"
                 "(https://en.wikipedia.org/wiki/Universally_unique_identifier) that's your token, by the way.)\n\n"
                 "To submit your records over Discord, you need to **share this token with the bot.**\n"
                 "- If you're already using the site to submit records, it's the same token you enter into "
                 "the \"update token\" box.\n"
                 "- If you've made an account, but don't know your update token, contact cypress (@1.c4) or another "
                 "member of Players' Page staff, and they can return it to you. There are several of us in the "
                 "[Mario Kart World Time Trials server](https://discord.gg/6gDAPxvqh7).\n"
                 "- If you don't have an account, [sign up](https://www.mariokart64.com/mkworld/signup.php) and "
                 "write down your token somewhere after verifying your email.\n\n"
                 "Once you know this token, register it with the bot using the command `/token set`. The bot will "
                 "save your token to your Discord account, and you can begin submitting through the bot directly "
                 "to the Players' Page using the command `/submit`."
        ), ephemeral=True)

    @options.command(
        name="set",
        description="Register an update token with the bot, so you can submit records. Other users won't see it."
    )
    @discord.app_commands.describe(token="Player's Page update token")
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
                desc=f"You already have the following update token registered with the bot:\n```{current_token}```\n"
                     f"Press **`Confirm`** to overwrite this token and set a new one. "
                     f"Press **`Cancel`** to keep your current token."
            ), view=view, ephemeral=True)
            await view.wait()
            if view.value is True:
                if not re.fullmatch(r"[0-9a-f]{32}", token):
                    await inter.edit_original_response(embed=red_embed(
                        title="⚠️ This doesn't look right.",
                        desc="Your update token should be a 32-character string made up of only the digits 0-9 "
                             "and the letters a-f, in lowercase. Make sure you've got the right token and try again."
                    ), view=None)
                else:
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
            if not re.fullmatch(r"[0-9a-f]{32}", token):
                await inter.response.send_message(embed=red_embed(
                    title="⚠️ This doesn't look right.",
                    desc="Your update token should be a 32-character string made up of only the digits 0-9 "
                         "and the letters a-f, in lowercase. "
                         "Make sure you've got the right token and try again.\n\n"
                         "If you don't know what an update token is, check `/token help`."
                ), ephemeral=True)
            else:
                self.bot.set_token(inter.user, token)
                await inter.response.send_message(embed=green_embed(
                    title="✅ Update token registered!",
                    desc="You can now begin submitting records with the `/submit` command."
                ), ephemeral=True)

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
                desc="Use `/token set` to register your update token with the bot.\n\n"
                     "If you don't know what an update token is, check `/token help`."
            ), ephemeral=True)

    @options.command(
        name="delete",
        description="Remove your update token from the bot's registry."
    )
    async def delete_command(self, inter: discord.Interaction):
        if self.bot.get_token(inter.user):
            view = ConfirmDelete()
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
                desc="Use `/token set` to register your update token with the bot.\n\n"
                     "If you don't know what an update token is, check `/token help`."
            ), ephemeral=True)


async def setup(bot: Bot):
    await bot.add_cog(TokenCog(bot))
