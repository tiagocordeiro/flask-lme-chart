import os
from datetime import datetime, timedelta
from urllib import parse

import pandas as pd
import psycopg2
from bs4 import BeautifulSoup
from flask import Flask, render_template, jsonify

pd.options.display.float_format = '{:,.2f}'.format
pd.set_option('colheader_justify', 'right')


def create_app():
    application = Flask(__name__)

    @application.route('/')
    def index(chartID='chart_ID', chart_type='line', chart_height=350):
        qt_semanas = 4
        periodo_cotacao = periodo_data()
        hoje = periodo_cotacao['fim']
        periodo = periodo_cotacao['inicio']

        parse.uses_netloc.append("postgres")
        url = parse.urlparse(os.environ["DATABASE_URL"])

        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )

        # cotacaoatual = pd.read_sql("SELECT * FROM cotacao_lme")

        query = """
                SELECT *
                FROM cotacao_lme
                WHERE "Date" BETWEEN %(inicio)s AND %(fim)s
                """

        query_params = {'inicio': periodo, 'fim': hoje}

        cotacaoatual = pd.read_sql(query, conn, params=query_params)

        cotacaoatual.columns = ['Data', 'Cobre', 'Zinco', 'Aluminio', 'Chumbo',
                                'Estanho', 'Niquel', 'Dolar']

        df = pd.DataFrame(cotacaoatual)

        df['Data'] = pd.to_datetime(df['Data'], utc=True)

        df = df.set_index(df['Data'])

        df = df.drop('Data', axis=1)

        df.fillna(method='ffill', inplace=True)
        df.fillna(method='bfill', inplace=True)

        cobre = list(df['Cobre'])
        zinco = list(df['Zinco'])
        aluminio = list(df['Aluminio'])
        chumbo = list(df['Chumbo'])
        estanho = list(df['Estanho'])
        niquel = list(df['Niquel'])
        dolar = list(df['Dolar'])
        data = list(df.index.strftime('%d/%m/%y'))

        chart = {"renderTo": chartID, "type": chart_type,
                 "height": chart_height}
        series = [{"name": 'Cobre', "data": cobre},
                  {"name": 'Zinco', "data": zinco, "visible": 'false'},
                  {"name": 'Alumínio', "data": aluminio, "visible": 'false'},
                  {"name": 'Chumbo', "data": chumbo, "visible": 'false'},
                  {"name": 'Estanho', "data": estanho, "visible": 'false'},
                  {"name": 'Níquel', "data": niquel, "visible": 'false'},
                  {"name": 'Dolar', "data": dolar, "visible": 'false'}
                  ]
        title = {"text": 'Cotação LME'}
        xAxis = {"categories": data, "crosshair": 'true'}
        yAxis = {"title": {"text": 'Valor'}}

        semana01_inicio = hoje - timedelta(days=hoje.isoweekday() - 1)
        semana01_fim = semana01_inicio + timedelta(days=4)

        semanas = {}

        semanas[1] = (semana01_inicio, semana01_fim)

        for i in range(2, qt_semanas + 1):
            semanas[i] = (semanas[i - 1][0] - timedelta(weeks=1),
                          semanas[i - 1][1] - timedelta(weeks=1))

        cotacao_semana_04 = df[semanas[4][0].strftime("%Y-%m-%d"):semanas[4][
            1].strftime("%Y-%m-%d")]
        cotacao_semana_03 = df[semanas[3][0].strftime("%Y-%m-%d"):semanas[3][
            1].strftime("%Y-%m-%d")]
        cotacao_semana_02 = df[semanas[2][0].strftime("%Y-%m-%d"):semanas[2][
            1].strftime("%Y-%m-%d")]
        cotacao_semana_01 = df[semanas[1][0].strftime("%Y-%m-%d"):semanas[1][
            1].strftime("%Y-%m-%d")]

        media_semana_04 = df[semanas[4][0].strftime("%Y-%m-%d"):semanas[4][
            1].strftime("%Y-%m-%d")]
        media_semana_04 = pd.DataFrame(media_semana_04.mean())
        media_semana_04.rename(
            columns={0: 'semana: ' + semanas[4][0].strftime("%U")},
            inplace=True)
        media_semana_04_pivot = pd.pivot_table(media_semana_04,
                                               columns=['Cobre', 'Zinco',
                                                        'Aluminio', 'Chumbo',
                                                        'Estanho', 'Niquel',
                                                        'Dolar'])
        media_semana_04_pivot = media_semana_04_pivot[
            ['Cobre', 'Zinco', 'Aluminio', 'Chumbo', 'Estanho', 'Niquel',
             'Dolar']]

        media_semana_03 = df[semanas[3][0].strftime("%Y-%m-%d"):semanas[3][
            1].strftime("%Y-%m-%d")]
        media_semana_03 = pd.DataFrame(media_semana_03.mean())
        media_semana_03.rename(
            columns={0: 'semana: ' + semanas[3][0].strftime("%U")},
            inplace=True)
        media_semana_03_pivot = pd.pivot_table(media_semana_03,
                                               columns=['Cobre', 'Zinco',
                                                        'Aluminio', 'Chumbo',
                                                        'Estanho', 'Niquel',
                                                        'Dolar'])
        media_semana_03_pivot = media_semana_03_pivot[
            ['Cobre', 'Zinco', 'Aluminio', 'Chumbo', 'Estanho', 'Niquel',
             'Dolar']]

        media_semana_02 = df[semanas[2][0].strftime("%Y-%m-%d"):semanas[2][
            1].strftime("%Y-%m-%d")]
        media_semana_02 = pd.DataFrame(media_semana_02.mean())
        media_semana_02.rename(
            columns={0: 'Semana: ' + semanas[2][0].strftime("%U")},
            inplace=True)
        media_semana_02_pivot = pd.pivot_table(media_semana_02,
                                               columns=['Cobre', 'Zinco',
                                                        'Aluminio', 'Chumbo',
                                                        'Estanho', 'Niquel',
                                                        'Dolar'])
        media_semana_02_pivot = media_semana_02_pivot[
            ['Cobre', 'Zinco', 'Aluminio', 'Chumbo', 'Estanho', 'Niquel',
             'Dolar']]

        media_semana_01 = df[semanas[1][0].strftime("%Y-%m-%d"):semanas[1][
            1].strftime("%Y-%m-%d")]
        media_semana_01 = pd.DataFrame(media_semana_01.mean())
        media_semana_01.rename(
            columns={0: 'semana: ' + semanas[1][0].strftime("%U")},
            inplace=True)
        media_semana_01_pivot = pd.pivot_table(media_semana_01,
                                               columns=['Cobre', 'Zinco',
                                                        'Aluminio', 'Chumbo',
                                                        'Estanho', 'Niquel',
                                                        'Dolar'])
        media_semana_01_pivot = media_semana_01_pivot[
            ['Cobre', 'Zinco', 'Aluminio', 'Chumbo', 'Estanho', 'Niquel',
             'Dolar']]

        # Corrigindo htmls e datas ptBR
        media_semana_01 = media_semana_01_pivot.to_html(classes='mediasemana')
        media_semana_01 = media_semana_01.replace('<th></th>',
                                                  '<th>média na</th>')
        media_semana_02 = media_semana_02_pivot.to_html(classes='mediasemana')
        media_semana_02 = media_semana_02.replace('<th></th>',
                                                  '<th>média na</th>')
        media_semana_03 = media_semana_03_pivot.to_html(classes='mediasemana')
        media_semana_03 = media_semana_03.replace('<th></th>',
                                                  '<th>média na</th>')
        media_semana_04 = media_semana_04_pivot.to_html(classes='mediasemana')
        media_semana_04 = media_semana_04.replace('<th></th>',
                                                  '<th>média na</th>')

        cotacao_semana_01 = cotacao_semana_01.to_html(classes='cotacaolme')
        cotacao_semana_01 = cotacao_semana_01.replace('<th></th>',
                                                      '<th>Data</th>')
        cotacao_semana_01 = BeautifulSoup(cotacao_semana_01, 'html.parser')

        tabela = cotacao_semana_01.find('table')
        colunadata = tabela.find('tbody').findAll('th')

        for data in colunadata:
            databr = data.string.split(" ")
            databr = databr[0].split("-")
            data.string = str(databr[2] + "/" + databr[1] + "/" + databr[0])

        cotacao_semana_02 = cotacao_semana_02.to_html(classes='cotacaolme')
        cotacao_semana_02 = cotacao_semana_02.replace('<th></th>',
                                                      '<th>Data</th>')
        cotacao_semana_02 = BeautifulSoup(cotacao_semana_02, 'html.parser')

        tabela = cotacao_semana_02.find('table')
        colunadata = tabela.find('tbody').findAll('th')

        for data in colunadata:
            databr = data.string.split(" ")
            databr = databr[0].split("-")
            data.string = str(databr[2] + "/" + databr[1] + "/" + databr[0])

        cotacao_semana_03 = cotacao_semana_03.to_html(classes='cotacaolme')
        cotacao_semana_03 = cotacao_semana_03.replace('<th></th>',
                                                      '<th>Data</th>')
        cotacao_semana_03 = BeautifulSoup(cotacao_semana_03, 'html.parser')

        tabela = cotacao_semana_03.find('table')
        colunadata = tabela.find('tbody').findAll('th')

        for data in colunadata:
            databr = data.string.split(" ")
            databr = databr[0].split("-")
            data.string = str(databr[2] + "/" + databr[1] + "/" + databr[0])

        cotacao_semana_04 = cotacao_semana_04.to_html(classes='cotacaolme')
        cotacao_semana_04 = cotacao_semana_04.replace('<th></th>',
                                                      '<th>Data</th>')
        cotacao_semana_04 = BeautifulSoup(cotacao_semana_04, 'html.parser')

        tabela = cotacao_semana_04.find('table')
        colunadata = tabela.find('tbody').findAll('th')

        for data in colunadata:
            databr = data.string.split(" ")
            databr = databr[0].split("-")
            data.string = str(databr[2] + "/" + databr[1] + "/" + databr[0])

        media_periodo = df[
                        periodo.strftime("%Y-%m-%d"):hoje.strftime("%Y-%m-%d")]
        media_periodo = pd.DataFrame(media_periodo.mean())
        media_periodo = media_periodo.to_html(classes='mediaperiodo')
        media_periodo = media_periodo.replace('<th>0</th>',
                                              '<th>média no período</th>')
        media_periodo = media_periodo.replace('<th></th>',
                                              '<th>Metais / Dolar</th>')

        media_periodo_hor = df[
                            periodo.strftime("%Y-%m-%d"):hoje.strftime(
                                "%Y-%m-%d")]
        media_periodo_hor = pd.DataFrame(media_periodo_hor.mean())
        media_periodo_hor = pd.pivot_table(media_periodo_hor,
                                           columns=['Cobre', 'Zinco',
                                                    'Aluminio', 'Chumbo',
                                                    'Estanho', 'Niquel',
                                                    'Dolar'])

        media_periodo_hor = media_periodo_hor[
            ['Cobre', 'Zinco', 'Aluminio', 'Chumbo', 'Estanho', 'Niquel',
             'Dolar']]

        media_periodo_hor = media_periodo_hor.to_html(
            classes='mediaperiodohor')
        media_periodo_hor = media_periodo_hor.replace('<th></th>',
                                                      '<th>média no</th>')
        media_periodo_hor = media_periodo_hor.replace('<th>0</th>',
                                                      '<th>período</th>')

        return render_template('index.html', chartID=chartID,
                               chart=chart,
                               series=series, title=title, xAxis=xAxis,
                               yAxis=yAxis,
                               media_periodo=media_periodo,
                               media_periodo_pivot=media_periodo_hor,
                               tabelas=[
                                   cotacao_semana_04, media_semana_04,
                                   cotacao_semana_03, media_semana_03,
                                   cotacao_semana_02, media_semana_02,
                                   cotacao_semana_01, media_semana_01])

    @application.route('/grafico/')
    def grafico(chartID='chart_ID', chart_type='line', chart_height=350):
        periodo_grafico = periodo_data()
        hoje = periodo_grafico['fim']
        periodo = periodo_grafico['inicio']

        parse.uses_netloc.append("postgres")
        url = parse.urlparse(os.environ["DATABASE_URL"])

        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )

        query = """
                SELECT *
                FROM cotacao_lme
                WHERE "Date" BETWEEN %(inicio)s AND %(fim)s
                """

        query_params = {'inicio': periodo, 'fim': hoje}

        cotacaoatual = pd.read_sql(query, conn, params=query_params)

        cotacaoatual.columns = ['Data', 'Cobre', 'Zinco', 'Aluminio', 'Chumbo',
                                'Estanho', 'Niquel', 'Dolar']

        df = pd.DataFrame(cotacaoatual)

        df['Data'] = pd.to_datetime(df['Data'], utc=True)

        df = df.set_index(df['Data'])

        df = df.drop('Data', axis=1)

        df.fillna(method='ffill', inplace=True)
        df.fillna(method='bfill', inplace=True)

        cobre = list(df['Cobre'])
        zinco = list(df['Zinco'])
        aluminio = list(df['Aluminio'])
        chumbo = list(df['Chumbo'])
        estanho = list(df['Estanho'])
        niquel = list(df['Niquel'])
        dolar = list(df['Dolar'])
        data = list(df.index.strftime('%d/%m/%y'))

        chart = {"renderTo": chartID, "type": chart_type,
                 "height": chart_height}
        series = [{"name": 'Cobre', "data": cobre},
                  {"name": 'Zinco', "data": zinco, "visible": 'false'},
                  {"name": 'Alumínio', "data": aluminio, "visible": 'false'},
                  {"name": 'Chumbo', "data": chumbo, "visible": 'false'},
                  {"name": 'Estanho', "data": estanho, "visible": 'false'},
                  {"name": 'Níquel', "data": niquel, "visible": 'false'},
                  {"name": 'Dolar', "data": dolar, "visible": 'false'}
                  ]
        title = {"text": 'Cotação LME'}
        xAxis = {"categories": data, "crosshair": 'true'}
        yAxis = {"title": {"text": 'Valor'}}

        return render_template('grafico.html', chartID=chartID, chart=chart,
                               series=series, title=title, xAxis=xAxis,
                               yAxis=yAxis)

    @application.route('/cotacao/')
    def lme_cotacao(chartID='chart_ID', chart_type='line', chart_height=350,
                    colorscheme=None):
        qt_semanas = 4
        periodo_cotacao = periodo_data()
        hoje = periodo_cotacao['fim']
        periodo = periodo_cotacao['inicio']

        parse.uses_netloc.append("postgres")
        url = parse.urlparse(os.environ["DATABASE_URL"])

        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )

        # cotacaoatual = pd.read_sql("SELECT * FROM cotacao_lme")

        query = """
                SELECT *
                FROM cotacao_lme
                WHERE "Date" BETWEEN %(inicio)s AND %(fim)s
                """

        query_params = {'inicio': periodo, 'fim': hoje}

        cotacaoatual = pd.read_sql(query, conn, params=query_params)

        cotacaoatual.columns = ['Data', 'Cobre', 'Zinco', 'Aluminio', 'Chumbo',
                                'Estanho', 'Niquel', 'Dolar']

        df = pd.DataFrame(cotacaoatual)

        df['Data'] = pd.to_datetime(df['Data'], utc=True)

        df = df.set_index(df['Data'])

        df = df.drop('Data', axis=1)

        df.fillna(method='ffill', inplace=True)
        df.fillna(method='bfill', inplace=True)

        cobre = list(df['Cobre'])
        zinco = list(df['Zinco'])
        aluminio = list(df['Aluminio'])
        chumbo = list(df['Chumbo'])
        estanho = list(df['Estanho'])
        niquel = list(df['Niquel'])
        dolar = list(df['Dolar'])
        data = list(df.index.strftime('%d/%m/%y'))

        chart = {"renderTo": chartID, "type": chart_type,
                 "height": chart_height}
        series = [{"name": 'Cobre', "data": cobre},
                  {"name": 'Zinco', "data": zinco, "visible": 'false'},
                  {"name": 'Alumínio', "data": aluminio, "visible": 'false'},
                  {"name": 'Chumbo', "data": chumbo, "visible": 'false'},
                  {"name": 'Estanho', "data": estanho, "visible": 'false'},
                  {"name": 'Níquel', "data": niquel, "visible": 'false'},
                  {"name": 'Dolar', "data": dolar, "visible": 'false'}
                  ]
        title = {"text": 'Cotação LME'}
        xAxis = {"categories": data, "crosshair": 'true'}
        yAxis = {"title": {"text": 'Valor'}}

        semana01_inicio = hoje - timedelta(days=hoje.isoweekday() - 1)
        semana01_fim = semana01_inicio + timedelta(days=4)

        semanas = {}

        semanas[1] = (semana01_inicio, semana01_fim)

        for i in range(2, qt_semanas + 1):
            semanas[i] = (semanas[i - 1][0] - timedelta(weeks=1),
                          semanas[i - 1][1] - timedelta(weeks=1))

        cotacao_semana_04 = df[semanas[4][0].strftime("%Y-%m-%d"):semanas[4][
            1].strftime("%Y-%m-%d")]
        cotacao_semana_03 = df[semanas[3][0].strftime("%Y-%m-%d"):semanas[3][
            1].strftime("%Y-%m-%d")]
        cotacao_semana_02 = df[semanas[2][0].strftime("%Y-%m-%d"):semanas[2][
            1].strftime("%Y-%m-%d")]
        cotacao_semana_01 = df[semanas[1][0].strftime("%Y-%m-%d"):semanas[1][
            1].strftime("%Y-%m-%d")]

        media_semana_04 = df[semanas[4][0].strftime("%Y-%m-%d"):semanas[4][
            1].strftime("%Y-%m-%d")]
        media_semana_04 = pd.DataFrame(media_semana_04.mean())
        media_semana_04.rename(
            columns={0: 'semana: ' + semanas[4][0].strftime("%U")},
            inplace=True)
        media_semana_04_pivot = pd.pivot_table(media_semana_04,
                                               columns=['Cobre', 'Zinco',
                                                        'Aluminio', 'Chumbo',
                                                        'Estanho', 'Niquel',
                                                        'Dolar'])
        media_semana_04_pivot = media_semana_04_pivot[
            ['Cobre', 'Zinco', 'Aluminio', 'Chumbo', 'Estanho', 'Niquel',
             'Dolar']]

        media_semana_03 = df[semanas[3][0].strftime("%Y-%m-%d"):semanas[3][
            1].strftime("%Y-%m-%d")]
        media_semana_03 = pd.DataFrame(media_semana_03.mean())
        media_semana_03.rename(
            columns={0: 'semana: ' + semanas[3][0].strftime("%U")},
            inplace=True)
        media_semana_03_pivot = pd.pivot_table(media_semana_03,
                                               columns=['Cobre', 'Zinco',
                                                        'Aluminio', 'Chumbo',
                                                        'Estanho', 'Niquel',
                                                        'Dolar'])
        media_semana_03_pivot = media_semana_03_pivot[
            ['Cobre', 'Zinco', 'Aluminio', 'Chumbo', 'Estanho', 'Niquel',
             'Dolar']]

        media_semana_02 = df[semanas[2][0].strftime("%Y-%m-%d"):semanas[2][
            1].strftime("%Y-%m-%d")]
        media_semana_02 = pd.DataFrame(media_semana_02.mean())
        media_semana_02.rename(
            columns={0: 'Semana: ' + semanas[2][0].strftime("%U")},
            inplace=True)
        media_semana_02_pivot = pd.pivot_table(media_semana_02,
                                               columns=['Cobre', 'Zinco',
                                                        'Aluminio', 'Chumbo',
                                                        'Estanho', 'Niquel',
                                                        'Dolar'])
        media_semana_02_pivot = media_semana_02_pivot[
            ['Cobre', 'Zinco', 'Aluminio', 'Chumbo', 'Estanho', 'Niquel',
             'Dolar']]

        media_semana_01 = df[semanas[1][0].strftime("%Y-%m-%d"):semanas[1][
            1].strftime("%Y-%m-%d")]
        media_semana_01 = pd.DataFrame(media_semana_01.mean())
        media_semana_01.rename(
            columns={0: 'semana: ' + semanas[1][0].strftime("%U")},
            inplace=True)
        media_semana_01_pivot = pd.pivot_table(media_semana_01,
                                               columns=['Cobre', 'Zinco',
                                                        'Aluminio', 'Chumbo',
                                                        'Estanho', 'Niquel',
                                                        'Dolar'])
        media_semana_01_pivot = media_semana_01_pivot[
            ['Cobre', 'Zinco', 'Aluminio', 'Chumbo', 'Estanho', 'Niquel',
             'Dolar']]

        # Corrigindo htmls e datas ptBR
        media_semana_01 = media_semana_01_pivot.to_html(classes='mediasemana')
        media_semana_01 = media_semana_01.replace('<th></th>',
                                                  '<th>média na</th>')
        media_semana_02 = media_semana_02_pivot.to_html(classes='mediasemana')
        media_semana_02 = media_semana_02.replace('<th></th>',
                                                  '<th>média na</th>')
        media_semana_03 = media_semana_03_pivot.to_html(classes='mediasemana')
        media_semana_03 = media_semana_03.replace('<th></th>',
                                                  '<th>média na</th>')
        media_semana_04 = media_semana_04_pivot.to_html(classes='mediasemana')
        media_semana_04 = media_semana_04.replace('<th></th>',
                                                  '<th>média na</th>')

        cotacao_semana_01 = cotacao_semana_01.to_html(classes='cotacaolme')
        cotacao_semana_01 = cotacao_semana_01.replace('<th></th>',
                                                      '<th>Data</th>')
        cotacao_semana_01 = BeautifulSoup(cotacao_semana_01, 'html.parser')

        tabela = cotacao_semana_01.find('table')
        colunadata = tabela.find('tbody').findAll('th')

        for data in colunadata:
            databr = data.string.split(" ")
            databr = databr[0].split("-")
            data.string = str(databr[2] + "/" + databr[1] + "/" + databr[0])

        cotacao_semana_02 = cotacao_semana_02.to_html(classes='cotacaolme')
        cotacao_semana_02 = cotacao_semana_02.replace('<th></th>',
                                                      '<th>Data</th>')
        cotacao_semana_02 = BeautifulSoup(cotacao_semana_02, 'html.parser')

        tabela = cotacao_semana_02.find('table')
        colunadata = tabela.find('tbody').findAll('th')

        for data in colunadata:
            databr = data.string.split(" ")
            databr = databr[0].split("-")
            data.string = str(databr[2] + "/" + databr[1] + "/" + databr[0])

        cotacao_semana_03 = cotacao_semana_03.to_html(classes='cotacaolme')
        cotacao_semana_03 = cotacao_semana_03.replace('<th></th>',
                                                      '<th>Data</th>')
        cotacao_semana_03 = BeautifulSoup(cotacao_semana_03, 'html.parser')

        tabela = cotacao_semana_03.find('table')
        colunadata = tabela.find('tbody').findAll('th')

        for data in colunadata:
            databr = data.string.split(" ")
            databr = databr[0].split("-")
            data.string = str(databr[2] + "/" + databr[1] + "/" + databr[0])

        cotacao_semana_04 = cotacao_semana_04.to_html(classes='cotacaolme')
        cotacao_semana_04 = cotacao_semana_04.replace('<th></th>',
                                                      '<th>Data</th>')
        cotacao_semana_04 = BeautifulSoup(cotacao_semana_04, 'html.parser')

        tabela = cotacao_semana_04.find('table')
        colunadata = tabela.find('tbody').findAll('th')

        for data in colunadata:
            databr = data.string.split(" ")
            databr = databr[0].split("-")
            data.string = str(databr[2] + "/" + databr[1] + "/" + databr[0])

        media_periodo = df[
                        periodo.strftime("%Y-%m-%d"):hoje.strftime("%Y-%m-%d")]
        media_periodo = pd.DataFrame(media_periodo.mean())
        media_periodo = media_periodo.to_html(classes='mediaperiodo')
        media_periodo = media_periodo.replace('<th>0</th>',
                                              '<th>média no período</th>')
        media_periodo = media_periodo.replace('<th></th>',
                                              '<th>Metais / Dolar</th>')

        media_periodo_hor = df[
                            periodo.strftime("%Y-%m-%d"):hoje.strftime(
                                "%Y-%m-%d")]
        media_periodo_hor = pd.DataFrame(media_periodo_hor.mean())
        media_periodo_hor = pd.pivot_table(media_periodo_hor,
                                           columns=['Cobre', 'Zinco',
                                                    'Aluminio', 'Chumbo',
                                                    'Estanho', 'Niquel',
                                                    'Dolar'])

        media_periodo_hor = media_periodo_hor[
            ['Cobre', 'Zinco', 'Aluminio', 'Chumbo', 'Estanho', 'Niquel',
             'Dolar']]

        media_periodo_hor = media_periodo_hor.to_html(
            classes='mediaperiodohor')
        media_periodo_hor = media_periodo_hor.replace('<th></th>',
                                                      '<th>média no</th>')
        media_periodo_hor = media_periodo_hor.replace('<th>0</th>',
                                                      '<th>período</th>')

        return render_template('cotacao_scheme.html', chartID=chartID,
                               chart=chart,
                               series=series, title=title, xAxis=xAxis,
                               yAxis=yAxis,
                               colorscheme=colorscheme,
                               media_periodo=media_periodo,
                               media_periodo_pivot=media_periodo_hor,
                               tabelas=[
                                   cotacao_semana_04, media_semana_04,
                                   cotacao_semana_03, media_semana_03,
                                   cotacao_semana_02, media_semana_02,
                                   cotacao_semana_01, media_semana_01])

    @application.route('/summary', methods=['GET'])
    def summary():

        parse.uses_netloc.append("postgres")
        url = parse.urlparse(os.environ["DATABASE_URL"])

        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )

        query = """
                SELECT * FROM cotacao_lme
                WHERE cotacao_lme NOTNULL
                ORDER BY "Date" DESC LIMIT 1
                """

        cotacaoatual = pd.read_sql(query, conn)

        cotacaoatual.columns = ['Data', 'Cobre', 'Zinco', 'Aluminio', 'Chumbo',
                                'Estanho', 'Niquel', 'Dolar']

        df = pd.DataFrame(cotacaoatual)

        df['Data'] = pd.to_datetime(df['Data'], utc=True)

        df = df.set_index(df['Data'])

        df = df.drop('Data', axis=1)

        df.fillna(method='ffill', inplace=True)

        cobre = list(df['Cobre'])
        zinco = list(df['Zinco'])
        aluminio = list(df['Aluminio'])
        chumbo = list(df['Chumbo'])
        estanho = list(df['Estanho'])
        niquel = list(df['Niquel'])
        dolar = list(df['Dolar'])
        data = list(df.index.strftime('%d/%m/%y'))

        response = jsonify(
            cobre=cobre,
            zinco=zinco,
            aluminio=aluminio,
            chumbo=chumbo,
            estanho=estanho,
            niquel=niquel,
            dolar=dolar,
            data=data)

        response.headers.add("Access-Control-Allow-Origin", '*')
        return response

    @application.route('/json', methods=['GET'])
    def json_summary():

        parse.uses_netloc.append("postgres")
        url = parse.urlparse(os.environ["DATABASE_URL"])

        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )

        query = """
                    SELECT * FROM cotacao_lme
                    WHERE cotacao_lme NOTNULL
                    ORDER BY "Date" DESC LIMIT 40
                    """

        cotacaoatual = pd.read_sql(query, conn)

        cotacaoatual.columns = ['Data', 'Cobre', 'Zinco', 'Aluminio', 'Chumbo',
                                'Estanho', 'Niquel', 'Dolar']

        df = pd.DataFrame(cotacaoatual)

        df['Data'] = pd.to_datetime(df['Data'], utc=True)

        df = df.set_index(df['Data'])

        df.fillna(method='ffill', inplace=True)

        response = jsonify(df.to_json(orient='records',
                                      date_format='iso',
                                      force_ascii=False))

        response.headers.add("Access-Control-Allow-Origin", '*')
        return response

    @application.route('/json/v2', methods=['GET'])
    def json_summary_v2():
        periodo_cotacao = periodo_data()
        hoje = periodo_cotacao['fim']
        periodo = periodo_cotacao['inicio']

        parse.uses_netloc.append("postgres")
        url = parse.urlparse(os.environ["DATABASE_URL"])

        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )

        query = """
                SELECT *
                FROM cotacao_lme
                WHERE "Date" BETWEEN %(inicio)s AND %(fim)s
                """

        query_params = {'inicio': periodo, 'fim': hoje}

        cotacaoatual = pd.read_sql(query, conn, params=query_params)

        cotacaoatual.columns = ['Data', 'Cobre', 'Zinco', 'Aluminio', 'Chumbo',
                                'Estanho', 'Niquel', 'Dolar']

        df = pd.DataFrame(cotacaoatual)

        df['Data'] = pd.to_datetime(df['Data'], utc=True)

        df = df.set_index(df['Data'])

        df.fillna(method='ffill', inplace=True)

        cobre = list(df['Cobre'])
        zinco = list(df['Zinco'])
        aluminio = list(df['Aluminio'])
        chumbo = list(df['Chumbo'])
        estanho = list(df['Estanho'])
        niquel = list(df['Niquel'])
        dolar = list(df['Dolar'])
        data = list(df.index.strftime('%d/%m/%y'))

        response = jsonify(
            cobre=cobre,
            zinco=zinco,
            aluminio=aluminio,
            chumbo=chumbo,
            estanho=estanho,
            niquel=niquel,
            dolar=dolar,
            data=data)

        response.headers.add("Access-Control-Allow-Origin", '*')
        return response

    def latest_values():
        parse.uses_netloc.append("postgres")
        url = parse.urlparse(os.environ["DATABASE_URL"])

        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )

        query = """
                SELECT * FROM cotacao_lme
                WHERE cotacao_lme NOTNULL
                ORDER BY "Date" DESC LIMIT 1
                """

        values = pd.read_sql(query, conn)

        values.columns = ['Data', 'Cobre', 'Zinco', 'Aluminio', 'Chumbo',
                          'Estanho', 'Niquel', 'Dolar']

        df = pd.DataFrame(values)

        df['Data'] = latest_date = pd.to_datetime(df['Data'], utc=True)
        print(latest_date[0])
        print(latest_date[0].strftime('%Y-%m-%d'))

        df = df.set_index(df['Data'])
        df = df.drop('Data', axis=1)

        df.fillna(method='ffill', inplace=True)
        df.fillna(method='bfill', inplace=True)

        return latest_date[0]

    def periodo_data():
        fim = latest_values()
        inicio = fim - timedelta(weeks=4)

        dia_semana = fim.isoweekday()
        semana_numero = fim.strftime("%U")

        if semana_numero == "00":
            fim = datetime.now() - timedelta(days=fim.isoweekday())
        else:
            pass

        if dia_semana == 1:
            fim = datetime.now() - timedelta(days=3)
        else:
            pass

        return {'inicio': inicio, 'fim': fim}

    return application
