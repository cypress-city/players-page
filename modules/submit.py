import discord
from discord.ext import commands
import datetime
import re
import requests
import bs4

from modules.core import Bot, ordinal, rank_emoji, prettify_seconds
from modules.embeds import green_embed, red_embed, could_not_connect
from modules.courses import courses, course_autocomplete
from modules.player import get_player


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
        description="Submit a record to the Players' Page."
    )
    @discord.app_commands.autocomplete(course=course_autocomplete)
    @discord.app_commands.describe(
        course="Track name", time="Time formatted as 1:23.456",
        comments="Comments (e.g. video links), max. of 127 characters",
        date="Date formatted as YYYY-MM-DD (e.g. 2025-07-30 for July 30, 2025); leave blank for today's date"
    )
    async def submit_command(
            self, inter: discord.Interaction, course: int, time: str,
            comments: str = "N/A", date: str = ""
    ):
        if not (token := self.bot.get_token(inter.user)):
            return await inter.response.send_message(embed=red_embed(
                title="⚠️ Register first!",
                desc="Before you can submit records, you need to share your update token with the bot using "
                     "the `/token set` command. Check `/token help` for more information."
            ), ephemeral=True)

        if not (reg := re.fullmatch(r"(?P<min>[0-9]):(?P<sec>[0-9]{2}\.[0-9]{3})", time)):
            return await inter.response.send_message(embed=red_embed(
                title="⚠️ Formatting error.",
                desc="Times must be in the format: `1:23.456`"
            ), ephemeral=True)

        if len(comments) > 127:
            return await inter.response.send_message(embed=red_embed(
                title="⚠️ Comments must be 127 characters or shorter.",
                desc=f"Your comment was {len(comments)} characters long."
            ), ephemeral=True)
        elif not comments:
            comments = "N/A"

        if date:
            try:
                date_input = datetime.datetime.strptime(date, "%Y-%m-%d")
                today = datetime.datetime.now(tz=datetime.timezone.utc)
                if (date_input.date() - today.date()).days > 1:
                    return await inter.response.send_message(embed=red_embed(
                        title="⚠️ Formatting error.",
                        desc="Date cannot be in the future."
                    ), ephemeral=True)
            except ValueError:
                return await inter.response.send_message(embed=red_embed(
                    title="⚠️ Formatting error.",
                    desc="Dates must be in the format: `YYYY-MM-DD` (e.g. `2025-07-30` for July 30, 2025)"
                ), ephemeral=True)
        else:
            date = datetime.datetime.now(tz=datetime.timezone.utc).strftime("%Y-%m-%d")

        time_as_float = int(reg.group("min")) * 60 + float(reg.group("sec"))
        course = courses[course]

        try:
            auth_timestamp, auth_sig = self.get_auth_sig()
        except discord.HTTPException:
            return await inter.response.send_message(embed=could_not_connect, ephemeral=True)

        response = submit_time(course.id, time_as_float, date, token, auth_timestamp, auth_sig, comments=comments)
        if response.status_code == 200:
            print(response.text)
            try:
                try:
                    if "is slower" in response.text:
                        player = get_player(name=re.search(r"(?<=<i>).+(?=,n,)", response.text)[0], force_load=True)
                    else:
                        player = get_player(int(re.search(r"(?<=pid=)[0-9]+", response.text)[0]), force_load=True)
                except TypeError:  # if the response text looks nonstandard
                    player = None
                if not player:
                    return await inter.response.send_message(embed=green_embed(
                        title="✅ Record updated!",
                        desc=f"Submitted a time of `{time}` on [{course.game_and_name}]({course.url})." +
                             (f"\n> {comments}" if comments != "N/A" else "")
                    ))
                record = player.timesheet(force_reload=True)[course.id]
            except discord.HTTPException:
                return await inter.response.send_message(embed=green_embed(
                    title="✅ Record updated!",
                    desc=f"Submitted a time of `{time}` on [{course.game_and_name}]({course.url})." +
                         (f"\n> {comments}" if comments != "N/A" else "")
                ))

            if record.previous_time:
                delta = (f" | `{'-' if record.previous_time >= record.time else '+'}"
                         f"{prettify_seconds(record.previous_time - record.time)}s`")
            else:
                delta = ""

            return await inter.response.send_message(embed=green_embed(
                title="✅ Record updated!",
                desc=f"Submitted a time of `{time}` ({ordinal(record.rank)}{rank_emoji(record.rank)}{delta}) on "
                     f"[{course.game_and_name}]({course.url})." +
                     (f"\n> {comments}" if comments != "N/A" else ""),
                url=player.profile
            ))
        else:
            return await inter.response.send_message(embed=red_embed(
                title="⚠️ Something went wrong.",
                desc=f"The bot encountered an error in submitting your time.\n"
                     f"`{response.status_code} {response.text}`"
            ), ephemeral=True)


async def setup(bot: Bot):
    await bot.add_cog(SubmitCog(bot))
