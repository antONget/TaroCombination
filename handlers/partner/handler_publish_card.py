from aiogram import Router, Bot, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config_data.config import Config, load_config
from database import requests as rq
from database.models import Card, Group
from utils.error_handling import error_handler
from filter.user_filter import IsRoleAdmin

import logging
import random

router = Router()
config: Config = load_config()


class StateLoadCard(StatesGroup):
    load_card = State()


@router.message(F.text == 'Опубликовать карту дня', IsRoleAdmin())
@error_handler
async def process_publish_card(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Публикация карты дня в добавленных ресурсах
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_publish_card: {message.chat.id}')
    list_cards = await rq.get_cards()
    if list_cards:
        random_card: Card = random.choice(list_cards)
        list_groups: list[Group] = await rq.get_group_partner(tg_id_partner=message.from_user.id)
        if list_groups:
            for group in list_groups:
                try:
                    await bot.send_photo(chat_id=group.group_id,
                                         photo=random_card.photo_id,
                                         caption=random_card.description)
                    await message.answer(text=f'Карта дня опубликована в {group.name}')
                except:
                    pass
        else:
            await message.answer(text='У вас нет добавленных ресурсов для публикации карты дня')
    else:
        await message.answer(text='Карт для публикации нет')
