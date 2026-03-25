import discord
from discord.ext import commands
import matplotlib.pyplot as plt
import numpy as np

from modules.core import Bot
from modules.courses import Course, courses, course_autocomplete, region_autocomplete
from modules.embeds import could_not_connect, blue_embed
from modules.players import get_player, player_autocomplete, players
from modules.views import PageNavigator


class CourseCog(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @discord.app_commands.command(
        name="course",
        description="View the leaderboard for a course."
    )
    @discord.app_commands.autocomplete(
        course=course_autocomplete, player=player_autocomplete, region=region_autocomplete
    )
    @discord.app_commands.describe(course="Track name", player="Player name", region="Country or region name")
    async def course_command(self, inter: discord.Interaction, course: int, player: int = None, region: str = None):
        course = courses[course]
        try:
            leaderboard = course.get_leaderboard(region_filter=region)
        except ConnectionError:
            return await inter.response.send_message(embed=could_not_connect, ephemeral=True)

        if player is not None:
            if leaderboard.get_record_for(player):
                starting_page = (leaderboard.get_record_for(player).rank - 1) // 10 + 1
            else:
                return await inter.response.send_message(embed=blue_embed(
                    title=course.full_display,
                    desc=f"{players[player].name} has no time recorded on {course.game_and_name}."
                ), ephemeral=True)
        else:
            starting_page = 1

        if not leaderboard.entries:
            return await inter.response.send_message(embed=blue_embed(
                title=course.full_display + (f" > {region}" if region else ""),
                desc="No records found."
            ))

        view = PageNavigator(inter.user, leaderboard.pages, starting_page=starting_page)
        await inter.response.send_message(embed=leaderboard.embed(view.page, player), view=view)
        while not await view.wait():
            view = view.copy()
            await inter.edit_original_response(embed=leaderboard.embed(view.page, player), view=view)
        await inter.edit_original_response(embed=leaderboard.embed(view.page, player), view=None)

    @discord.app_commands.command(
        name="graph",
        description="View a graph of all submitted records on a course."
    )
    @discord.app_commands.autocomplete(
        course=course_autocomplete, player=player_autocomplete
    )
    @discord.app_commands.describe(course="Track name", player="Player name")
    async def graph_command(self, inter: discord.Interaction, course: int, player: int = None):
        course = courses[course]
        try:
            course.get_leaderboard()
        except ConnectionError:
            return await inter.response.send_message(embed=could_not_connect, ephemeral=True)

        await inter.response.defer()
        graph(course, player)
        return await inter.edit_original_response(attachments=[discord.File(f"images/{course.id}-{player}.png")])


def graph(course: Course, player: int = None):
    leaderboard = course.get_leaderboard()
    times = sorted([g.time for g in leaderboard.entries])
    min_time = int(min(times) - 0.1)
    max_time = times[round(len(times) * 0.8)]
    step_size = 0.1
    x_values = np.arange(min_time, int(max(times))+1, step_size)
    plt.hist(times, bins=x_values, color="#88AACC", label="Players")
    plt.plot(x_values, [len([g for g in times if n - 0.5 <= g < n + 0.5]) * step_size for n in x_values],
             color="black", label="Moving avg.")
    if highlight := leaderboard.get_record_for(player):
        plt.axvline(highlight.time, color="red", label=get_player(player).name)
        if highlight.time > max_time:
            max_time = int(highlight.time) + 1
    tick_size = min(g for g in [2, 4, 10, 30, 60] if (max_time - min_time) / g < 10)
    x_range = np.arange(min_time, max_time + tick_size, tick_size)
    plt.xlim(x_range[0], x_range[-1])
    plt.xticks(x_range, [f"{int(g // 60)}:{str(int(g % 60)).rjust(2, '0')}" for g in x_range])
    plt.xticks([g+tick_size/2 for g in x_range][:-1], minor=True)
    plt.title(course.game_and_name)
    plt.ylabel("Number of players")
    plt.legend()
    plt.savefig(f"images/{course.id}-{player}.png")
    plt.close()


async def setup(bot: Bot):
    await bot.add_cog(CourseCog(bot))
