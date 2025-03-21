from aiogram import Router, Bot, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from config_data.config import Config, load_config
from database import requests as rq
from database.models import User, Combination
from utils.error_handling import error_handler
from keyboards.start_keyboard import keyboard_start
from filter.admin_filter import check_super_admin

import logging

router = Router()
config: Config = load_config()
router.message.filter(F.chat.type == "private")


@router.message(CommandStart())
@error_handler
async def process_start_command_user(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Обработки запуска бота или ввода команды /start
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_start_command_user: {message.chat.id}')
    await state.set_state(state=None)
    # добавление пользователя в БД если еще его там нет
    user: User = await rq.get_user_by_id(tg_id=message.from_user.id)
    if not user:
        if message.from_user.username:
            username = message.from_user.username
        else:
            username = "user_name"
        data_user = {"tg_id": message.from_user.id,
                     "name": username}
        if await check_super_admin(telegram_id=message.from_user.id):
            data_user = {"tg_id": message.from_user.id,
                         "name": username,
                         "role": rq.UserRole.admin}
        await rq.add_user(data=data_user)
    await message.answer(text='Благодарим Вас, что выбрали нас 🥰\n'
                              'Для продолжения введи кодовое слово…')


@router.message(F.text == 'Сила сочетаний')
@error_handler
async def process_get_key_word(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Обработки ключевого слова
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_get_key_word: {message.chat.id}')
    await message.answer(text=f'Записали на подкорке, приступаем к разборам⚡')
    await message.answer(text='В данном боте представлены сочетания для всех арканов, в перевернутом'
                              ' и прямом значении. Отправьте сообщение с наименованием двух карт по примеру:'
                              ' “Шут + Сила”, “Императрица + Мир” и т.д.\n'
                              'P.S. Все сочетания являются базовыми/основными, при раскладе нужно прислушиваться'
                              ' к интуиции и приобщать к своей ситуации и вопросам.')
    await rq.set_user_active(tg_id=message.from_user.id)


@router.message(F.text)
@error_handler
async def process_get_combination(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Получаем запрос
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_get_combination: {message.chat.id}')
    user: User = await rq.get_user_by_id(tg_id=message.from_user.id)
    if user.active == 'true':
        combinations: list[Combination] = await rq.get_cards()
        for combination in combinations:
            if combination.combination.lower() == message.text.lower():
                await message.answer_photo(photo=combination.photo_id,
                                           caption=f'<b>{combination.combination}</b>\n'
                                                   f'{combination.description}')
    else:
        await message.answer(text='Для доступа к функционалу бота, пришлите кодовое слово.')
