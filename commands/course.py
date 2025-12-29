import discord
from discord.ext import commands

from modules.core import Bot
from modules.courses import courses, course_autocomplete
from modules.embeds import could_not_connect, blue_embed
from modules.players import player_autocomplete, players
from modules.views import PageNavigator


class CourseCog(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @discord.app_commands.command(
        name="course",
        description="View the leaderboard for a course."
    )
    @discord.app_commands.autocomplete(course=course_autocomplete, player=player_autocomplete)
    @discord.app_commands.describe(course="Track name", player="Player name")
    async def course_command(self, inter: discord.Interaction, course: int, player: int = None):
        course = courses[course]
        try:
            course.load_leaderboard()
        except discord.HTTPException:
            return await inter.response.send_message(embed=could_not_connect, ephemeral=True)

        if player is not None:
            if course.get_record_for(player):
                starting_page = (course.get_record_for(player).rank - 1) // 10 + 1
            else:
                return await inter.response.send_message(embed=blue_embed(
                    title=course.full_display,
                    desc=f"{players[player].name} has no time recorded on {course.game_and_name}."
                ), ephemeral=True)
        else:
            starting_page = 1

        view = PageNavigator(inter.user, course.leaderboard_pages, starting_page=starting_page)
        await inter.response.send_message(embed=course.leaderboard_embed(view.page, player), view=view)
        while not await view.wait():
            view = PageNavigator(inter.user, course.leaderboard_pages, starting_page=view.page)
            await inter.edit_original_response(embed=course.leaderboard_embed(view.page, player), view=view)
        await inter.edit_original_response(embed=course.leaderboard_embed(view.page, player), view=None)


async def setup(bot: Bot):
    await bot.add_cog(CourseCog(bot))
