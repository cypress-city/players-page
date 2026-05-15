import discord


class SingleUserView(discord.ui.View):
    def __init__(self, user: discord.User):
        super().__init__(timeout=180)
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


# adapted from https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/utils/paginator.py
class GoToPage(discord.ui.Modal, title="Go to page..."):
    page = discord.ui.TextInput(label='Page', placeholder='Enter a number', min_length=1)

    def __init__(self, max_pages: int) -> None:
        super().__init__()
        as_string = str(max_pages)
        self.interaction: discord.Interaction | None = None
        self.page.placeholder = f'Enter a number between 1 and {as_string}'
        self.page.max_length = len(as_string)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        self.interaction = interaction
        self.stop()


class PageNavigator(SingleUserView):
    def __init__(self, user: discord.User, max_pages: int, starting_page: int = 1):
        super().__init__(user)
        self.max_pages = max_pages
        self.page = starting_page

    def copy(self):
        return PageNavigator(self.user, self.max_pages, self.page)

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

    # adapted from https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/utils/paginator.py
    @discord.ui.button(label='...', style=discord.ButtonStyle.grey)
    async def go_to_page(self, inter: discord.Interaction, button: discord.ui.Button):
        modal = GoToPage(self.max_pages)
        await inter.response.send_modal(modal)
        timed_out = await modal.wait()

        if timed_out:
            return await inter.followup.send("Menu timed out.", ephemeral=True)
        elif self.is_finished():
            return await modal.interaction.response.send_message("Menu timed out.", ephemeral=True)

        value = str(modal.page.value)
        if not value.isdigit():
            return await modal.interaction.response.send_message("Please enter a number.", ephemeral=True)

        value = int(value)
        self.page = max(1, min(value, self.max_pages))
        await modal.interaction.response.defer()
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


class TimesheetSorter(SingleUserView):
    def __init__(self, user: discord.User, sort: str = "cup"):
        super().__init__(user)
        self.sort = sort

    def copy(self):
        return TimesheetSorter(self.user, self.sort)

    @discord.ui.button(label='Sort by cup', style=discord.ButtonStyle.blurple)
    async def sort_by_cup(self, inter: discord.Interaction, button: discord.ui.Button):
        await inter.response.defer()
        self.sort = "cup"
        self.stop()

    @discord.ui.button(label='Sort by rank', style=discord.ButtonStyle.blurple)
    async def sort_by_rank(self, inter: discord.Interaction, button: discord.ui.Button):
        await inter.response.defer()
        self.sort = "rank"
        self.stop()
