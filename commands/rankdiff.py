import discord
from discord.ext import commands

from modules.core import rank_emoji, prettify_time, prettify_seconds, GeneralConnectionError
from modules.courses import courses, course_autocomplete
from modules.embeds import could_not_connect
from modules.players import player_autocomplete, get_player


class RankDiffCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(
        name="rankdiff",
        description="See how far a player's time is from a target rank on a course."
    )
    @discord.app_commands.autocomplete(
        player=player_autocomplete, 
        course=course_autocomplete
    )
    @discord.app_commands.describe(
        player="Player name",
        course="Track name",
        rank="Target rank to compare against"
    )
    async def rankdiff_command(self, inter: discord.Interaction, player: int, course: int, rank: int):
        if rank < 1:
            return await inter.response.send_message(
                "Lol what", ephemeral=True
            )

        try:
            player = get_player(player)
            timesheet = player.timesheet()
            leaderboard = courses[course].get_leaderboard()
        except GeneralConnectionError:
            return await inter.response.send_message(embed=could_not_connect, ephemeral=True)

        course_obj = courses[course]

        # Check player has a time on this course
        player_record = timesheet.get(course)
        if not player_record:
            return await inter.response.send_message(embed=player.profile_embed(
                desc=f"{player.name} has no time recorded on {course_obj.game_and_name}."
            ), ephemeral=True)
       
        # Find the entry at the target rank, accounting for ties
        # (e.g. if ranks 199 and 200 are tied, rank 200 won't exist — find the tie band instead)
        max_rank = leaderboard.entries[-1].rank if leaderboard.entries else 0
        if rank > max_rank:
            return await inter.response.send_message(embed=player.profile_embed(
                desc=f"No time found at rank #{rank} on {course_obj.game_and_name}. "
                     f"The leaderboard only goes up to rank #{max_rank}."
            ), ephemeral=True)
 
        # Find the highest rank that is still <= the target rank
        effective_rank = max(e.rank for e in leaderboard.entries if e.rank <= rank)
        rank_entries = [e for e in leaderboard.entries if e.rank == effective_rank]
        is_tied = len(rank_entries) > 1
        target_entry = rank_entries[0]
        player_time = player_record.time
        target_time = target_entry.time
        diff = player_time - target_time  # positive = slower, negative = faster

        if diff == 0:
            diff_str = "0.000"
            diff_sign = ""
        elif diff > 0:
            diff_str = f"+{prettify_seconds(diff)}"
            diff_sign = "+"
        else:
            diff_str = f"**–{prettify_seconds(-diff)}**"
            diff_sign = "–"

        player_rank_str = f"#{player_record.rank}{rank_emoji(player_record.rank)}"
        target_rank_str = f"#{rank}{rank_emoji(rank)}"

        desc = (
            f"**{course_obj.game_and_name}**\n\n"
            f"{player_rank_str} — {player_record.time_with_link()} — {player.name}\n"
            f"{target_rank_str} — `{prettify_time(target_time)}` — {target_entry.player.name} "
            f"{target_entry.player.flag}\n\n"
            f"**Diff:** `{diff_str}`"
        )

        await inter.response.send_message(embed=player.profile_embed(
            title_suffix=f" > {course_obj.abbrev} > Rank Diff",
            desc=desc
        ))


async def setup(bot):
    await bot.add_cog(RankDiffCog(bot))
