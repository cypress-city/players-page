import discord


class SingleUserView(discord.ui.View):
    def __init__(self, user: discord.User):
        super().__init__(timeout=60)
        self.user = user

    async def interaction_check(self, inter: discord.Interaction, /) -> bool:
        if inter.user == self.user:
            return True
        await inter.response.send_message("You can't control someone else's menu.", ephemeral=True)
        return False


class Confirm(SingleUserView):
    def __init__(self, user: discord.User):
        super().__init__(user)
        self.value = None

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, inter: discord.Interaction, button: discord.ui.Button):
        await inter.response.defer()
        self.value = True
        self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.gray)
    async def cancel(self, inter: discord.Interaction, button: discord.ui.Button):
        await inter.response.defer()
        self.value = False
        self.stop()


class ConfirmDelete(SingleUserView):
    def __init__(self, user: discord.User):
        super().__init__(user)
        self.value = None

    @discord.ui.button(label='Delete', style=discord.ButtonStyle.red)
    async def confirm(self, inter: discord.Interaction, button: discord.ui.Button):
        await inter.response.defer()
        self.value = True
        self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.gray)
    async def cancel(self, inter: discord.Interaction, button: discord.ui.Button):
        await inter.response.defer()
        self.value = False
        self.stop()


class PageNavigator(SingleUserView):
    def __init__(self, user: discord.User, max_pages: int, starting_page: int = 1):
        super().__init__(user)
        self.max_pages = max_pages
        self.page = starting_page

    @discord.ui.button(label='<<', style=discord.ButtonStyle.blurple)
    async def to_top(self, inter: discord.Interaction, button: discord.ui.Button):
        await inter.response.defer()
        self.page = 1
        self.stop()

    @discord.ui.button(label='<', style=discord.ButtonStyle.blurple)
    async def back_one(self, inter: discord.Interaction, button: discord.ui.Button):
        await inter.response.defer()
        self.page = max(self.page - 1, 1)
        self.stop()

    @discord.ui.button(label='>', style=discord.ButtonStyle.blurple)
    async def forward_one(self, inter: discord.Interaction, button: discord.ui.Button):
        await inter.response.defer()
        self.page = min(self.page + 1, self.max_pages)
        self.stop()

    @discord.ui.button(label='>>', style=discord.ButtonStyle.blurple)
    async def to_bottom(self, inter: discord.Interaction, button: discord.ui.Button):
        await inter.response.defer()
        self.page = self.max_pages
        self.stop()
