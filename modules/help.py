import discord
from discord.ext import commands

from modules.bot import Bot
from modules.embeds import blue_embed


class HelpCog(commands.Cog):
    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot

    @discord.app_commands.command(
        name="help",
        description="Help with all bot functions."
    )
    async def help_command(self, inter: discord.Interaction):
        await inter.response.send_message(embed=blue_embed(
            title="ℹ️ Help",
            desc="If you haven't made one already, start by **[making an account]"
                 "(https://www.mariokart64.com/mkworld/signup.php)** on the Player's Page.\n\n"
                 "Once you do, you'll be given a \"self-submit token\", a long string of numbers and letters. "
                 "To start submitting times via Discord, share this token with the bot using the command "
                 "`/token set`. You can later view your token using the command `/token view`. "
                 "Other users will never see your token.\n\n"
                 "After registering your token, you can begin submitting times to the Player's Page using the command "
                 "`/submit`. Select a track and input your time, and the bot will automatically forward it "
                 "to the Player's Page."
        ))


async def setup(bot: Bot):
    await bot.add_cog(HelpCog(bot))
