import discord
from discord.ext import commands

from modules.core import rank_emoji, prettify_time
from modules.courses import courses, course_autocomplete
from modules.embeds import could_not_connect
from modules.players import player_autocomplete, get_player, players


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
        if course != -1:
            try:
                player = get_player(player)
                timesheet = player.timesheet()
            except discord.HTTPException:
                return await inter.response.send_message(embed=could_not_connect, ephemeral=True)

            if not timesheet.get(course):
                return await inter.response.send_message(embed=player.profile_embed(
                    desc=f"{player.name} has no time recorded on {courses[course].game_and_name}."
                ), ephemeral=True)
            else:
                course = courses[course]
                return await inter.response.send_message(embed=player.profile_embed(
                    title_suffix=f" > {course.abbrev}",
                    desc=f"**{course.game_and_name}** - `{timesheet[course.id].time_with_link()}` - "
                         f"\\#{timesheet[course.id].rank}{rank_emoji(timesheet[course.id].rank)}"
                ))

        try:
            await inter.response.send_message(embed=players[player].timesheet_embed())
        except discord.HTTPException:
            await inter.response.send_message(embed=could_not_connect, ephemeral=True)

    @discord.app_commands.command(
        name="compare",
        description="Compare two players' timesheets."
    )
    @discord.app_commands.autocomplete(player1=player_autocomplete, player2=player_autocomplete)
    @discord.app_commands.describe(player1="Player 1 name", player2="Player 2 name")
    async def compare_command(self, inter: discord.Interaction, player1: int, player2: int):
        try:
            await inter.response.send_message(embed=players[player1].compare_embed(players[player2]))
        except discord.HTTPException:
            await inter.response.send_message(embed=could_not_connect, ephemeral=True)


async def setup(bot):
    await bot.add_cog(PlayerCog(bot))
