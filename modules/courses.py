import discord


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

    def closeness(self, user_input: str):
        term = user_input.lower()
        return 2 if term in self.abbrev.lower() else 1 if term in self.name.lower() else 0


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


def rank_emoji(rank: int) -> str:
    return " 🏆" if rank == 1 else " 🥈" if rank == 2 else " 🥉" if rank == 3 else " 🔹" if rank <= 10 else ""
