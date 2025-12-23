import discord


def hex_color(hex_code: str):
    return discord.Colour(int(hex_code, 16))


def construct_embed(**kwargs) -> discord.Embed:
    ret = discord.Embed(
        title=kwargs.get("title"),
        description=kwargs.get("desc"),
        color=kwargs.get("color"),
        url=kwargs.get("url")
    )
    ret.set_thumbnail(url=kwargs.get("thumb"))
    ret.set_footer(text=kwargs.get("footer"))
    return ret


def red_embed(**kwargs) -> discord.Embed:
    return construct_embed(color=hex_color("FD3017"), **kwargs)


def green_embed(**kwargs) -> discord.Embed:
    return construct_embed(color=hex_color("5CE072"), **kwargs)


def blue_embed(**kwargs) -> discord.Embed:
    return construct_embed(color=hex_color("4FCCFB"), **kwargs)


could_not_connect = red_embed(
    title="⚠️ Something went wrong.",
    desc="The bot could not connect to the Players' Page. Try again in a few minutes."
)
