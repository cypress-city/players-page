import discord
from discord.ext import commands

from modules.core import rank_emoji, prettify_time, GeneralConnectionError
from modules.courses import courses, course_autocomplete
from modules.embeds import could_not_connect
from modules.players import player_autocomplete, get_player, players
from modules.views import TimesheetSorter


class PlayerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(
        name="player",
        description="View a player's timesheet, or check their record on a specific course."
    )
    @discord.app_commands.autocomplete(player=player_autocomplete, course=course_autocomplete)
    @discord.app_commands.describe(player="Player name", course="Track name")
    async def player_command(self, inter: discord.Interaction, player: int, course: int = -1):
        try:
            player = get_player(player)
            timesheet = player.timesheet()
        except GeneralConnectionError:
            return await inter.response.send_message(embed=could_not_connect, ephemeral=True)

        if course != -1:
            if not timesheet.get(course):
                return await inter.response.send_message(embed=player.profile_embed(
                    desc=f"{player.name} has no time recorded on {courses[course].game_and_name}."
                ), ephemeral=True)
            else:
                course = courses[course]
                return await inter.response.send_message(embed=player.profile_embed(
                    title_suffix=f" > {course.abbrev}",
                    desc=f"**{course.game_and_name}** - {timesheet[course.id].time_with_link()} - "
                         f"\\#{timesheet[course.id].rank}{rank_emoji(timesheet[course.id].rank)}"
                ))
        else:
            view = TimesheetSorter(inter.user)
            await inter.response.send_message(embed=player.timesheet_embed(), view=view)
            while not await view.wait():
                view = view.copy()
                await inter.edit_original_response(embed=player.timesheet_embed(view.sort), view=view)
            await inter.edit_original_response(embed=player.timesheet_embed(view.sort), view=None)

    @discord.app_commands.command(
        name="compare",
        description="Compare two players' timesheets."
    )
    @discord.app_commands.autocomplete(player1=player_autocomplete, player2=player_autocomplete)
    @discord.app_commands.describe(player1="Player 1 name", player2="Player 2 name")
    async def compare_command(self, inter: discord.Interaction, player1: int, player2: int):
        try:
            get_player(player1)
            get_player(player2)
            await inter.response.send_message(embed=players[player1].compare_embed(players[player2]))
        except GeneralConnectionError:
            await inter.response.send_message(embed=could_not_connect, ephemeral=True)


async def setup(bot):
    await bot.add_cog(PlayerCog(bot))
