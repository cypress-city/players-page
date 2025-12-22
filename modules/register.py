import discord
import re
from discord.ext import commands

from modules.bot import Bot
from modules.embeds import red_embed, green_embed, blue_embed


class RegisterCog(commands.Cog):
    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot

    @discord.app_commands.command(
        name="register",
        description="Register a self-submit token with the bot, so you can use it to submit times to the Player's Page."
    )
    @discord.app_commands.describe(token="Player's Page self-submit token")
    async def register_command(self, inter: discord.Interaction, token: str = None):
        if not token:
            await inter.response.send_message(embed=blue_embed(
                title="Registering",
                desc="First, [make an account](https://www.mariokart64.com/mkworld/signup.php) on the Player's Page."
                     "\n\nAfter signing up, you'll receive a self-submit token: a long string of numbers and letters. "
                     "Run this command again and include the token in your message to register your account with the "
                     "bot and start submitting times. (Other users won't see your token.)"
            ))
        else:
            if not re.fullmatch(r"[0-9a-f]{32}", token):
                await inter.response.send_message(embed=red_embed(
                    title="⚠️ This doesn't look right.",
                    desc="Your self-submit token should be a 32-character string made up of only the digits 0-9 "
                         "and the letters a-f, in lowercase. "
                         "Make sure you've got the right token and try again. If you don't know what a "
                         "self-submit token is, start by [making an account]"
                         "(https://www.mariokart64.com/mkworld/signup.php) on the Player's Page."
                ), ephemeral=True)
            else:
                self.bot.add_token(inter.user, token)
                await inter.response.send_message(embed=green_embed(
                    title="✅ Token registered!",
                    desc="You can now begin submitting times with the `/submit` command."
                ), ephemeral=True)


async def setup(bot: Bot):
    await bot.add_cog(RegisterCog(bot))
