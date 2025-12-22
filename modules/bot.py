import discord
from discord.ext import commands
from pathlib import Path
import json
import os


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

    def add_token(self, user: discord.User, token: str):
        self.tokens[str(user.id)] = token
        self.save_tokens()

    def get_token(self, user: discord.User) -> str | None:
        return self.tokens.get(str(user.id))

    async def setup_hook(self) -> None:
        for extension in ["modules.register", "modules.submit", "modules.admin"]:
            await self.load_extension(extension)
