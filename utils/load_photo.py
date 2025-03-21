import asyncio

from aiogram import Router, Bot
from aiogram.filters import Command, StateFilter, CommandObject
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config_data.config import Config, load_config
from database import requests as rq
from database.models import Combination
from utils.error_handling import error_handler
from filter.admin_filter import IsSuperAdmin

import logging
import random

router = Router()
config: Config = load_config()


class StateLoadCard(StatesGroup):
    combination = State()
    load_card = State()


@router.message(Command('load_cards'), IsSuperAdmin())
@router.message(Command('cancel'), IsSuperAdmin())
@router.message(Command('random'), IsSuperAdmin())
@router.message(Command('show_all_cards'), IsSuperAdmin())
@router.message(Command('delete_card'), IsSuperAdmin())
@error_handler
async def process_load_card(message: Message, state: FSMContext, command: CommandObject, bot: Bot) -> None:
    """
    Запуск загрузки фото
    :param message:
    :param state:
    :param command:
    :param bot:
    :return:
    """
    logging.info(f'process_load_card: {message.chat.id}')
    if message.text == '/cancel':
        await state.set_state(state=None)
        await message.answer(text='Загрузка комбинаций карт прервана')
    elif message.text == '/load_cards':
        await message.answer(text='Пришлите <b>название</b> для добавляемого сочетания карт')
        await state.set_state(StateLoadCard.combination)
    elif message.text == '/random':
        list_cards = await rq.get_cards()
        if list_cards:
            random_card: Combination = random.choice(list_cards)
            await message.answer_photo(photo=random_card.photo_id,
                                       caption=random_card.description)
        else:
            await message.answer(text='Карты не добавлены в БД')
    elif message.text == '/show_all_cards':
        list_cards = await rq.get_cards()
        if list_cards:
            for card in list_cards:
                await message.answer_photo(photo=card.photo_id,
                                           caption=f'{card.id}. <b>{card.combination}</b>\n {card.description}')
                await asyncio.sleep(0.2)
        else:
            await message.answer(text='Карты не добавлены в БД')
    elif message.text.startswith('/delete_card'):
        card_id = command.args
        if card_id and card_id.isdigit() and int(card_id) > 0:
            card = await rq.get_card(id_=int(card_id))
            if card:
                result = await rq.delete_card(id_=int(card_id))
                if result:
                    await message.answer(text=f'Карта ID {card_id} удалена из БД')
            else:
                await message.answer(text=f'Карты не c ID {card_id} не найдена в БД')
        else:
            await message.answer(text='Для применения команды удаления карты необходимо передать в параметрах'
                                      ' ID карты, например /delete_card 0 (ID карты вы можете посмотреть вызвав'
                                      ' команду /show_all_cards')


@router.message(StateFilter(StateLoadCard.combination))
@error_handler
async def get_card(message: Message, state: FSMContext, bot: Bot):
    """
    Получение название комбинации для добавления карточки
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info('get_card')
    combination = message.text
    await message.answer(text=f'Пришлите картинку с описанием к ней для добавления к комбинации {combination}')
    await state.update_data(combination=message.text)
    await state.set_state(StateLoadCard.load_card)


@router.message(StateFilter(StateLoadCard.load_card))
@error_handler
async def get_card(message: Message, state: FSMContext, bot: Bot):
    """
    Получение карточки таро для добавления в БД
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info('get_card')
    if message.photo:
        if message.caption:
            data = await state.get_data()
            combination = data['combination']
            photo_id = message.photo[-1].file_id
            caption = message.caption
            await rq.add_card(data={"combination": combination,
                                    "photo_id": photo_id,
                                    "description": caption})
            await message.answer(text='Карта добавлена в БД, пришлите название новой комбинации карт или для введите'
                                      ' /cancel')
            await state.set_state(StateLoadCard.combination)
        else:
            await message.answer(text='Комбинация должна содержать описание')
    else:
        await message.answer(text='Ждем только фото с описанием')
