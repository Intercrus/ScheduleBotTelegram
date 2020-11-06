from asyncpg import UniqueViolationError

from utils.db_api.db_gino import db
from utils.db_api.schemas.user import User


async def add_user(id: int, name: str, name_group: str = None, email: str = None, mailing_time: str = None):
    try:
        user = User(id=id, name=name, name_group=name_group, email=email, mailing_time=mailing_time)
        await user.create()

    except UniqueViolationError:  # Если два уникальных ключа
        pass


async def select_all_users():
    users = await User.query.gino.all()
    return users


async def select_user(id: int):
    user = await User.query.where(User.id == id).gino.first()
    return user


async def count_users():
    total = await db.func.count(User.id).gino.scalar()
    return total


async def update_user_name_group(id, name_group):
    user = await User.get(id)
    await user.update(name_group=name_group).apply()


async def delete_user_name_group(id):
    user = await User.get(id)
    await user.update(name_group=None).apply()


async def update_user_email(id, email):
    user = await User.get(id)
    await user.update(email=email).apply()


async def update_user_mailing_time(id, mailing_time):
    user = await User.get(id)
    await user.update(mailing_time=mailing_time).apply()


async def delete_user_mailing_time(id):
    user = await User.get(id)
    await user.update(mailing_time=None).apply()


async def select_all_users_for_notification(current_time):
    users = await User.query.where(User.mailing_time == current_time).gino.all()
    return users
