import re
from typing import Awaitable, Callable, List, Optional, Union

import discord

from ..breadcrumbs import Breadcrumbs
from ..dispatch import Dispatch
from ...db.entity import Entity


# See https://github.com/Rapptz/discord.py/blob/master/examples/views/dropdown.py
class EntityDropdown(discord.ui.Select):
    def __init__(self, entities: List[Entity], start_index: int, dispatch: Dispatch):
        self.__dispatch = dispatch
        # print(f"Constructing EntityDropdown with start index {start_index}")
        options = self._get_options(entities, start_index)
        super().__init__(
            placeholder="Select one",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="multi_dropdown"
        )

    async def callback(self, interaction: discord.Interaction):
        breadcrumbs = Breadcrumbs.extract(interaction.message.content)
        selection_option = self.values[0]
        query = selection_option
        breadcrumbs.add_page(Breadcrumbs.Page(query))
        await self.__dispatch.query_and_replace(breadcrumbs, interaction)

    @staticmethod
    def _get_options(entities: List[Entity], start: int) -> list[discord.SelectOption]:
        options = []
        end = len(entities)
        if end > 25:
            end = start + 25
        for i in range(start, end):
            entity = entities[i]
            options.append(discord.SelectOption(label=entity.var(), description=entity.human_readable_name()))
        return options

    async def update_options(self, interaction: discord.Interaction, start: int):
        breadcrumbs = Breadcrumbs.extract(interaction.message.content)
        breadcrumbs.current_page().set_single_custom_id(str(start))
        await self.__dispatch.query_and_replace(breadcrumbs, interaction)


class ButtonWithCallback(discord.ui.Button):
    def __init__(
            self,
            *,
            style: discord.ButtonStyle = discord.ButtonStyle.secondary,
            label: Optional[str] = None,
            disabled: bool = False,
            custom_id: Optional[str] = None,
            url: Optional[str] = None,
            emoji: Optional[Union[str, discord.Emoji, discord.PartialEmoji]] = None,
            row: Optional[int] = None,
            callback: Callable[[discord.Interaction], Awaitable[None]],
    ):
        super().__init__(
            style=style,
            label=label,
            disabled=disabled,
            custom_id=custom_id,
            url=url,
            emoji=emoji,
            row=row
        )
        self.__callback = callback

    async def callback(self, interaction: discord.Interaction):
        await self.__callback(interaction)


class MultiEntityView(discord.ui.View):
    def __init__(self, entities: List[Entity], start_index: int, dispatch: Dispatch):
        super().__init__(timeout=None)

        self.__dropdown = EntityDropdown(entities, start_index, dispatch)

        num_entities = len(entities)

        self.__previous_button = ButtonWithCallback(
            label="Previous",
            style=discord.ButtonStyle.grey,
            emoji="⬅",
            disabled=start_index <= 0,
            callback=self._previous,
            custom_id="multi_previous",
        )
        self.__num_button = discord.ui.Button(
            label=self._get_num_label(start_index, num_entities),
            style=discord.ButtonStyle.grey,
            disabled=True,
            custom_id="multi_num",
        )
        self.__next_button = ButtonWithCallback(
            label="Next",
            style=discord.ButtonStyle.grey,
            emoji="➡",
            disabled=start_index > num_entities - 25,
            callback=self._next,
            custom_id="multi_next",
        )
        self.add_item(self.__previous_button)
        self.add_item(self.__num_button)
        self.add_item(self.__next_button)

        # Adds the dropdown to our view object.
        self.add_item(self.__dropdown)

    async def _previous(self, interaction: discord.Interaction):
        start_index = self._get_start_index()
        start_index -= 25
        if start_index <= 0:
            start_index = 0
        await self._update_buttons(interaction, start_index)

    async def _next(self, interaction: discord.Interaction):
        num_entities = self._get_num_entities()
        start_index = self._get_start_index()
        start_index += 25
        if start_index + 25 >= num_entities:
            start_index = num_entities - 25
        await self._update_buttons(interaction, start_index)

    async def _update_buttons(self, interaction: discord.Interaction, start_index):
        num_entities = self._get_num_entities()
        self.__previous_button.disabled = start_index <= 0
        self.__next_button.disabled = start_index > num_entities - 25
        self.__num_button.label = self._get_num_label(start_index, num_entities)
        await self.__dropdown.update_options(interaction, start_index)

    @staticmethod
    def _get_num_label(start_index: int, num_entities: int):
        start = start_index + 1
        end = start_index + 25
        if end > num_entities:
            end = num_entities
        return f"Showing {start} - {end} out of {num_entities} matches"

    def _get_num_entities(self):
        return int(re.findall(r'\d+', self.__num_button.label)[-1])

    def _get_start_index(self):
        return int(re.findall(r'\d+', self.__num_button.label)[0])
