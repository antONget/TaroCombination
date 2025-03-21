from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.models import User
import logging


def keyboard_select_action() -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора действия которое нужно совершить с ролью
    :return:
    """
    logging.info('keyboard_select_action')
    button_1 = InlineKeyboardButton(text='Назначить',
                                    callback_data='personal_add')
    button_2 = InlineKeyboardButton(text='Разжаловать',
                                    callback_data='personal_delete')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1, button_2]])
    return keyboard
