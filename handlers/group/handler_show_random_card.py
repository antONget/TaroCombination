from aiogram import Router, Bot, F
from aiogram.filters import StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config_data.config import Config, load_config
from database import requests as rq
from database.models import Card
from utils.error_handling import error_handler

import logging
import random

router = Router()
config: Config = load_config()


class StateLoadCard(StatesGroup):
    load_card = State()


@router.message(F.text == '/картадня')
@error_handler
async def process_load_card(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Запуск загрузки фото
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_load_card: {message.chat.id}')
    list_cards = await rq.get_cards()
    if list_cards:
        random_card: Card = random.choice(list_cards)
        await message.answer_photo(photo=random_card.photo_id,
                                   caption=random_card.description)
        # await message.delete()
