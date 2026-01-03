import discord
import bs4
import requests

from modules.core import unprettify_time, PlayerBase, country_codes, closeness, Leaderboard, LeaderboardEntry


class Course:
    def __init__(self, abbrev: str, name: str, id_no: int, cup: str, source_game: str = ""):
        self.name = name
        self.abbrev = abbrev
        self.id = id_no
        self.cup = cup
        self.source_game = source_game

    @property
    def game_and_name(self):
        return f"{(self.source_game+' ') if self.source_game else ''}{self.name}"

    @property
    def full_display(self):
        return f"[{self.abbrev}] {self.game_and_name}"

    @property
    def url(self):
        return f"https://www.mariokart64.com/mkworld/course.php?system=Normal&cid={self.id}"

    def get_leaderboard(self, region_filter: str = None):
        ret = []
        region = f"&country={'+'.join(region_filter.split())}" if region_filter else ""
        current_page = 1
        total_submissions = 0

        while current_page <= max((total_submissions - 1) // 100 + 1, 1):
            response = requests.get(self.url + f"&page={current_page}{region}")
            if response.status_code != 200:
                raise discord.HTTPException
            soup = bs4.BeautifulSoup(response.text, "html.parser")

            total_submissions = int(
                soup.find("div", attrs={"class": "page-info"}).text.split(" of ")[1]
            )

            table = soup.find("div", id="main-content").find("table", attrs={"class": "n"})
            for row in table.find_all("tr", attrs={"class": True}):
                cells = row.find_all("td")
                if video_cell := cells[5].find("a"):
                    video_link = video_cell["href"]
                else:
                    video_link = None
                ret.append(LeaderboardEntry(
                    player=PlayerBase(
                        name=cells[1].text,
                        id_no=int(cells[2].find("a")["href"].split("=")[1]),
                        country=cells[3].text
                    ),
                    time=unprettify_time(cells[4].text),
                    rank=int(cells[0].text),
                    video_link=video_link
                ))

            current_page += 1

        ret.sort(key=lambda c: c.rank)
        return Leaderboard(self.full_display, self.url, ret, region=region_filter)

    def closeness(self, user_input: str):
        term = user_input.lower()
        return 3 if term in self.abbrev.lower() else 2 if term in self.name.lower() else \
            1 if term in self.full_display.lower() else 0


courses: dict[int, Course] = {
    0: Course("MBC", "Mario Bros. Circuit", 0, "Mushroom"),
    1: Course("CC", "Crown City", 1, "Mushroom"),
    2: Course("WS", "Whistlestop Summit", 2, "Mushroom"),
    3: Course("DKS", "DK Spaceport", 3, "Mushroom"),
    4: Course("rDH", "Desert Hills", 4, "Flower", "DS"),
    5: Course("rSGB", "Shy Guy Bazaar", 5, "Flower", "3DS"),
    6: Course("rWS", "Wario Stadium", 6, "Flower", "N64"),
    7: Course("rAF", "Airship Fortress", 7, "Flower", "DS"),
    8: Course("rDKP", "DK Pass", 8, "Star", "DS"),
    9: Course("SP", "Starview Peak", 9, "Star"),
    10: Course("rSHS", "Sky-High Sundae", 10, "Star", "Tour"),
    11: Course("rWSh", "Wario Shipyard", 11, "Star", "3DS"),
    12: Course("rKTB", "Koopa Troopa Beach", 12, "Shell", "SNES"),
    13: Course("FO", "Faraway Oasis", 13, "Shell"),
    14: Course("PS", "Peach Stadium", 14, "Shell"),
    15: Course("rPB", "Peach Beach", 15, "Banana", "GCN"),
    16: Course("SSS", "Salty Salty Speedway", 16, "Banana"),
    17: Course("rDDJ", "Dino Dino Jungle", 17, "Banana", "GCN"),
    18: Course("GBR", "Great ? Block Ruins", 18, "Banana"),
    19: Course("CCF", "Cheep Cheep Falls", 19, "Leaf"),
    20: Course("DD", "Dandelion Depths", 20, "Leaf"),
    21: Course("BCi", "Boo Cinema", 21, "Leaf"),
    22: Course("DBB", "Dry Bones Burnout", 22, "Leaf"),
    23: Course("rMMM", "Moo Moo Meadows", 23, "Lightning", "Wii"),
    24: Course("rCM", "Choco Mountain", 24, "Lightning", "N64"),
    25: Course("rTF", "Toad's Factory", 25, "Lightning", "Wii"),
    26: Course("BC", "Bowser's Castle", 26, "Lightning"),
    27: Course("AH", "Acorn Heights", 27, "Special"),
    28: Course("rMC", "Mario Circuit", 28, "Special", "SNES"),
    29: Course("RR", "Rainbow Road", 29, "Special")
}


async def course_autocomplete(inter: discord.Interaction, current: str) -> list[discord.app_commands.Choice[str]]:
    matches = sorted([g for g in courses.values() if g.closeness(current)], key=lambda c: -c.closeness(current))
    return [discord.app_commands.Choice(name=g.full_display, value=g.id) for g in matches][:25]


regions = ["North America", "South America", "Europe", "Africa", "Asia", "Oceania"] + list(country_codes)


def region_closeness(search_term: str, match: str) -> int:
    return 3 if search_term.lower() == country_codes.get(match) else closeness(search_term.lower(), match.lower())


async def region_autocomplete(inter: discord.Interaction, current: str) -> list[discord.app_commands.Choice[str]]:
    matches = sorted([g for g in regions if region_closeness(current, g)], key=lambda c: -region_closeness(current, c))
    return [discord.app_commands.Choice(name=g, value=g) for g in matches][:25]
