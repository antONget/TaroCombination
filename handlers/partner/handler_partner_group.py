from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import StateFilter
from aiogram.enums.chat_member_status import ChatMemberStatus
from aiogram.exceptions import TelegramBadRequest

from utils.error_handling import error_handler
from utils.utils_keyboard import utils_handler_pagination_and_select_item
from database import requests as rq
from keyboards.partner import partner_group_keyboards as kb
from filter.user_filter import IsRoleAdmin
from config_data.config import Config, load_config

import logging

config: Config = load_config()
router = Router()
router.message.filter(F.chat.type == "private")


class Partner(StatesGroup):
    group_id = State()
    group_name = State()


@router.message(F.text == 'Ресурсы', IsRoleAdmin())
@error_handler
async def change_list_my_groups(message: Message, bot: Bot) -> None:
    """
    Работа со списком ресурсов
    :param message:
    :param bot:
    :return:
    """
    logging.info('change_list_my_groups')
    await message.answer(text='Выберите действие, которое нужно выполнить со списком ресурсов для публикации карты дня',
                         reply_markup=kb.keyboard_change_list_group())


@router.callback_query(F.data.startswith('group_'))
@error_handler
async def select_change_group(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Изменяем список групп
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info('select_change_group')
    select = callback.data.split('_')[-1]
    if select == 'add':
        await callback.message.edit_text(text='Пришлите id группы, обязательно добавьте бота в качестве'
                                              ' администратора (Чтобы получить ID чата добавьте бота @FIND_MY_ID_BOT'
                                              ' в чат и напишите в команду /id@FIND_MY_ID_BOT или воспользуйтесь '
                                              'ботом @username_to_id_bot',
                                         reply_markup=None)
        await state.set_state(Partner.group_id)
        await callback.answer()
        return
    elif select == 'del':
        print('del')
        list_group = await rq.get_group_partner(tg_id_partner=callback.from_user.id)
        if list_group:
            await utils_handler_pagination_and_select_item(list_items=list_group,
                                                           text_message_pagination=
                                                           'Выберите ресурс для удаления из БД бота',
                                                           page=0,
                                                           count_item_page=6,
                                                           callback_prefix_select='group_select',
                                                           callback_prefix_back='group_back',
                                                           callback_prefix_next='group_next',
                                                           callback=callback,
                                                           message=None)
        else:
            await callback.answer(text='В БД нет добавленных вами групп', show_alert=True)
        await callback.answer()


@router.message(F.text, StateFilter(Partner.group_id))
@error_handler
async def process_get_group(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Добавление группы партнера
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_get_group: {message.from_user.id}')
    if message.text in ['Тарифы', 'Мои группы', 'Партнеры']:
        await state.set_state(state=None)
        await message.answer(text='Добавление группы отменено')
        return

    try:
        group_id = int(message.text)
    except:
        await message.answer(text='ID чата должно быть целым числом '
                                  '(Чтобы получить ID чата добавьте бота @FIND_MY_ID_BOT в чат и напишите в команду'
                                  ' /id@FIND_MY_ID_BOT')
        return
    try:
        bot = await bot.get_chat_member(group_id, bot.id)
        if bot.status == ChatMemberStatus.ADMINISTRATOR:
            await message.answer(text='Отлично! Бот уже состоит в администраторах группы')
        else:
            await message.answer(text='Бот не добавлен администратором в группу, обязательно добавьте'
                                      ' бота администратором'
                                      ' в группу иначе он не сможет публиковать в нее посты')
        await message.answer(text='Пришлите наименование группы (до 32 символов):')
        await state.update_data(group_id=group_id)
        await state.set_state(Partner.group_name)
    except TelegramBadRequest:
        await message.answer(text='Бот не нашел такого чата, добавьте бота в чат, для того чтобы он мог публиковать'
                                  ' посты боту требуется права администратора.'
                                  ' Проверьте права бота в группе и повторите добавления')


@router.message(F.text, StateFilter(Partner.group_name))
@error_handler
async def process_get_group_name(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Добавление/удаление менеджера по username
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_get_group_name: {message.from_user.id}')
    group_name = message.text
    if group_name in ['Опубликовать пост', 'Менеджеры', 'Мои группы', 'Партнеры']:
        await message.answer(text='Добавление группы отменено')
        await state.set_state(state=None)
        return
    if len(group_name) <= 32:
        data = await state.get_data()
        group_id = data['group_id']
        data_add = {'tg_id_partner': message.from_user.id, 'group_id': group_id, 'name': group_name}
        await rq.add_group(group_id=group_id, data=data_add)
        await message.answer(text='Группа успешно добавлена')
        await state.set_state(state=None)
    else:
        await message.answer(text='Название канала не должно превышать 32 символа')


@router.callback_query(F.data.startswith('group_back'))
@router.callback_query(F.data.startswith('group_next'))
@error_handler
async def process_forward_group(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Пагинация вперед
    :param callback: int(callback.data.split('_')[1]) номер блока для вывода
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_forward_group: {callback.from_user.id}')
    list_group = await rq.get_group_partner(tg_id_partner=callback.from_user.id)
    await utils_handler_pagination_and_select_item(list_items=list_group,
                                                   text_message_pagination=
                                                   'Выберите ресурс для удаления из БД бота',
                                                   page=0,
                                                   count_item_page=6,
                                                   callback_prefix_select='group_select',
                                                   callback_prefix_back='group_back',
                                                   callback_prefix_next='group_next',
                                                   callback=callback,
                                                   message=None)
    await callback.answer()


@router.callback_query(F.data.startswith('group_select'))
@error_handler
async def process_select_group(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Удаление выбранной группы из БД
    :param callback: int(callback.data.split('_')[1]) номер блока для вывода
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_select_group: {callback.from_user.id}')
    await state.set_state(state=None)
    id_group = int(callback.data.split('_')[-1])
    await rq.delete_group(id_=id_group)
    await callback.message.answer(text='Группа успешно удалена',
                                  reply_markup=None)
    await callback.answer()



