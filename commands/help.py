import discord
from discord.ext import commands

from modules.core import Bot
from modules.embeds import blue_embed


help_pages = {
    "General": "This is a Discord integration for the **[Mario Kart World Players' Page]"
               "(https://www.mariokart64.com/mkworld)**, a community Time Trials leaderboard.\n\n"
               "Click one of the buttons below to learn more about a particular topic:\n"
               "* **Registering:** How to sign up for the Players' Page, and how to link your account with the bot.\n"
               "* **Submitting:** How to submit records to the Players' Page.\n"
               "* **Players:** How to view and compare players' records.\n"
               "* **Leaderboards:** How to view course leaderboards.",
    "Registering": "In order to submit records via the bot, you need an **update token**: a unique identifier that "
                   "acts as a \"passkey\" for your account. The token is a [32-character string of numbers and letters]"
                   "(https://en.wikipedia.org/wiki/Universally_unique_identifier) given to you after making an account "
                   "and verifying your email.\n\n"
                   "**If you don't have an account:**\n"
                   "* [Sign up](https://www.mariokart64.com/mkworld/signup.php) on the Players' Page. Use either your "
                   "real name or a unique, recognizable handle.\n"
                   "* Check your email for a message from noreply@mariokart64.com containing a verification link.\n"
                   "* Click the verification link to receive an update token.\n\n"
                   "**If you have an account:**\n"
                   "* If you're already submitting records via the website, it's the same update token you enter at "
                   "the bottom of the submission widget.\n"
                   "* If you don't know your update token, contact Players' Page staff. Most of us are in the "
                   "[Mario Kart World Time Trials server](https://discord.gg/6gDAPxvqh7).\n\n"
                   "**After receiving your update token:**\n"
                   "* Use the command `/register` and enter your token to link your account with the bot and "
                   "start submitting records.\n\n"
                   "**After registering with the bot:**\n"
                   "* Use `/submit` to submit records. See the **Submitting** page below for more details.\n"
                   "* Use `/token view` to view the token you have registered.\n"
                   "* Use `/token set` to change your token.\n"
                   "* Use `/token delete` to remove your token from the database and unlink your account.",
    "Submitting": "The **`/submit`** command allows you to submit your records to the Players' Page. "
                  "It has two required fields and two optional fields:\n"
                  "* `course`: (required) The track you set the record on. Start typing a track's name or "
                  "abbreviation to search, then select from the list of options above the message bar.\n"
                  "* `time`: (required) The time you set on the track. Enter it exactly as you see in-game "
                  "(like `1:23.456`).\n"
                  "* `comments`: (optional) Any comments you want to leave on the run. If you want to attach "
                  "a link to a video of your run, enter it in this field.\n"
                  "* `date`: (optional) The date you set the record on. If you leave this blank, your record will be "
                  "submitted under today's date. If you want to specify an earlier date, enter it in `YYYY-MM-DD` "
                  "format (like `2025-07-30` for July 30, 2025).\n\n"
                  "**Note:** In order to use the `/submit` command, you need to link your account with the bot. "
                  "See the **Registering** page below for more details.",
    "Players": "The **`/player`** command allows you to view any player's timesheet (their full list of records), "
               "or to view their record on a specific track. It has one required field and one optional field:\n"
               "* `player`: (required) The player's display name on the Players' Page. Start typing a player's name "
               "to search, then select from the list of options above the message bar.\n"
               "* `course`: (optional) The name of the track you want to see their record on. Leave this blank to "
               "view their full timesheet.\n\n"
               "The **``/compare``** command allows you to compare any two players' timesheets. It has two "
               "required fields:\n"
               "* `player1`: (required) The display name of the first player to compare. Tracks where player 1 is "
               "faster will be marked with a 🔹 blue diamond.\n"
               "* `player2`: (required) The display name of the second player to compare. Tracks where player 2 is "
               "faster will be marked with an 🔸 orange diamond.",
    "Leaderboards": "The **``/course``** command allows you to view the global or regional leaderboards for a track. "
                    "It has one required field and two optional fields:\n"
                    "* `course`: (required) The name of the track. Start typing a track's name or abbreviation to "
                    "search, then select from the list of options above the message bar.\n"
                    "* `region`: (optional) A specific country or continent. Leave this blank to view global "
                    "leaderboards.\n"
                    "* `player`: (optional) A specific player to highlight. Use if you want to quickly see the "
                    "times surrounding a certain player on the leaderboards."
}


class HelpView(discord.ui.View):
    def __init__(self, starting_page: str = "General"):
        super().__init__(timeout=600)
        self.page = starting_page

    def copy(self):
        return HelpView(self.page)

    @discord.ui.button(label="General", style=discord.ButtonStyle.gray)
    async def general(self, inter: discord.Interaction, button: discord.ui.Button):
        await inter.response.defer()
        self.page = "General"
        self.stop()

    @discord.ui.button(label="Registering", style=discord.ButtonStyle.gray)
    async def register(self, inter: discord.Interaction, button: discord.ui.Button):
        await inter.response.defer()
        self.page = "Registering"
        self.stop()

    @discord.ui.button(label="Submitting", style=discord.ButtonStyle.gray)
    async def submit(self, inter: discord.Interaction, button: discord.ui.Button):
        await inter.response.defer()
        self.page = "Submitting"
        self.stop()

    @discord.ui.button(label="Players", style=discord.ButtonStyle.gray)
    async def players(self, inter: discord.Interaction, button: discord.ui.Button):
        await inter.response.defer()
        self.page = "Players"
        self.stop()

    @discord.ui.button(label="Leaderboards", style=discord.ButtonStyle.gray)
    async def leaderboards(self, inter: discord.Interaction, button: discord.ui.Button):
        await inter.response.defer()
        self.page = "Leaderboards"
        self.stop()


def help_embed(page: str):
    return blue_embed(title=f"ℹ️ {page}", desc=help_pages.get(page))


async def topic_autocomplete(inter: discord.Interaction, current: str) -> list[discord.app_commands.Choice[str]]:
    return [discord.app_commands.Choice(name=g, value=g) for g in help_pages.keys() if current in g.lower()][:25]


class HelpCog(commands.Cog):
    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot

    @discord.app_commands.command(
        name="help",
        description="Help with all bot functions."
    )
    @discord.app_commands.describe(topic="A particular topic you want help with.")
    @discord.app_commands.autocomplete(topic=topic_autocomplete)
    async def help_command(self, inter: discord.Interaction, topic: str = "General"):
        view = HelpView(topic)
        await inter.response.send_message(embed=help_embed(view.page), view=view, ephemeral=True)
        while not await view.wait():
            view = view.copy()
            await inter.edit_original_response(embed=help_embed(view.page), view=view)
        await inter.edit_original_response(embed=help_embed(view.page), view=None)


async def setup(bot: Bot):
    await bot.add_cog(HelpCog(bot))
