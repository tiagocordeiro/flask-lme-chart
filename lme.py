#!/usr/bin/env python3
# coding: utf-8

import os
import quandl
from urllib import parse
from sqlalchemy import create_engine

quandl.ApiConfig.api_key = os.environ.get('QUANDL_KEY')

def updateDatabase():
    todo_periodo = quandl.get(["LME/PR_CU.2", "LME/PR_ZI.2", "LME/PR_AL.2",
                               "LME/PR_PB.2", "LME/PR_TN.2", "LME/PR_NI.2",
                               "CURRFX/USDBRL.1"], start_date="2012-01-03",
                              returns="pandas")

    todo_periodo.columns = ['Cobre', 'Zinco', 'Aluminio', 'Chumbo',
                            'Estanho', 'Niquel', 'Dolar']

    parse.uses_netloc.append("postgres")
    url = parse.urlparse(os.environ["DATABASE_URL"])

    engine = create_engine('postgresql+psycopg2://'+url.username+':'+url.password+'@'+url.hostname+'/'+url.path[1:])

    connection = engine.connect()

    todo_periodo.to_sql('cotacao_lme', connection, if_exists='replace')

    connection.close()


if __name__ == '__main__':
    updateDatabase()