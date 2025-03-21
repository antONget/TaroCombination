from database.models import User, Combination, async_session
from sqlalchemy import select
from dataclasses import dataclass
import logging


""" USER """


@dataclass
class UserRole:
    user = "user"
    admin = "admin"
    partner = "partner"


async def add_user(data: dict) -> None:
    """
    Добавление пользователя
    :param data:
    :return:
    """
    logging.info(f'add_user')
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == data['tg_id']))
        if not user:
            session.add(User(**data))
            await session.commit()
        else:
            user.username = data['username']
            await session.commit()


async def get_user_by_id(tg_id: int) -> User:
    """
    Получение информации о пользователе по tg_id
    :param tg_id:
    :return:
    """
    logging.info(f'get_user_by_id {tg_id}')
    async with async_session() as session:
        return await session.scalar(select(User).where(User.tg_id == tg_id))


async def get_user_id(id_: int) -> User:
    """
    Получение информации о пользователе id
    :param id_:
    :return:
    """
    logging.info(f'get_user_id {id_}')
    async with async_session() as session:
        return await session.scalar(select(User).where(User.id == id_))


async def set_user_role(tg_id: int, role: str) -> None:
    """
    Обновление роли пользователя
    :param tg_id:
    :param role:
    :return:
    """
    logging.info('set_user_phone')
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            user.role = role
            await session.commit()


async def set_user_active(tg_id: int) -> None:
    """
    Обновление доступа к боту
    :param tg_id:
    :return:
    """
    logging.info('set_user_phone')
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            user.active = 'true'
            await session.commit()


async def get_users_role(role: str):
    """
    Получение списка пользователей с заданной ролью
    :param role:
    :return:
    """
    logging.info('get_users_role')
    async with async_session() as session:
        users = await session.scalars(select(User).where(User.role == role))
        list_users = [user for user in users]
        return list_users


""" COMBINATION """


async def add_card(data: dict) -> None:
    """
    Добавление токена
    :param data:
    :return:
    """
    logging.info(f'add_token')
    async with async_session() as session:
        new_card = Combination(**data)
        session.add(new_card)
        await session.commit()


async def get_card(id_: int) -> Combination:
    """
    Получение карты таро по id
    :param id_:
    :return:
    """
    logging.info('get_token')
    async with async_session() as session:
        return await session.scalar(select(Combination).filter(Combination.id == id_))


async def get_cards():
    """
    Получение списка карт таро
    :return:
    """
    logging.info('get_token')
    async with async_session() as session:
        cards = await session.scalars(select(Combination))
        return [card for card in cards]


async def delete_card(id_: int) -> bool:
    """
    Удаленеи карты таро по id
    :param id_:
    :return:
    """
    logging.info('get_token')
    async with async_session() as session:
        card = await session.scalar(select(Combination).where(Combination.id == id_))
        if card:
            await session.delete(card)
            await session.commit()
            return True
