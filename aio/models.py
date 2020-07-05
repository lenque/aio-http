# ______________________________
# 1.RAW SQL
# from sqlalchemy import create_engine
# engine = create_engine('postgresql://aiouser:password@127.0.0.1:5432/aio_db', echo=True)
#
# engine.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, name VARCHAR(30) NOT NULL, "
#                "surname VARCHAR(50) NOT NULL, patronymic VARCHAR(30) NOT NULL, gender VARCHAR(6) NOT NULL, "
#                "age numeric CHECK (age > 0))")
# engine.execute("CREATE TABLE IF NOT EXISTS cars (id SERIAL PRIMARY KEY, model VARCHAR(50) NOT NULL, "
#                "year INT NOT NULL, color VARCHAR(20) NOT NULL)")
# engine.execute("CREATE TABLE IF NOT EXISTS details (id SERIAL PRIMARY KEY, name VARCHAR(50) NOT NULL, "
#                "model VARCHAR(50) NOT NULL, price numeric CHECK (price > 0), country VARCHAR(50) NOT NULL)")


# ______________________________
# 2.SQL EXPRESSION
# str columns were generated without a length
# on SQLite and PostgreSQL, this is a valid datatype, but on others, it’s not allowed

# from sqlalchemy import (
#     create_engine, MetaData, Table, Column, Text, Integer, String, VARCHAR, ForeignKey
#     )
#
# engine = create_engine('postgresql://aiouser:password@172.17.0.1:5432/aio_db', echo=True)
# meta = MetaData()
#
# users = Table(
#     'users', meta,
#     Column('id', Integer, primary_key=True),
#     Column('name', String, nullable=False),
#     Column('surname', String, nullable=False),
#     Column('patronymic', String),
#     Column('gender', String, nullable=False),
#     Column('age', Integer),
# )
#
# cars = Table(
#     'cars', meta,
#     Column('id', Integer, primary_key=True),
#     Column('model', String, nullable=False),
#     Column('year', Integer, nullable=False),
#     Column('color', VARCHAR),
#     Column('user_id', None, ForeignKey('users.id')),
# )
#
# details = Table(
#     'details', meta,
#     Column('id', Integer, primary_key=True),
#     Column('name', String, nullable=False),
#     Column('model', String, nullable=False),
#     Column('price', Integer, nullable=False),
#     Column('country', VARCHAR),
# )
#
# meta.create_all(engine)
#
#
# def recreate_db():
#     meta.drop_all(engine)
#     meta.create_all(engine)


# ______________________________
# 3.SQL ORM
# import json
# from sqlalchemy import create_engine, Column, Integer, String, Numeric, VARCHAR
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker, relationship
#
# engine = create_engine('postgresql://aiouser:password@127.0.0.1:5432/aio_db', echo=True)
# base = declarative_base()
#
#
# class User(base):
#     __tablename__ = 'users'
#
#     id = Column(Integer, primary_key=True)
#     name = Column(String(30), nullable=False)
#     surname = Column(String(50), nullable=False)
#     patronymic = Column(String(30), nullable=False)
#     gender = Column(String(6), nullable=False)
#     age = Column(Numeric, nullable=False)
#     car = relationship("Car")
#
#     def __repr__(self):
#         return f"{self.surname} {self.name}"
#
#     def to_json(self):
#         return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=6)
#
#
# class Car(base):
#     __tablename__ = 'cars'
#
#     id = Column(Integer, primary_key=True)
#     model = Column(String(50), nullable=False)
#     year = Column(Integer, nullable=False)
#     color = Column(String(30), nullable=False)
#     user_id = Column(Integer, ForeignKey('user.id'))
#
#     def __repr__(self):
#         return f"{self.model}"
#
#
# class Detail(base):
#     __tablename__ = 'details'
#
#     id = Column(Integer, primary_key=True)
#     name = Column(String(50), nullable=False)
#     model = Column(String(50), nullable=False)
#     price = Column(Integer, nullable=False)
#     country = Column(VARCHAR, nullable=False)
#
#     def __repr__(self):
#         return f"{self.name}"
#
#
# Session = sessionmaker(engine)
# session = Session()
#
# base.metadata.create_all(engine)

# ______________________________
# 4.AIOPG

import asyncio
from aiopg.sa import create_engine
import sqlalchemy as sa
from sqlalchemy.sql.ddl import CreateTable

metadata = sa.MetaData()

users = sa.Table(
    'users', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('name', sa.String(40), nullable=False),
    sa.Column('surname', sa.String(40), nullable=False),
    sa.Column('patronymic', sa.String(40)),
    sa.Column('gender', sa.String(40), nullable=False),
    sa.Column('age', sa.Integer),
)

cars = sa.Table(
    'cars', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('model', sa.String(60), nullable=False),
    sa.Column('year', sa.Integer, nullable=False),
    sa.Column('color', sa.VARCHAR),
    sa.Column('user_id', None, sa.ForeignKey('users.id')),
)


async def create_table(conn):
    await conn.execute('DROP TABLE IF EXISTS cars')
    await conn.execute('DROP TABLE IF EXISTS users')
    await conn.execute('DROP TYPE IF EXISTS s_enum CASCADE')
    await conn.execute("CREATE TYPE s_enum AS ENUM ('f', 's')")
    await conn.execute(CreateTable(users))
    await conn.execute(CreateTable(cars))


async def go():
    async with create_engine(user='aiouser', database='aio_db', host='172.17.0.1', password='password') as engine:
        async with engine.acquire() as conn:
            await create_table(conn)
        async with engine.acquire() as conn:
            await conn.execute(users.insert().values(name='Elena', surname='Ch', patronymic='Y', gender='female'))
            await conn.execute(cars.insert().values(model='W', year=2020, color='black', user_id=1))
            async for row in conn.execute(users.select()):
                print(row.id, row.surname)

loop = asyncio.get_event_loop()
loop.run_until_complete(go())
