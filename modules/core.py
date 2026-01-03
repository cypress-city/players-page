import discord
from discord.ext import commands
from pathlib import Path
import json
import os
import bs4
import re

from modules.embeds import blue_embed


_COGS = [
    "commands.admin",
    "commands.course",
    "commands.help",
    "commands.player",
    "commands.submit",
    "commands.token"
]


country_codes = {
    'USA': 'us', 'UK': 'gb', 'Germany': 'de', 'France': 'fr', 'Canada': 'ca', 'Australia': 'au', 'Netherlands': 'nl',
    'Japan': 'jp', 'Spain': 'es', 'Italy': 'it', 'Afghanistan': 'af', 'Albania': 'al', 'Algeria': 'dz',
    'American Samoa': 'as', 'Andorra': 'ad', 'Angola': 'ao', 'Anguilla': 'ai', 'Antarctica': 'aq',
    'Antigua and Barbuda': 'ag', 'Argentina': 'ar', 'Armenia': 'am', 'Aruba': 'aw', 'Austria': 'at',
    'Azerbaijan': 'az', 'Bahamas': 'bs', 'Bahrain': 'bh', 'Bangladesh': 'bd', 'Barbados': 'bb', 'Belarus': 'by',
    'Belgium': 'be', 'Belize': 'bz', 'Benin': 'bj', 'Bermuda': 'bm', 'Bhutan': 'bt', 'Bolivia': 'bo',
    'Bosnia and Herzegovina': 'ba', 'Botswana': 'bw', 'Brazil': 'br', 'Brunei': 'bn', 'Bulgaria': 'bg',
    'Burkina Faso': 'bf', 'Burundi': 'bi', 'Cambodia': 'kh', 'Cameroon': 'cm', 'Cape Verde': 'cv',
    'Cayman Islands': 'ky', 'Central African Republic': 'cf', 'Chad': 'td', 'Chile': 'cl', 'China': 'cn',
    'Colombia': 'co', 'Comoros': 'km', 'Congo': 'cg', 'Congo, The DRC': 'cd', 'Cook Islands': 'ck', 'Costa Rica': 'cr',
    "Côte d'Ivoire": 'ci', 'Croatia': 'hr', 'Cuba': 'cu', 'Curacao': 'cw', 'Cyprus': 'cy', 'Czech Republic': 'cz',
    'Denmark': 'dk', 'Djibouti': 'dj', 'Dominica': 'dm', 'Dominican Republic': 'do', 'Ecuador': 'ec', 'Egypt': 'eg',
    'El Salvador': 'sv', 'Equatorial Guinea': 'gq', 'Eritrea': 'er', 'Estonia': 'ee', 'Eswatini': 'sz',
    'Ethiopia': 'et', 'Falkland Islands': 'fk', 'Faroe Islands': 'fo', 'Fiji': 'fj', 'Finland': 'fi',
    'French Guiana': 'gf', 'French Polynesia': 'pf', 'Gabon': 'ga', 'Gambia': 'gm', 'Georgia': 'ge', 'Ghana': 'gh',
    'Gibraltar': 'gi', 'Greece': 'gr', 'Greenland': 'gl', 'Grenada': 'gd', 'Guadeloupe': 'gp', 'Guam': 'gu',
    'Guatemala': 'gt', 'Guinea': 'gn', 'Guinea-Bissau': 'gw', 'Guyana': 'gy', 'Haiti': 'ht', 'Honduras': 'hn',
    'Hong Kong': 'hk', 'Hungary': 'hu', 'Iceland': 'is', 'India': 'in', 'Indonesia': 'id', 'Iran': 'ir', 'Iraq': 'iq',
    'Ireland': 'ie', 'Israel': 'il', 'Jamaica': 'jm', 'Jordan': 'jo', 'Kazakhstan': 'kz', 'Kenya': 'ke',
    'Kiribati': 'ki', 'Korea, D.P.R.': 'kp', 'Kuwait': 'kw', 'Kyrgyzstan': 'kg', 'Laos': 'la', 'Latvia': 'lv',
    'Lebanon': 'lb', 'Lesotho': 'ls', 'Liberia': 'lr', 'Libya': 'ly', 'Liechtenstein': 'li', 'Lithuania': 'lt',
    'Luxembourg': 'lu', 'Macau': 'mo', 'Madagascar': 'mg', 'Malawi': 'mw', 'Malaysia': 'my', 'Maldives': 'mv',
    'Mali': 'ml', 'Malta': 'mt', 'Mauritania': 'mr', 'Mauritius': 'mu', 'Mayotte': 'yt', 'Mexico': 'mx',
    'Micronesia': 'fm', 'Moldova': 'md', 'Monaco': 'mc', 'Mongolia': 'mn', 'Montenegro': 'me', 'Montserrat': 'ms',
    'Morocco': 'ma', 'Mozambique': 'mz', 'Myanmar': 'mm', 'Namibia': 'na', 'Nepal': 'np', 'New Caledonia': 'nc',
    'New Zealand': 'nz', 'Nicaragua': 'ni', 'Niger': 'ne', 'Nigeria': 'ng', 'Niue': 'nu', 'North Macedonia': 'mk',
    'Norway': 'no', 'Oman': 'om', 'Pakistan': 'pk', 'Palestine': 'ps', 'Panama': 'pa', 'Papua New Guinea': 'pg',
    'Paraguay': 'py', 'Peru': 'pe', 'Philippines': 'ph', 'Poland': 'pl', 'Portugal': 'pt', 'Qatar': 'qa',
    'Romania': 'ro', 'Russia': 'ru', 'Rwanda': 'rw', 'Samoa': 'ws', 'Sao Tome and Principe': 'st',
    'Saudi Arabia': 'sa', 'Senegal': 'sn', 'Serbia': 'rs', 'Seychelles': 'sc', 'Sierra Leone': 'sl', 'Singapore': 'sg',
    'Slovakia': 'sk', 'Slovenia': 'si', 'Solomon Islands': 'sb', 'Somalia': 'so', 'South Africa': 'za',
    'South Korea': 'kr', 'South Sudan': 'ss', 'Sri Lanka': 'lk', 'Sudan': 'sd', 'Suriname': 'sr', 'Sweden': 'se',
    'Switzerland': 'ch', 'Syria': 'sy', 'Taiwan': 'tw', 'Tajikistan': 'tj', 'Tanzania': 'tz', 'Thailand': 'th',
    'Timor-Leste': 'tl', 'Togo': 'tg', 'Tokelau': 'tk', 'Tonga': 'to', 'Trinidad and Tobago': 'tt', 'Tunisia': 'tn',
    'Turkey': 'tr', 'Turkmenistan': 'tm', 'Uganda': 'ug', 'Ukraine': 'ua', 'United Arab Emirates': 'ae',
    'Uruguay': 'uy', 'Uzbekistan': 'uz', 'Vanuatu': 'vu', 'Venezuela': 've', 'Viet Nam': 'vn', 'Western Sahara': 'eh',
    'Yemen': 'ye', 'Zambia': 'zm', 'Zimbabwe': 'zw'
}


def rank_emoji(rank: int) -> str:
    return " 🏆" if rank == 1 else " 🥈" if rank == 2 else " 🥉" if rank == 3 else " 🔹" if rank <= 10 else ""


def ordinal(n: int) -> str:
    return str(n) + (
        "st" if (n % 10 == 1 and n % 100 != 11) else
        "nd" if (n % 10 == 2 and n % 100 != 12) else
        "rd" if (n % 10 == 3 and n % 100 != 13) else
        "th"
    )


def prettify_seconds(seconds: float) -> str:
    return f"{int(abs(seconds))}.{str(round((abs(seconds) % 1) * 1000)).rjust(3, '0')}"


def prettify_time(time: float, include_hour: bool = False) -> str:
    if not time:
        return ("-:-" if include_hour else "") + "-:--.---"
    return (f"{int(time // 3600)}:" if include_hour else "") + \
        f"{str(int((time % 3600) // 60)).rjust(2, '0') if include_hour else int(time // 60)}:" \
        f"{prettify_seconds(time % 60).rjust(6, '0')}"


def unprettify_time(text: str) -> float:
    if not (match := re.fullmatch(
            r"((?P<hr>[0-9]):)?(?P<min>[0-9]{1,2})[:'.](?P<sec>[0-9]{1,2})[.\"](?P<mil>[0-9]{1,3})",
            text.strip('"')
    )):
        raise ValueError(f"Cannot interpret string as time: {text}")
    return round(
        (0 if not match["hr"] else int(match["hr"]) * 3600) +
        int(match["min"]) * 60 + int(match["sec"]) + int(match["mil"]) / 1000, 3
    )


def closeness(search_term: str, match: str) -> int:
    return 2 if match.startswith(search_term) else 1 if search_term in match else 0


class Record:
    def __init__(self, **kwargs):
        self.time: float = kwargs.get("time", 0.0)
        self.rank: int = kwargs.get("rank", 0)
        self.previous_time: float = kwargs.get("previous_time", 0.0)

    def __bool__(self):
        return bool(self.time)

    @staticmethod
    def from_html_row(html: str | bs4.BeautifulSoup):
        if isinstance(html, str):
            soup = bs4.BeautifulSoup(html, "html.parser")
        else:
            soup = html
        if not (record_info := soup.find("td", attrs={"data-tt-time": True})):
            return Record()
        if record_info.get("data-tt-insert-at-old-time") == "no older time":
            previous_time = 0
        else:
            previous_time = unprettify_time(record_info["data-tt-insert-at-old-time"])
        return Record(
            time=float(record_info["data-sv"]),
            rank=int(record_info["data-tt-position"]),
            previous_time=previous_time
        )


class PlayerBase:
    def __init__(self, name: str, id_no: int, country: str):
        self.name = name
        self.id = id_no
        self.country = country

    @property
    def profile(self):
        return f"https://www.mariokart64.com/mkworld/player.php?pid={self.id}"

    @property
    def flag(self):
        return f":flag_{country_codes[self.country]}:"

    def closeness(self, user_input: str):
        return closeness(user_input.lower(), self.name.lower())


class LeaderboardEntry:
    def __init__(self, player: PlayerBase, time: float, rank: int):
        self.player = player
        self.time = time
        self.rank = rank


class Leaderboard:
    def __init__(self, name: str, url: str, entries: list[LeaderboardEntry], region: str = None):
        self.name = name
        self.url = url
        self.region = region
        self.entries = entries

    def __getitem__(self, item: int):
        return self.entries[item]

    @property
    def pages(self):
        return int((len(self.entries) - 1) // 10 + 1)

    async def player_search(self, inter: discord.Interaction, current: str) -> list[discord.app_commands.Choice[str]]:
        players = [g.player for g in self.entries]
        matches = sorted([g for g in players if g.closeness(current)], key=lambda c: -c.closeness(current))
        return [discord.app_commands.Choice(name=g.name, value=g.id) for g in matches][:25]

    def get_record_for(self, player_id: int) -> LeaderboardEntry | None:
        try:
            return [g for g in self.entries if g.player.id == player_id][0]
        except IndexError:
            return None

    def embed(self, page: int = 1, highlight_player_id: int = None):
        return blue_embed(
            title=self.name + (f" > {self.region}" if self.region else ""),
            desc="\n".join(
                f"{g.rank}. {'**' if g.player.id == highlight_player_id else ''}"
                f"`{prettify_time(g.time)}` - {g.player.name} {g.player.flag}"
                f"{'**' if g.player.id == highlight_player_id else ''}"
                for g in self.entries[(page - 1) * 10:page * 10]
            ),
            footer=f"Total records: {len(self.entries)} | Page: {page}/{self.pages}",
            url=self.url
        )


class Bot(commands.Bot):  # main bot class
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(
            intents=intents, command_prefix="pp!",
            allowed_contexts=discord.app_commands.AppCommandContext(guild=True, dm_channel=True, private_channel=True),
            allowed_installs=discord.app_commands.AppInstallationType(guild=True, user=True)
        )
        self.tokens = self.load_tokens()

    @staticmethod
    def load_tokens(filename: str = "data/tokens.json") -> dict[str, str]:
        if not os.path.exists(filename):
            return {}
        with open(filename, "r") as f:
            return json.load(f)

    def save_tokens(self, filename: str = "data/tokens.json"):
        if not os.path.exists(filename):
            Path(filename).parent.mkdir(exist_ok=True, parents=True)
        with open(filename, "w") as f:
            json.dump(self.tokens, f)

    def set_token(self, user: discord.User, token: str):
        self.tokens[str(user.id)] = token
        self.save_tokens()

    def get_token(self, user: discord.User) -> str | None:
        return self.tokens.get(str(user.id))

    def remove_token(self, user: discord.User):
        self.tokens.pop(str(user.id))
        self.save_tokens()

    async def setup_hook(self) -> None:
        for extension in _COGS:
            await self.load_extension(extension)
