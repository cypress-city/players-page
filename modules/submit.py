import discord
from discord.ext import commands
import datetime
import re
import requests
import bs4

from modules.bot import Bot
from modules.embeds import green_embed, red_embed


class Course:
    def __init__(self, abbrev: str, name: str, id_no: int, source_game: str = ""):
        self.name = name
        self.abbrev = abbrev
        self.id = id_no
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


courses = [
    Course("MBC", "Mario Bros. Circuit", 0),
    Course("CC", "Crown City", 1),
    Course("WS", "Whistlestop Summit", 2),
    Course("DKS", "DK Spaceport", 3),
    Course("rDH", "Desert Hills", 4, "DS"),
    Course("rSGB", "Shy Guy Bazaar", 5, "3DS"),
    Course("rWS", "Wario Stadium", 6, "N64"),
    Course("rAF", "Airship Fortress", 7, "DS"),
    Course("rDKP", "DK Pass", 8, "DS"),
    Course("SP", "Starview Peak", 9),
    Course("rSHS", "Sky-High Sundae", 10, "Tour"),
    Course("rWSh", "Wario Shipyard", 11, "3DS"),
    Course("rKTB", "Koopa Troopa Beach", 12, "SNES"),
    Course("FO", "Faraway Oasis", 13),
    Course("PS", "Peach Stadium", 14),
    Course("rPB", "Peach Beach", 15, "GCN"),
    Course("SSS", "Salty Salty Speedway", 16),
    Course("rDDJ", "Dino Dino Jungle", 17, "GCN"),
    Course("GBR", "Great ? Block Ruins", 18),
    Course("CCF", "Cheep Cheep Falls", 19),
    Course("DD", "Dandelion Depths", 20),
    Course("BCi", "Boo Cinema", 21),
    Course("DBB", "Dry Bones Burnout", 22),
    Course("rMMM", "Moo Moo Meadows", 23, "Wii"),
    Course("rCM", "Choco Mountain", 24, "N64"),
    Course("rTF", "Toad's Factory", 25, "Wii"),
    Course("BC", "Bowser's Castle", 26),
    Course("AH", "Acorn Heights", 27),
    Course("rMC", "Mario Circuit", 28, "SNES"),
    Course("RR", "Rainbow Road", 29)
]


async def course_autocomplete(inter: discord.Interaction, current: str) -> list[discord.app_commands.Choice[str]]:
    matches = sorted([g for g in courses if g.closeness(current)], key=lambda c: -c.closeness(current))
    return [discord.app_commands.Choice(name=g.full_display, value=g.id) for g in matches][:25]


def submit_time(
        course_id: int, time: float, date: str, token: str, timestamp: str, sig: str,
        system: str = "Normal", comments: str = "N/A"
) -> requests.Response:
    form_data = {
        "cid": course_id,
        "system": system,
        "time": time,
        "date": date,
        "comments": comments,
        "token": token,
        "timestamp": timestamp,
        "sig": sig
    }
    return requests.post("https://www.mariokart64.com/mkworld/quick_entry_form.php", data=form_data)


class SubmitCog(commands.Cog):
    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot

    @staticmethod
    def get_auth_sig() -> (str, str):
        example_profile = "https://www.mariokart64.com/mkworld/player.php?pid=252"
        hackney = requests.get(example_profile, timeout=10)
        if hackney.status_code != 200:
            raise discord.HTTPException
        soup = bs4.BeautifulSoup(hackney.text, "html.parser")
        timestamp_input = soup.find("input", attrs={"name": "timestamp"})
        sig_input = soup.find("input", attrs={"name": "sig"})
        return timestamp_input["value"], sig_input["value"]

    @discord.app_commands.command(
        name="submit",
        description="Submit a time to the Player's Page."
    )
    @discord.app_commands.autocomplete(course=course_autocomplete)
    @discord.app_commands.describe(
        course="Track name", time="Time formatted as 1:23.456"
    )
    async def submit_command(self, inter: discord.Interaction, course: int, time: str):
        if not (token := self.bot.get_token(inter.user)):
            return await inter.response.send_message(embed=red_embed(
                title="⚠️ Register first!",
                desc="Before you can submit times, you need to share your self-submit token with the bot using "
                     "the `/token set` command. Check `/help` for more information."
            ), ephemeral=True)

        if not (reg := re.fullmatch(r"(?P<min>[0-9]):(?P<sec>[0-9]{2}\.[0-9]{3})", time)):
            return await inter.response.send_message(embed=red_embed(
                title="⚠️ Formatting error.",
                desc="Times should be in the format: `1:23.456`"
            ), ephemeral=True)

        time_as_float = int(reg.group("min")) * 60 + float(reg.group("sec"))
        date = datetime.datetime.now(tz=datetime.timezone.utc).strftime("%Y-%m-%d")
        course = courses[course]

        try:
            auth_timestamp, auth_sig = self.get_auth_sig()
        except discord.HTTPException:
            return await inter.response.send_message(embed=red_embed(
                title="⚠️ Something went wrong.",
                desc="The bot could not connect to the Player's Page. Try again in a few minutes."
            ), ephemeral=True)

        response = submit_time(course.id, time_as_float, date, token, auth_timestamp, auth_sig)
        if response.status_code == 200:
            return await inter.response.send_message(embed=green_embed(
                title="✅ Time updated!",
                desc=f"Submitted a time of `{time}` on {course.game_and_name}."
            ))
        else:
            return await inter.response.send_message(embed=red_embed(
                title="⚠️ Something went wrong.",
                desc=f"The bot encountered an error in submitting your time.\n"
                     f"`{response.status_code} {response.text}`"
            ), ephemeral=True)


async def setup(bot: Bot):
    await bot.add_cog(SubmitCog(bot))
