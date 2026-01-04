import discord
from discord.ext import commands
import bs4
import requests

from modules.core import Bot, Leaderboard, LeaderboardEntry, PlayerBase, prettify_time, unprettify_time
from modules.courses import region_autocomplete
from modules.embeds import blue_embed, could_not_connect
from modules.players import players, player_autocomplete
from modules.views import PageNavigator


class PlayerLeaderboardEntry(LeaderboardEntry):
    def __init__(self, player: PlayerBase, score: float, rank: int, mode: str):
        super().__init__(player, score, rank)
        self.mode = mode

    @property
    def score_display(self):
        if self.mode == "time":
            return prettify_time(self.time)
        else:
            return f"{str(int(self.time))}.{str(round((self.time % 1) * 1e4)).rjust(4, '0')}"

    @staticmethod
    def from_html_row(html: str | bs4.BeautifulSoup, mode: str):
        if isinstance(html, str):
            soup = bs4.BeautifulSoup(html, "html.parser")
        else:
            soup = html
        cells = soup.find_all("td")
        return PlayerLeaderboardEntry(
            player=PlayerBase(
                name=cells[1].text,
                id_no=int(cells[2].find("a")["href"].split("=")[1]),
                country=cells[3].text
            ),
            score=(unprettify_time(cells[4].text) if mode == "time" else float(cells[4].text)),
            rank=int(cells[0].text),
            mode=mode
        )


def load_leaderboard(url: str, mode: str, title: str, region_filter: str = None) -> Leaderboard:
    ret = []
    region = f"&country={'+'.join(region_filter.split())}" if region_filter else ""
    current_page = 1
    total_submissions = 0

    while current_page <= max((total_submissions - 1) // 100 + 1, 1):
        response = requests.get(url + f"&page={current_page}{region}", timeout=3)
        if response.status_code != 200:
            raise discord.HTTPException
        soup = bs4.BeautifulSoup(response.text, "html.parser")

        total_submissions = int(
            soup.find("div", attrs={"class": "page-info"}).text.split(" of ")[1]
        )

        table = soup.find("div", id="main-content").find("table", attrs={"class": "n"})
        for row in table.find_all("tr", attrs={"class": True}):
            ret.append(PlayerLeaderboardEntry.from_html_row(row, mode))

        current_page += 1

    ret.sort(key=lambda c: c.rank)
    return Leaderboard(title, url, ret, region=region_filter)


class LeaderboardsCog(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    group = discord.app_commands.Group(name="leaderboard", description="Overall player leaderboards.")

    @staticmethod
    async def browse_leaderboard(inter: discord.Interaction, leaderboard: Leaderboard, player: int, region: str):
        if player is not None:
            if leaderboard.get_record_for(player):
                starting_page = (leaderboard.get_record_for(player).rank - 1) // 10 + 1
            else:
                return await inter.response.send_message(embed=blue_embed(
                    title=leaderboard.name,
                    desc=f"{players[player].name} does not have a complete timesheet.",
                    url=leaderboard.url
                ), ephemeral=True)
        else:
            starting_page = 1

        if not leaderboard.entries:
            return await inter.response.send_message(embed=blue_embed(
                title=leaderboard.name + (f" > {region}" if region else ""),
                desc="No complete timesheets found.",
                url=leaderboard.url
            ))

        view = PageNavigator(inter.user, leaderboard.pages, starting_page=starting_page)
        await inter.response.send_message(embed=leaderboard.embed(view.page, player), view=view)
        while not await view.wait():
            view = view.copy()
            await inter.edit_original_response(embed=leaderboard.embed(view.page, player), view=view)
        await inter.edit_original_response(embed=leaderboard.embed(view.page, player), view=None)

    @group.command(
        name="average",
        description="View player rankings by the average of their ranks on all 30 courses (also called Average Finish)."
    )
    @discord.app_commands.autocomplete(player=player_autocomplete, region=region_autocomplete)
    @discord.app_commands.describe(player="Player name", region="Country or region name")
    async def average_finish(self, inter: discord.Interaction, player: int = None, region: str = None):
        try:
            leaderboard = load_leaderboard(
                "https://www.mariokart64.com/mkworld/stat.php?type=AF",
                mode="score", title="AF | Average Finish", region_filter=region
            )
        except discord.HTTPException:
            return await inter.response.send_message(embed=could_not_connect, ephemeral=True)
        return await self.browse_leaderboard(inter, leaderboard, player, region)

    @group.command(
        name="total",
        description="View player rankings by the total of their times on all 30 courses."
    )
    @discord.app_commands.autocomplete(player=player_autocomplete, region=region_autocomplete)
    @discord.app_commands.describe(player="Player name", region="Country or region name")
    async def total_time(self, inter: discord.Interaction, player: int = None, region: str = None):
        try:
            leaderboard = load_leaderboard(
                "https://www.mariokart64.com/mkworld/stat.php?type=Total%20Times",
                mode="time", title="Total Times", region_filter=region
            )
        except discord.HTTPException:
            return await inter.response.send_message(embed=could_not_connect, ephemeral=True)
        return await self.browse_leaderboard(inter, leaderboard, player, region)


async def setup(bot: Bot):
    await bot.add_cog(LeaderboardsCog(bot))
