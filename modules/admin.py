from discord.ext import commands
from modules.bot import Bot


class AdminCog(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(name="about", hidden=True)
    async def about_command(self, ctx: commands.Context):
        if ctx.author == self.bot.application.owner:
            await ctx.send(f"🏠 Servers: {len(self.bot.guilds)} | 👤 Registered users: {len(self.bot.tokens)}")

    @commands.command(name="close", aliases=["stop"], hidden=True)
    async def close_command(self, ctx: commands.Context):
        if ctx.author == self.bot.application.owner:
            await ctx.send("😴 Stopping bot.")
            await self.bot.close()

    @commands.command(name="ping", hidden=True)
    async def ping_command(self, ctx: commands.Context):
        message = await ctx.send(":ping_pong:!")
        return await message.edit(
            content=f":ping_pong:! ({round((message.created_at - ctx.message.created_at).microseconds / 1000)} ms)"
        )

    @commands.command(name="sync", hidden=True)
    async def sync_command(self, ctx: commands.Context):
        if ctx.author == self.bot.application.owner:
            await self.bot.tree.sync()
            return await ctx.send("✅ Command tree re-synced.")


async def setup(bot: Bot):
    await bot.add_cog(AdminCog(bot))
