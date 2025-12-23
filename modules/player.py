import bs4
import discord
from discord.ext import commands
import requests
import time

from modules.courses import courses
from modules.embeds import blue_embed, could_not_connect


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


def pretty_time(course_time: float, include_hour: bool = False):
    if not course_time:
        return "-:--.---"
    return (f"{int(course_time // 3600)}:" if include_hour else "") + \
           f"{str(int((course_time % 3600) // 60)).rjust(2, '0') if include_hour else int(course_time // 60)}:" \
           f"{str(int(course_time % 60)).rjust(2, '0')}." \
           f"{str(round((course_time % 1) * 1000)).rjust(3, '0')}"


class Player:
    def __init__(self, name: str, id_no: int, country: str):
        self.name = name
        self.id = id_no
        self.country = country

    @staticmethod
    def from_html_table(tr: bs4.BeautifulSoup):
        cells = tr.find_all("td")
        name = cells[0].text
        id_no = int(cells[1].find("a", attrs={"class": "no-underline"}).get("href").split("=")[1])
        country = cells[2].text
        return Player(name, id_no, country)

    @property
    def profile(self):
        return f"https://www.mariokart64.com/mkworld/player.php?pid={self.id}"

    @property
    def flag(self):
        return f":flag_{country_codes[self.country]}:"

    def closeness(self, user_input: str):
        term = user_input.lower()
        return 2 if self.name.lower().startswith(term) else 1 if term in self.name.lower() else 0

    def timesheet(self) -> dict[int, (float, int)]:
        """Returns the player's timesheet as a dict with the course ID as the key and (time, rank) as the value."""
        response = requests.get(self.profile)
        if response.status_code != 200:
            raise discord.HTTPException
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        timetable = soup.find("div", id="main-content").find("table", attrs={"class": "n"})
        ret = {}
        if timetable:
            for row in timetable.find_all("tr"):
                if row.find("td", attrs={"data-tt-position": True}):
                    cells = row.find_all("td", attrs={"data-sv": True})
                    course_id = int(cells[0]["data-sv"])
                    course_time = float(cells[1]["data-sv"])
                    course_rank = int(cells[1]["data-tt-position"])
                    ret[course_id] = course_time, course_rank
        return ret

    def timesheet_with_blanks(self) -> dict[int, (float, int)]:
        """Includes unsubmitted times as (0.0, 0)."""
        timesheet = self.timesheet()
        return {g: timesheet.get(g, (0.0, 0)) for g in courses}

    def timesheet_embed(self) -> discord.Embed:
        timesheet = self.timesheet()
        times = ""
        current_cup = ""
        for k, v in timesheet.items():
            course = courses[k]
            if course.cup != current_cup:
                current_cup = course.cup
                times += "\n"
            emoji = " 🏆" if v[1] == 1 else " 🥈" if v[1] == 2 else " 🥉" if v[1] == 3 else " 🔹" if v[1] <= 10 else ""
            times += f"**{course.game_and_name}** - `{pretty_time(v[0])}` - \\#{v[1]}{emoji}\n"
        return blue_embed(
            title=f"Player: {self.name} {self.flag}",
            desc=times.strip("\n") if times else "Player has no times submitted.",
            footer=(f"Total - {pretty_time(sum(g[0] for g in timesheet.values()), include_hour=True)} | "
                    f"AF - {round(sum(g[1] for g in timesheet.values()) / len(timesheet), 4)}"
                    if len(timesheet) == len(courses) else f"Courses - {len(timesheet)}/{len(courses)}"
                    if timesheet else None),
            url=self.profile
        )

    def compare_embed(self, opponent) -> discord.Embed:
        my_timesheet = self.timesheet_with_blanks()
        their_timesheet = opponent.timesheet_with_blanks()
        scores = [0, 0, 0]
        ret = ""
        current_cup = ""

        for course in courses.values():
            if course.cup != current_cup:
                current_cup = course.cup
                ret += "\n"

            better_time = min(my_timesheet[course.id][0], their_timesheet[course.id][0])
            if better_time:
                if my_timesheet[course.id][0] == better_time:
                    if their_timesheet[course.id][0] == better_time:
                        scores[2] += 1
                    else:
                        scores[0] += 1
                else:
                    scores[1] += 1

            ret += f"**{course.game_and_name}:** " \
                   f"{'🔹 **' if my_timesheet[course.id][0] == better_time > 0 else ''}" \
                   f"`{pretty_time(my_timesheet[course.id][0])}`" \
                   f"{'**' if my_timesheet[course.id][0] == better_time > 0 else ''} - " \
                   f"{'**' if their_timesheet[course.id][0] == better_time > 0 else ''}" \
                   f"`{pretty_time(their_timesheet[course.id][0])}`" \
                   f"{'** 🔸' if their_timesheet[course.id][0] == better_time > 0 else ''}\n"

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


async def player_autocomplete(inter: discord.Interaction, current: str) -> list[discord.app_commands.Choice[str]]:
    if time.time() - players_last_updated > 600:
        refresh_player_list()
    matches = sorted([g for g in players.values() if g.closeness(current)], key=lambda c: -c.closeness(current))
    return [discord.app_commands.Choice(name=g.name, value=g.id) for g in matches][:25]


class PlayerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(
        name="player",
        description="View a player's timesheet."
    )
    @discord.app_commands.autocomplete(player=player_autocomplete)
    @discord.app_commands.describe(player="Player name")
    async def player_command(self, inter: discord.Interaction, player: int):
        try:
            await inter.response.send_message(embed=players[player].timesheet_embed())
        except discord.HTTPException:
            await inter.response.send_message(embed=could_not_connect, ephemeral=True)

    @discord.app_commands.command(
        name="compare",
        description="Compare two players' timesheets."
    )
    @discord.app_commands.autocomplete(player1=player_autocomplete, player2=player_autocomplete)
    @discord.app_commands.describe(player1="Player 1 name", player2="Player 2 name")
    async def compare_command(self, inter: discord.Interaction, player1: int, player2: int):
        try:
            await inter.response.send_message(embed=players[player1].compare_embed(players[player2]))
        except discord.HTTPException:
            await inter.response.send_message(embed=could_not_connect, ephemeral=True)


async def setup(bot):
    await bot.add_cog(PlayerCog(bot))
