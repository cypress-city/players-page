import bs4
import discord
import requests
import time

from modules.core import Record, rank_emoji, prettify_time, PlayerBase
from modules.courses import courses
from modules.embeds import blue_embed


class Player(PlayerBase):
    def __init__(self, name: str, id_no: int, country: str):
        super().__init__(name, id_no, country)
        self._profile_html = ""

    @staticmethod
    def from_html_table(tr: bs4.BeautifulSoup):
        cells = tr.find_all("td")
        name = cells[0].text
        id_no = int(cells[1].find("a", attrs={"class": "no-underline"}).get("href").split("=")[1])
        country = cells[2].text
        return Player(name, id_no, country)

    def _load_profile(self, force_reload: bool = False):
        if force_reload or not self._profile_html:
            response = requests.get(self.profile)
            if response.status_code == 200:
                self._profile_html = response.text
            else:
                raise discord.HTTPException

    @property
    def profile_html(self):
        self._load_profile(force_reload=False)
        return self._profile_html

    def timesheet(self, force_reload: bool = False, include_blanks: bool = True) -> dict[int, Record]:
        """Returns the player's timesheet as a dict with the course ID as the key and a Record object as the value."""
        self._load_profile(force_reload=force_reload)
        soup = bs4.BeautifulSoup(self.profile_html, "html.parser")
        timetable = soup.find("div", id="main-content").find("table", attrs={"class": "n"})
        ret = {}
        if timetable:
            for row in timetable.find_all("tr"):
                if row.find("td", attrs={"data-sv": True}):
                    course_id = int(row.find("td")["data-sv"])
                    if (record := Record.from_html_row(row)) or include_blanks:
                        ret[course_id] = record
        return ret

    def profile_embed(self, title_suffix: str = "", **kwargs):
        return blue_embed(title=f"Player: {self.name} {self.flag}{title_suffix}", url=self.profile, **kwargs)

    def timesheet_embed(self) -> discord.Embed:
        timesheet = {k: v for k, v in self.timesheet(force_reload=True).items() if v}
        times = ""
        current_cup = ""
        for k, v in timesheet.items():
            course = courses[k]
            if course.cup != current_cup:
                current_cup = course.cup
                times += "\n"
            times += f"**{course.game_and_name}** - {v.time_with_link()} - \\#{v.rank}{rank_emoji(v.rank)}\n"
        return self.profile_embed(
            desc=times.strip("\n") if times else "Player has no times submitted.",
            footer=(f"Total - {prettify_time(sum(g.time for g in timesheet.values()), include_hour=True)} | "
                    f"AF - {round(sum(g.rank for g in timesheet.values()) / len(timesheet), 4)}"
                    if len(timesheet) == len(courses) else f"Courses - {len(timesheet)}/{len(courses)}"
                    if timesheet else None)
        )

    def compare_embed(self, opponent) -> discord.Embed:
        my_timesheet = self.timesheet(force_reload=True)
        their_timesheet = opponent.timesheet(force_reload=True)
        scores = [0, 0, 0]
        ret = ""
        current_cup = ""

        for course in courses.values():
            if course.cup != current_cup:
                current_cup = course.cup
                ret += "\n"

            better_time = min(my_timesheet[course.id].time, their_timesheet[course.id].time)
            if better_time:
                if my_timesheet[course.id].time == better_time:
                    if their_timesheet[course.id].time == better_time:
                        scores[2] += 1
                    else:
                        scores[0] += 1
                else:
                    scores[1] += 1

            ret += f"**{course.game_and_name}:** " \
                   f"{'🔹 **' if my_timesheet[course.id].time == better_time > 0 else ''}" \
                   f"`{prettify_time(my_timesheet[course.id].time)}`" \
                   f"{'**' if my_timesheet[course.id].time == better_time > 0 else ''} - " \
                   f"{'**' if their_timesheet[course.id].time == better_time > 0 else ''}" \
                   f"`{prettify_time(their_timesheet[course.id].time)}`" \
                   f"{'** 🔸' if their_timesheet[course.id].time == better_time > 0 else ''}\n"

        return blue_embed(
            title=f"🔹 {self.name} {self.flag} vs. 🔸 {opponent.name} {opponent.flag}",
            desc=ret.strip("\n"),
            footer=f"Total: 🔷 {scores[0]} - {scores[1]} 🔶" +
                   (f" ({scores[2]} tie{'s' if scores[2] > 1 else ''})" if scores[2] else "")
        )


players: dict[int, Player] = {}
players_last_updated = 0


def refresh_player_list():
    response = requests.get("https://www.mariokart64.com/mkworld/playerlist.php", timeout=10)
    if response.status_code == 200:
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        player_table = soup.find("table", id="player-table").find("tbody")
        players.clear()
        player_list = [Player.from_html_table(g) for g in player_table.find_all("tr")]
        players.update({g.id: g for g in player_list})
        global players_last_updated
        players_last_updated = time.time()


def get_player(id_no: int = None, name: str = None, force_load: bool = False) -> Player | None:
    if time.time() - players_last_updated > 60 or (id_no not in players and force_load):
        refresh_player_list()
    if id_no is not None:
        return players.get(id_no)
    elif matches := [g for g in players.values() if g.name == name]:
        return matches[0]


async def player_autocomplete(inter: discord.Interaction, current: str) -> list[discord.app_commands.Choice[str]]:
    if time.time() - players_last_updated > 60:
        refresh_player_list()
    matches = sorted([g for g in players.values() if g.closeness(current)], key=lambda c: -c.closeness(current))
    return [discord.app_commands.Choice(name=g.name, value=g.id) for g in matches][:25]
