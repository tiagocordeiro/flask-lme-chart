#!/usr/bin/env python3
# coding: utf-8

import os
from urllib import parse

from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData, Table, Column, DateTime, Float

load_dotenv()


def create_database():
    parse.uses_netloc.append("postgres")
    url = parse.urlparse(os.environ["DATABASE_URL"])

    engine = create_engine(
        'postgresql+psycopg2://' + url.username + ':' + url.password + '@' + url.hostname + '/' + url.path[1:])

    meta = MetaData()

    cotacao_lme = Table(
        'cotacao_lme', meta,
        Column('Date', DateTime(timezone=False)),
        Column('Cobre', Float),
        Column('Zinco', Float),
        Column('Aluminio', Float),
        Column('Chumbo', Float),
        Column('Estanho', Float),
        Column('Niquel', Float),
        Column('Dolar', Float),
    )

    meta.create_all(engine)

    print(f'Tabela {cotacao_lme} criada')


if __name__ == '__main__':
    create_database()
