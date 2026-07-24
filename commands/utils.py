# Assorted Time Trial utilities that may be moved to a dedicated bot in the future.
import discord
from discord.ext import commands
import json
import matplotlib.pyplot as plt
import numpy as np

from modules.core import Bot, unprettify_time, prettify_time, closeness
from modules.embeds import blue_embed, red_embed
from modules.views import ComboStatBrowser

with open("data/coins.txt", "r") as f:
    COIN_CURVES = [[float(g) for g in row.split("\t")] for row in f.read().splitlines()]


def simplify_text(s: str):
    return "".join(c for c in s if c.isalnum()).lower()


def comp_display(infill: str, t1: int, t2: int):
    return f"{'🔹' if t1 > t2 else '🔸' if t2 > t1 else '▫️'} {infill} " \
        f"{'**' if t1 >= t2 else ''}{t1}{'**' if t1 >= t2 else ''}" \
        f" {'>' if t1 > t2 else '<' if t1 < t2 else '='} " \
        f"{'**' if t2 >= t1 else ''}{t2}{'**' if t2 >= t1 else ''}"


TIME_ERROR = "**⚠️ Bad input: `{input}`**\n-# Times should look like `1:23.456` or `12.345`"


class ComboPart:
    def __init__(self, name: str, type_: str, speed_smooth: int, speed_rough: int, speed_water: int,
                 acceleration: int, miniturbo: int, weight: int, coin_curve: int, invincibility: int,
                 handling_smooth: int, handling_rough: int, handling_water: int, glider: int):
        self.name = name
        self.type = type_
        self.speed_smooth = speed_smooth
        self.speed_rough = speed_rough
        self.speed_water = speed_water
        self.handling_smooth = handling_smooth
        self.handling_rough = handling_rough
        self.handling_water = handling_water
        self.weight = weight
        self.coin_curve = coin_curve
        self.glider = glider
        self.acceleration = acceleration
        self.miniturbo = miniturbo
        self.invincibility = invincibility

    def json(self) -> dict:
        return {
            "name": self.name,
            "type_": self.type,
            "speed_smooth": self.speed_smooth,
            "speed_rough": self.speed_rough,
            "speed_water": self.speed_water,
            "acceleration": self.acceleration,
            "miniturbo": self.miniturbo,
            "weight": self.weight,
            "coin_curve": self.coin_curve,
            "invincibility": self.invincibility,
            "handling_smooth": self.handling_smooth,
            "handling_rough": self.handling_rough,
            "handling_water": self.handling_water,
            "glider": self.glider
        }

    def stats_embed(self):
        return blue_embed(
            title=self.name,
            desc=f"Speed (smooth): **{self.speed_smooth}**\n"
                 f"Speed (rough): **{self.speed_rough}**\n"
                 f"Speed (water): **{self.speed_water}**\n\n"
                 f"Handling (smooth): **{self.handling_smooth}**\n"
                 f"Handling (rough): **{self.handling_rough}**\n"
                 f"Handling (water): **{self.handling_water}**\n\n"
                 f"Coin curve: **{self.coin_curve}**\n"
                 f"Acceleration: **{self.acceleration}**\n"
                 f"Mini-turbo: **{self.miniturbo}**\n"
                 f"Weight: **{self.weight}**\n"
                 f"Invincibility: **{self.invincibility}**\n"
                 f"Gliding: **{self.glider}**"
        )

    def compare_embed(self, other):
        assert isinstance(other, ComboPart)
        return blue_embed(
            title=f"🔹 {self.name} vs. 🔸 {other.name}",
            desc=f"{comp_display('Speed (smooth):', self.speed_smooth, other.speed_smooth)}\n"
                 f"{comp_display('Speed (rough):', self.speed_rough, other.speed_rough)}\n"
                 f"{comp_display('Speed (water):', self.speed_water, other.speed_water)}\n\n"
                 f"{comp_display('Handling (smooth):', self.handling_smooth, other.handling_smooth)}\n"
                 f"{comp_display('Handling (rough):', self.handling_rough, other.handling_rough)}\n"
                 f"{comp_display('Handling (water):', self.handling_water, other.handling_water)}\n\n"
                 f"{comp_display('Coin curve:', self.coin_curve, other.coin_curve)}\n"
                 f"{comp_display('Acceleration:', self.acceleration, other.acceleration)}\n"
                 f"{comp_display('Mini-turbo:', self.miniturbo, other.miniturbo)}\n"
                 f"{comp_display('Weight:', self.weight, other.weight)}\n"
                 f"{comp_display('Invincibility:', self.invincibility, other.invincibility)}\n"
                 f"{comp_display('Gliding:', self.glider, other.glider)}"
        )

    @property
    def coin_speeds(self):
        return COIN_CURVES[self.coin_curve]

    def coin_graph(self, comparison = None):
        fig, ax = plt.subplots()

        ax.xaxis.set_major_locator(plt.MultipleLocator(2))
        ax.xaxis.set_minor_locator(plt.MultipleLocator(1))
        ax.xaxis.grid(True, which="major", linestyle=":")
        ax.set_xlabel("Coins")

        ax.yaxis.set_minor_locator(plt.MultipleLocator(0.5))
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{int(v)}%"))
        ax.yaxis.grid(True, which="major", linestyle="-")
        ax.yaxis.grid(True, which="minor", linestyle=":")
        ax.set_ylabel("Speed increase")

        ax.plot(range(0, 21), self.coin_speeds, marker="o", markerfacecolor="white",
                color="royalblue", label=self.name)

        if comparison:
            ax.plot(range(0, 21), comparison.coin_speeds, marker="^", markerfacecolor="white",
                    color="crimson", label=comparison.name)
            ax.set_title(f"Coin Curve\n{self.name} vs. {comparison.name}")
            ax.legend(loc="upper left")
            img_name = f"images/{simplify_text(self.name)}-{simplify_text(comparison.name)}-coins.png"
        else:
            ax.set_title(f"Coin Curve\n{self.name}")
            img_name = f"images/{simplify_text(self.name)}-coins.png"

        plt.savefig(img_name, dpi=200)
        plt.close()
        return img_name
    
    @property
    def coin_speeds_smooth(self):
        return [(100 + 0.312 * self.speed_smooth) * (1 + g / 100) for g in self.coin_speeds]

    @property
    def coin_speeds_rough(self):
        return [(100 + 0.312 * self.speed_rough) * (1 + g / 100) for g in self.coin_speeds]

    @property
    def coin_speeds_water(self):
        return [(100 + 0.312 * self.speed_water) * (1 + g / 100) for g in self.coin_speeds]

    def speed_graph(self, comparison = None):
        fig, ax = plt.subplots()

        ax.xaxis.set_major_locator(plt.MultipleLocator(2))
        ax.xaxis.set_minor_locator(plt.MultipleLocator(1))
        ax.xaxis.grid(True, which="major", linestyle=":")
        ax.set_xlabel("Coins")

        ax.yaxis.set_major_locator(plt.MultipleLocator(2))
        ax.yaxis.set_minor_locator(plt.MultipleLocator(1))
        ax.yaxis.grid(True, which="major", linestyle="-")
        ax.yaxis.grid(True, which="minor", linestyle=":")
        ax.set_ylim(99, 111)
        ax.set_ylabel("Speed")

        label_prefix = f"Combo 1 - " if comparison else ""
        ax.plot(range(0, 21), self.coin_speeds_smooth, marker="o", markerfacecolor="white", linestyle="-",
                color="dimgrey", label=f"{label_prefix}Smooth")
        ax.plot(range(0, 21), self.coin_speeds_rough, marker="o", markerfacecolor="white", linestyle="--",
                color="peru", label=f"{label_prefix}Rough")
        ax.plot(range(0, 21), self.coin_speeds_water, marker="o", markerfacecolor="white", linestyle=":",
                color="cornflowerblue", label=f"{label_prefix}Water")

        if comparison:
            ax.plot(range(0, 21), comparison.coin_speeds_smooth, marker="^", markerfacecolor="white", linestyle="-",
                    color="black", label=f"Combo 2 - Smooth")
            ax.plot(range(0, 21), comparison.coin_speeds_rough, marker="^", markerfacecolor="white", linestyle="--",
                    color="firebrick", label=f"Combo 2 - Rough")
            ax.plot(range(0, 21), comparison.coin_speeds_water, marker="^", markerfacecolor="white", linestyle=":",
                    color="slateblue", label=f"Combo 2 - Water")
            ax.set_title(f"Terrain Speeds\n{self.name} vs. {comparison.name}", wrap=True)
            img_name = f"images/{simplify_text(self.name)}-{simplify_text(comparison.name)}-speeds.png"
        else:
            ax.set_title(f"Terrain Speeds\n{self.name}", wrap=True)
            img_name = f"images/{simplify_text(self.name)}-speeds.png"

        ax.legend(loc="upper left")
        plt.savefig(img_name, dpi=200)
        plt.close()
        return img_name


with open("data/characters.json", "r") as f:
    CHARACTERS = {g: ComboPart(name=g, type_="character", **j) for g, j in json.load(f).items()}


with open("data/karts.json", "r") as f:
    KARTS = {g: ComboPart(name=g, type_="kart", **j) for g, j in json.load(f).items()}


_stat_types = [g for g, j in CHARACTERS["Baby Peach"].json().items() if isinstance(j, int)]
max_stats = {
    g: max(c.json()[g] for c in CHARACTERS.values()) + max(c.json()[g] for c in KARTS.values()) for g in _stat_types
}


async def character_autocomplete(inter: discord.Interaction, current: str) -> list[discord.app_commands.Choice[str]]:
    matches = sorted(
        [g for g in CHARACTERS if closeness(simplify_text(current), simplify_text(g))],
        key=lambda c: -closeness(simplify_text(current), simplify_text(c))
    )
    return [discord.app_commands.Choice(name=g, value=g) for g in matches][:25]


async def kart_autocomplete(inter: discord.Interaction, current: str) -> list[discord.app_commands.Choice[str]]:
    matches = sorted(
        [g for g in KARTS if closeness(simplify_text(current), simplify_text(g))],
        key=lambda c: -closeness(simplify_text(current), simplify_text(c))
    )
    return [discord.app_commands.Choice(name=g, value=g) for g in matches][:25]


class Combo(ComboPart):
    def __init__(self, character: ComboPart, kart: ComboPart):
        stats = {g: j + kart.json()[g] for g, j in character.json().items() if isinstance(j, int)}
        super().__init__(type_="combo", name=f"{character.name} + {kart.name}", **stats)
        self.character = character
        self.kart = kart

    @staticmethod
    def partial(character: ComboPart | None, kart: ComboPart | None):
        if character is None and kart is not None:
            return kart
        if kart is None and character is not None:
            return character
        return Combo(character, kart)


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

    group = discord.app_commands.Group(name="combo", description="Character + kart stats.")

    @group.command(
        name="stats",
        description="View character + kart stats."
    )
    @discord.app_commands.autocomplete(character=character_autocomplete, kart=kart_autocomplete)
    @discord.app_commands.describe(character="Character name", kart="Vehicle name")
    async def combo_stats(self, inter: discord.Interaction, character: str = None, kart: str = None):
        if character is not None and character not in CHARACTERS:
            return await inter.response.send_message(
                embed=red_embed(title="⚠️ Please enter a valid character name."), ephemeral=True
            )
        if kart is not None and kart not in KARTS:
            return await inter.response.send_message(
                embed=red_embed(title="⚠️ Please enter a valid vehicle name."), ephemeral=True
            )
        if character is None and kart is None:
            return await inter.response.send_message(
                embed=red_embed(title="⚠️ You must enter either a character or vehicle."), ephemeral=True
            )

        combo = Combo.partial(CHARACTERS.get(character), KARTS.get(kart))
        coin_graph = combo.coin_graph()
        speed_graph = combo.speed_graph()

        if combo.type == "combo":
            view = ComboStatBrowser(inter.user)
            await inter.response.send_message(embed=combo.stats_embed(), view=view)
            while not await view.wait():
                view = view.copy()
                if view.mode == "stats":
                    await inter.edit_original_response(embed=combo.stats_embed(), attachments=[], view=view)
                elif view.mode == "coins":
                    await inter.edit_original_response(embed=None, attachments=[discord.File(coin_graph)], view=view)
                elif view.mode == "speeds":
                    await inter.edit_original_response(embed=None, attachments=[discord.File(speed_graph)], view=view)
            return await inter.edit_original_response(view=None)
        else:
            return await inter.response.send_message(embed=combo.stats_embed())

    @group.command(
        name="compare",
        description="Compare character + kart stats."
    )
    @discord.app_commands.autocomplete(
        character1=character_autocomplete, character2=character_autocomplete,
        kart1=kart_autocomplete, kart2=kart_autocomplete)
    @discord.app_commands.describe(
        character1="Character name", character2="Character name",
        kart1="Vehicle name", kart2="Vehicle name"
    )
    async def combo_compare(self, inter: discord.Interaction, character1: str, kart1: str, character2: str, kart2: str):
        if character1 not in CHARACTERS or character2 not in CHARACTERS:
            return await inter.response.send_message(
                embed=red_embed(title="⚠️ Please enter a valid character name."), ephemeral=True
            )
        if kart1 not in KARTS or kart2 not in KARTS:
            return await inter.response.send_message(
                embed=red_embed(title="⚠️ Please enter a valid vehicle name."), ephemeral=True
            )

        combo1 = Combo(CHARACTERS[character1], KARTS[kart1])
        combo2 = Combo(CHARACTERS[character2], KARTS[kart2])
        coin_graph = combo1.coin_graph(combo2)
        speed_graph = combo1.speed_graph(combo2)

        view = ComboStatBrowser(inter.user)
        await inter.response.send_message(embed=combo1.compare_embed(combo2), view=view)
        while not await view.wait():
            view = view.copy()
            if view.mode == "stats":
                await inter.edit_original_response(embed=combo1.compare_embed(combo2), attachments=[], view=view)
            elif view.mode == "coins":
                await inter.edit_original_response(embed=None, attachments=[discord.File(coin_graph)], view=view)
            elif view.mode == "speeds":
                await inter.edit_original_response(embed=None, attachments=[discord.File(speed_graph)], view=view)
        return await inter.edit_original_response(view=None)


async def setup(bot: Bot):
    await bot.add_cog(UtilsCog(bot))
