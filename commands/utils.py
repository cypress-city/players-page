# Assorted Time Trial utilities that may be moved to a dedicated bot in the future.
import discord
from discord.ext import commands

from modules.core import Bot, unprettify_time, prettify_time


TIME_ERROR = "**⚠️ Bad input: `{input}`**\n-# Times should look like `1:23.456` or `12.345`"


def prettify_split(split: float) -> str:
    return prettify_time(split).lstrip("0:")


class UtilsCog(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @discord.app_commands.command(
        name="splits",
        description="Calculates the final lap time (split) of a run."
    )
    @discord.app_commands.describe(
        finish_time="Finish (total) time of the run", lap1="Lap 1 time", lap2="Lap 2 time",
        lap3="Lap 3 time (optional)", lap4="Lap 4 time (optional)", lap5="Lap 5 time (optional)"
    )
    async def splits_command(self, inter: discord.Interaction, finish_time: str, lap1: str, lap2: str,
                             lap3: str = None, lap4: str = None, lap5: str = None):
        try:
            finish_time = unprettify_time(finish_time)
        except ValueError:
            return await inter.response.send_message(TIME_ERROR.format(input=finish_time), ephemeral=True)

        splits = []
        for split in (lap1, lap2, lap3, lap4, lap5):
            if split:
                try:
                    splits.append(unprettify_time(split))
                except ValueError:
                    return await inter.response.send_message(TIME_ERROR.format(input=split), ephemeral=True)

        final_split = finish_time - sum(splits)
        return await inter.response.send_message(
            f"**{prettify_split(final_split)}**"
            f"\n-# {' - '.join(prettify_split(g) for g in [*splits, final_split])} = {prettify_time(finish_time)}",
            ephemeral=True
        )


async def setup(bot: Bot):
    await bot.add_cog(UtilsCog(bot))
