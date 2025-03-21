from aiogram import F, Router, Bot
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


import database.requests as rq
from database.models import User
from filter.admin_filter import IsSuperAdmin
from utils.error_handling import error_handler
from config_data.config import Config, load_config
from utils.utils_keyboard import utils_handler_pagination_and_select_item
from keyboards.admin.keyboards_edit_list_personal import keyboard_select_action

from uuid import uuid4
import asyncio
import logging


router = Router()
config: Config = load_config()


class Personal(StatesGroup):
    id_tg_personal = State()


# Персонал
@router.message(F.text == 'Персонал', IsSuperAdmin())
@error_handler
async def process_change_list_personal(message: Message, bot: Bot) -> None:
    """
    Выбор роли для редактирования списка
    :param message:
    :param bot:
    :return:
    """
    logging.info(f'process_change_list_personal: {message.chat.id}')
    await message.answer(text=f"Назначить или разжаловать партнера?",
                         reply_markup=keyboard_select_action())


@router.callback_query(F.data == 'personal_add')
@error_handler
async def process_personal_add(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Действие добавления пользователя в список выбранной роли
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_personal_add: {callback.message.chat.id}')
    rand_token = str(uuid4())
    token_data = {"token": rand_token,
                  "role": rq.UserRole.admin}
    await rq.add_token(data=token_data)
    await callback.message.edit_text(text=f'Для добавления пользователя в список <b>ПАРТНЕРОВ</b>, '
                                          f'отправьте ему пригласительную ссылку:\n'
                                          f'<code>https://t.me/{config.tg_bot.link_bot}?start={rand_token}'
                                          f'</code>')
    await callback.answer()


@router.callback_query(F.data == 'personal_delete')
@error_handler
async def process_del_admin(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Выбор пользователя для разжалования его из персонала
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_del_admin: {callback.message.chat.id}')
    list_users: list[User] = await rq.get_users_role(role=rq.UserRole.admin)
    if not list_users:
        await callback.answer(text=f'Нет пользователей для удаления из списка ПАРТНЕРОВ', show_alert=True)
        return
    await utils_handler_pagination_and_select_item(list_items=list_users,
                                                   text_message_pagination=f'Выберите пользователя, которого нужно'
                                                                           f' удалить из ПАРТНЕРОВ',
                                                   page=0,
                                                   count_item_page=6,
                                                   callback_prefix_select='personal_select',
                                                   callback_prefix_back='personal_back',
                                                   callback_prefix_next='personal_next',
                                                   callback=callback,
                                                   message=None)
    await callback.answer()


@router.callback_query(F.data.startswith('personal_back'))
@router.callback_query(F.data.startswith('personal_next'))
@error_handler
async def process_pagination_personal(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Пагинация по списку персоннала
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_pagination_personal: {callback.message.chat.id}')
    page = int(callback.data.split('_')[-1])
    list_users: list[User] = await rq.get_users_role(role=rq.UserRole.admin)
    await utils_handler_pagination_and_select_item(list_items=list_users,
                                                   text_message_pagination=f'Выберите пользователя, которого нужно'
                                                                           f' удалить из ПАРТНЕРОВ',
                                                   page=page,
                                                   count_item_page=6,
                                                   callback_prefix_select='personal_select',
                                                   callback_prefix_back='personal_back',
                                                   callback_prefix_next='personal_next',
                                                   callback=callback,
                                                   message=None)


@router.callback_query(F.data.startswith('personal_select'))
@error_handler
async def process_delete_personal(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Подтверждение удаления
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_delete_personal: {callback.message.chat.id}')
    user_id = int(callback.data.split('_')[-1])
    info_user: User = await rq.get_user_id(user_id)
    user_tg_id: int = info_user.tg_id
    await state.update_data(del_personal=user_tg_id)
    await rq.set_user_role(tg_id=user_tg_id, role=rq.UserRole.user)
    await callback.message.edit_text(text=f'Пользователь успешно удален из ПАРТНЕРОВ',
                                     reply_markup=None)
    await bot.send_message(chat_id=user_tg_id,
                           text=f'Вы удалены из списка ПАРТНЕРОВ',
                           reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(1)
    await process_change_list_personal(message=callback.message, bot=bot)
