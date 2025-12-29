import discord
from discord.ext import commands

from modules.core import Bot
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
            desc="This is a Discord integration for the **[Mario Kart World Players' Page]"
                 "(https://www.mariokart64.com/mkworld)**, a community Time Trials "
                 "leaderboard. If you'd like to participate, start by **[making an account]"
                 "(https://www.mariokart64.com/mkworld/signup.php)** on the Players' Page.\n\n"
                 "Once you verify your email, you'll be given an **update token**, a long string of numbers and "
                 "letters. To start submitting times via Discord, share this token with the bot using the command "
                 "`/token set`. You can later view your token using the command `/token view`. "
                 "For more info about update tokens, see `/token help`.\n\n"
                 "After registering your token, you can begin submitting times to the Players' Page using the command "
                 "`/submit`. Select a track and input your time, and the bot will automatically forward it "
                 "to the Players' Page.\n\n"
                 "View any player's timesheet using the command `/player`. "
                 "You can also compare two players' timesheets using the command `/compare`. "
                 "View the leaderboard for any course using the command `/course`."
        ), ephemeral=True)


async def setup(bot: Bot):
    await bot.add_cog(HelpCog(bot))
