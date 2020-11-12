from sqlalchemy import Integer, Column, BigInteger, String, sql

from utils.db_api.db_gino import TimedBaseModel


class User(TimedBaseModel):
    __tablename__ = 'users'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(100))
    email = Column(String(100))
    name_group = Column(String(100), nullable=True)
    mailing_time = Column(String(5), nullable=True)
    teacher = Column(String(50), nullable=True)
    referral = Column(BigInteger)

    query: sql.Select