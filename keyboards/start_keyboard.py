from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from database.requests import UserRole
import logging


def keyboard_start(role: str) -> ReplyKeyboardMarkup:
    """
    Стартовая клавиатура для каждой роли
    :param role:
    :return:
    """
    logging.info("keyboard_start")
    keyboard = ''
    if role == UserRole.admin:
        button_1 = KeyboardButton(text='Персонал')
        button_2 = KeyboardButton(text='Опубликовать карту дня')
        button_3 = KeyboardButton(text='Ресурсы')
        keyboard = ReplyKeyboardMarkup(keyboard=[[button_1], [button_2], [button_3]],
                                       resize_keyboard=True)
    elif role == UserRole.partner:
        button_1 = KeyboardButton(text='Опубликовать карту дня')
        button_2 = KeyboardButton(text='Ресурсы')
        keyboard = ReplyKeyboardMarkup(keyboard=[[button_1], [button_2]],
                                       resize_keyboard=True)
    return keyboard

