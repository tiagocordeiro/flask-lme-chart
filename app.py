from flask import Flask, render_template, jsonify
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import pandas as pd
import os
from urllib import parse
import psycopg2

app = Flask(__name__)

pd.options.display.float_format = '{:,.2f}'.format

pd.set_option('colheader_justify', 'right')

cotacaoatual = pd.read_csv('static/cotacao-atual.csv')

cotacaoatual.columns = ['Data', 'Cobre', 'Zinco', 'Aluminio', 'Chumbo',
                        'Estanho', 'Niquel', 'Dolar']

df = pd.DataFrame(cotacaoatual)

df['Data'] = pd.to_datetime(df['Data'])

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
data = list(df.index.strftime('%d/%m'))

"""
Testes com cotação completa
"""
cotacaocompleta = pd.read_csv('static/todo-periodo.csv')

cotacaocompleta.columns = ['Data', 'Cobre', 'Zinco', 'Aluminio', 'Chumbo',
                           'Estanho', 'Niquel', 'Dolar']

df_completo = pd.DataFrame(cotacaocompleta)

df_completo['Data'] = pd.to_datetime(df_completo['Data'])

df_completo = df_completo.set_index(df_completo['Data'])

df_completo = df_completo.drop('Data', axis=1)

df_completo.fillna(method='ffill', inplace=True)

cobre_completo = list(df_completo['Cobre'])
zinco_completo = list(df_completo['Zinco'])
aluminio_completo = list(df_completo['Aluminio'])
chumbo_completo = list(df_completo['Chumbo'])
estanho_completo = list(df_completo['Estanho'])
niquel_completo = list(df_completo['Niquel'])
dolar_completo = list(df_completo['Dolar'])
data_completo = list(df_completo.index.strftime('%d/%m/%Y'))

"""
Médias períodos
"""
now = datetime.now()
mes = now - timedelta(weeks=4)
semana = now - timedelta(days=7)

media_30dias = pd.DataFrame(df_completo[mes:now].mean())

media_ultima_semana = pd.DataFrame(df_completo[semana:now].mean())

"""
Rotas
"""


@app.route('/')
@app.route('/index')
@app.route('/lme')
@app.route('/lme-dashboard')
def lme_dashboard(chartID='chart_ID', chart_type='line', chart_height=350):
    qt_semanas = 4
    hoje = datetime.now()
    diadasemana = hoje.isoweekday()
    semanaNumero = hoje.strftime("%U")

    if semanaNumero == "00":
        hoje = datetime.now() - timedelta(days=hoje.isoweekday())
    else:
        pass

    if diadasemana == 1:
        hoje = datetime.now() - timedelta(weeks=1)
    else:
        pass

    periodo = hoje - timedelta(weeks=4)

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

    cobre = list(df['Cobre'])
    zinco = list(df['Zinco'])
    aluminio = list(df['Aluminio'])
    chumbo = list(df['Chumbo'])
    estanho = list(df['Estanho'])
    niquel = list(df['Niquel'])
    dolar = list(df['Dolar'])
    data = list(df.index.strftime('%d/%m/%y'))

    chart = {"renderTo": chartID, "type": chart_type, "height": chart_height}
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
        columns={0: 'semana: ' + semanas[4][0].strftime("%U")}, inplace=True)
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
        columns={0: 'semana: ' + semanas[3][0].strftime("%U")}, inplace=True)
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
        columns={0: 'Semana: ' + semanas[2][0].strftime("%U")}, inplace=True)
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
        columns={0: 'semana: ' + semanas[1][0].strftime("%U")}, inplace=True)
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
    media_semana_01 = media_semana_01.replace('<th></th>', '<th>média na</th>')
    media_semana_02 = media_semana_02_pivot.to_html(classes='mediasemana')
    media_semana_02 = media_semana_02.replace('<th></th>', '<th>média na</th>')
    media_semana_03 = media_semana_03_pivot.to_html(classes='mediasemana')
    media_semana_03 = media_semana_03.replace('<th></th>', '<th>média na</th>')
    media_semana_04 = media_semana_04_pivot.to_html(classes='mediasemana')
    media_semana_04 = media_semana_04.replace('<th></th>', '<th>média na</th>')

    cotacao_semana_01 = cotacao_semana_01.to_html(classes='cotacaolme')
    cotacao_semana_01 = cotacao_semana_01.replace('<th></th>', '<th>Data</th>')
    cotacao_semana_01 = BeautifulSoup(cotacao_semana_01, 'html.parser')

    tabela = cotacao_semana_01.find('table')
    colunadata = tabela.find('tbody').findAll('th')

    for data in colunadata:
        databr = data.string.split(" ")
        databr = databr[0].split("-")
        data.string = str(databr[2] + "/" + databr[1] + "/" + databr[0])

    cotacao_semana_02 = cotacao_semana_02.to_html(classes='cotacaolme')
    cotacao_semana_02 = cotacao_semana_02.replace('<th></th>', '<th>Data</th>')
    cotacao_semana_02 = BeautifulSoup(cotacao_semana_02, 'html.parser')

    tabela = cotacao_semana_02.find('table')
    colunadata = tabela.find('tbody').findAll('th')

    for data in colunadata:
        databr = data.string.split(" ")
        databr = databr[0].split("-")
        data.string = str(databr[2] + "/" + databr[1] + "/" + databr[0])

    cotacao_semana_03 = cotacao_semana_03.to_html(classes='cotacaolme')
    cotacao_semana_03 = cotacao_semana_03.replace('<th></th>', '<th>Data</th>')
    cotacao_semana_03 = BeautifulSoup(cotacao_semana_03, 'html.parser')

    tabela = cotacao_semana_03.find('table')
    colunadata = tabela.find('tbody').findAll('th')

    for data in colunadata:
        databr = data.string.split(" ")
        databr = databr[0].split("-")
        data.string = str(databr[2] + "/" + databr[1] + "/" + databr[0])

    cotacao_semana_04 = cotacao_semana_04.to_html(classes='cotacaolme')
    cotacao_semana_04 = cotacao_semana_04.replace('<th></th>', '<th>Data</th>')
    cotacao_semana_04 = BeautifulSoup(cotacao_semana_04, 'html.parser')

    tabela = cotacao_semana_04.find('table')
    colunadata = tabela.find('tbody').findAll('th')

    for data in colunadata:
        databr = data.string.split(" ")
        databr = databr[0].split("-")
        data.string = str(databr[2] + "/" + databr[1] + "/" + databr[0])

    media_periodo = df[periodo.strftime("%Y-%m-%d"):hoje.strftime("%Y-%m-%d")]
    media_periodo = pd.DataFrame(media_periodo.mean())
    media_periodo = media_periodo.to_html(classes='mediaperiodo')
    media_periodo = media_periodo.replace('<th>0</th>',
                                          '<th>média no período</th>')
    media_periodo = media_periodo.replace('<th></th>',
                                          '<th>Metais / Dolar</th>')

    media_periodo_hor = df[
                        periodo.strftime("%Y-%m-%d"):hoje.strftime("%Y-%m-%d")]
    media_periodo_hor = pd.DataFrame(media_periodo_hor.mean())
    media_periodo_hor = pd.pivot_table(media_periodo_hor,
                                       columns=['Cobre', 'Zinco',
                                                'Aluminio', 'Chumbo',
                                                'Estanho', 'Niquel',
                                                'Dolar'])

    media_periodo_hor = media_periodo_hor[
        ['Cobre', 'Zinco', 'Aluminio', 'Chumbo', 'Estanho', 'Niquel',
         'Dolar']]

    media_periodo_hor = media_periodo_hor.to_html(classes='mediaperiodohor')
    media_periodo_hor = media_periodo_hor.replace('<th></th>',
                                                  '<th>média no</th>')
    media_periodo_hor = media_periodo_hor.replace('<th>0</th>',
                                                  '<th>período</th>')

    return render_template('cotacao.html', chartID=chartID, chart=chart,
                           series=series, title=title, xAxis=xAxis,
                           yAxis=yAxis,
                           media_periodo=media_periodo,
                           media_periodo_pivot=media_periodo_hor,
                           tabelas=[
                               cotacao_semana_04, media_semana_04,
                               cotacao_semana_03, media_semana_03,
                               cotacao_semana_02, media_semana_02,
                               cotacao_semana_01, media_semana_01])


@app.route('/cotacao/')
def lme_cotacao(chartID='chart_ID', chart_type='line', chart_height=350,
                colorscheme=None):
    qt_semanas = 4
    hoje = datetime.now()
    diadasemana = hoje.isoweekday()
    semanaNumero = hoje.strftime("%U")

    if semanaNumero == "00":
        hoje = datetime.now() - timedelta(days=hoje.isoweekday())
    else:
        pass

    if diadasemana == 1:
        hoje = datetime.now() - timedelta(days=3)
    else:
        pass

    periodo = hoje - timedelta(weeks=4)

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

    cobre = list(df['Cobre'])
    zinco = list(df['Zinco'])
    aluminio = list(df['Aluminio'])
    chumbo = list(df['Chumbo'])
    estanho = list(df['Estanho'])
    niquel = list(df['Niquel'])
    dolar = list(df['Dolar'])
    data = list(df.index.strftime('%d/%m/%y'))

    chart = {"renderTo": chartID, "type": chart_type, "height": chart_height}
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
        columns={0: 'semana: ' + semanas[4][0].strftime("%U")}, inplace=True)
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
        columns={0: 'semana: ' + semanas[3][0].strftime("%U")}, inplace=True)
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
        columns={0: 'Semana: ' + semanas[2][0].strftime("%U")}, inplace=True)
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
        columns={0: 'semana: ' + semanas[1][0].strftime("%U")}, inplace=True)
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
    media_semana_01 = media_semana_01.replace('<th></th>', '<th>média na</th>')
    media_semana_02 = media_semana_02_pivot.to_html(classes='mediasemana')
    media_semana_02 = media_semana_02.replace('<th></th>', '<th>média na</th>')
    media_semana_03 = media_semana_03_pivot.to_html(classes='mediasemana')
    media_semana_03 = media_semana_03.replace('<th></th>', '<th>média na</th>')
    media_semana_04 = media_semana_04_pivot.to_html(classes='mediasemana')
    media_semana_04 = media_semana_04.replace('<th></th>', '<th>média na</th>')

    cotacao_semana_01 = cotacao_semana_01.to_html(classes='cotacaolme')
    cotacao_semana_01 = cotacao_semana_01.replace('<th></th>', '<th>Data</th>')
    cotacao_semana_01 = BeautifulSoup(cotacao_semana_01, 'html.parser')

    tabela = cotacao_semana_01.find('table')
    colunadata = tabela.find('tbody').findAll('th')

    for data in colunadata:
        databr = data.string.split(" ")
        databr = databr[0].split("-")
        data.string = str(databr[2] + "/" + databr[1] + "/" + databr[0])

    cotacao_semana_02 = cotacao_semana_02.to_html(classes='cotacaolme')
    cotacao_semana_02 = cotacao_semana_02.replace('<th></th>', '<th>Data</th>')
    cotacao_semana_02 = BeautifulSoup(cotacao_semana_02, 'html.parser')

    tabela = cotacao_semana_02.find('table')
    colunadata = tabela.find('tbody').findAll('th')

    for data in colunadata:
        databr = data.string.split(" ")
        databr = databr[0].split("-")
        data.string = str(databr[2] + "/" + databr[1] + "/" + databr[0])

    cotacao_semana_03 = cotacao_semana_03.to_html(classes='cotacaolme')
    cotacao_semana_03 = cotacao_semana_03.replace('<th></th>', '<th>Data</th>')
    cotacao_semana_03 = BeautifulSoup(cotacao_semana_03, 'html.parser')

    tabela = cotacao_semana_03.find('table')
    colunadata = tabela.find('tbody').findAll('th')

    for data in colunadata:
        databr = data.string.split(" ")
        databr = databr[0].split("-")
        data.string = str(databr[2] + "/" + databr[1] + "/" + databr[0])

    cotacao_semana_04 = cotacao_semana_04.to_html(classes='cotacaolme')
    cotacao_semana_04 = cotacao_semana_04.replace('<th></th>', '<th>Data</th>')
    cotacao_semana_04 = BeautifulSoup(cotacao_semana_04, 'html.parser')

    tabela = cotacao_semana_04.find('table')
    colunadata = tabela.find('tbody').findAll('th')

    for data in colunadata:
        databr = data.string.split(" ")
        databr = databr[0].split("-")
        data.string = str(databr[2] + "/" + databr[1] + "/" + databr[0])

    media_periodo = df[periodo.strftime("%Y-%m-%d"):hoje.strftime("%Y-%m-%d")]
    media_periodo = pd.DataFrame(media_periodo.mean())
    media_periodo = media_periodo.to_html(classes='mediaperiodo')
    media_periodo = media_periodo.replace('<th>0</th>',
                                          '<th>média no período</th>')
    media_periodo = media_periodo.replace('<th></th>',
                                          '<th>Metais / Dolar</th>')

    media_periodo_hor = df[
                        periodo.strftime("%Y-%m-%d"):hoje.strftime("%Y-%m-%d")]
    media_periodo_hor = pd.DataFrame(media_periodo_hor.mean())
    media_periodo_hor = pd.pivot_table(media_periodo_hor,
                                       columns=['Cobre', 'Zinco',
                                                'Aluminio', 'Chumbo',
                                                'Estanho', 'Niquel',
                                                'Dolar'])

    media_periodo_hor = media_periodo_hor[
        ['Cobre', 'Zinco', 'Aluminio', 'Chumbo', 'Estanho', 'Niquel',
         'Dolar']]

    media_periodo_hor = media_periodo_hor.to_html(classes='mediaperiodohor')
    media_periodo_hor = media_periodo_hor.replace('<th></th>',
                                                  '<th>média no</th>')
    media_periodo_hor = media_periodo_hor.replace('<th>0</th>',
                                                  '<th>período</th>')

    return render_template('cotacao_scheme.html', chartID=chartID, chart=chart,
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


@app.route('/grafico/')
def lme_grafico(chartID='chart_ID', chart_type='line', chart_height=350):
    hoje = datetime.now()
    periodo = hoje - timedelta(weeks=4)

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

    cobre = list(df['Cobre'])
    zinco = list(df['Zinco'])
    aluminio = list(df['Aluminio'])
    chumbo = list(df['Chumbo'])
    estanho = list(df['Estanho'])
    niquel = list(df['Niquel'])
    dolar = list(df['Dolar'])
    data = list(df.index.strftime('%d/%m/%y'))

    chart = {"renderTo": chartID, "type": chart_type, "height": chart_height}
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


@app.route('/grafico/cobre')
def lme_grafico_cobre(chartID='chart_ID', chart_type='line', chart_height=350):
    hoje = datetime.now()
    periodo = hoje - timedelta(weeks=4)

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

    cobre = list(df['Cobre'])
    data = list(df.index.strftime('%d/%m/%y'))

    chart = {"renderTo": chartID, "type": chart_type, "height": chart_height}
    series = [{"name": 'Cobre', "data": cobre}]
    title = {"text": 'Cotação Cobre'}
    xAxis = {"categories": data, "crosshair": 'true'}
    yAxis = {"title": {"text": 'Valor'}}

    return render_template('grafico_simples.html', chartID=chartID,
                           chart=chart,
                           series=series, title=title, xAxis=xAxis,
                           yAxis=yAxis)


@app.route('/grafico/zinco')
def lme_grafico_zinco(chartID='chart_ID', chart_type='line', chart_height=350):
    hoje = datetime.now()
    periodo = hoje - timedelta(weeks=4)

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

    zinco = list(df['Zinco'])
    data = list(df.index.strftime('%d/%m/%y'))

    chart = {"renderTo": chartID, "type": chart_type, "height": chart_height}
    series = [{"name": 'Zinco', "data": zinco}]
    title = {"text": 'Cotação Zinco'}
    xAxis = {"categories": data, "crosshair": 'true'}
    yAxis = {"title": {"text": 'Valor'}}

    return render_template('grafico_simples.html', chartID=chartID,
                           chart=chart, series=series, title=title,
                           xAxis=xAxis, yAxis=yAxis)


@app.route('/grafico/aluminio')
def lme_grafico_aluminio(chartID='chart_ID', chart_type='line',
                         chart_height=350):
    hoje = datetime.now()
    periodo = hoje - timedelta(weeks=4)

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

    aluminio = list(df['Aluminio'])
    data = list(df.index.strftime('%d/%m/%y'))

    chart = {"renderTo": chartID, "type": chart_type, "height": chart_height}
    series = [{"name": 'Alumínio', "data": aluminio}]
    title = {"text": 'Cotação Alumínio'}
    xAxis = {"categories": data, "crosshair": 'true'}
    yAxis = {"title": {"text": 'Valor'}}

    return render_template('grafico_simples.html', chartID=chartID,
                           chart=chart, series=series, title=title,
                           xAxis=xAxis, yAxis=yAxis)


@app.route('/grafico/chumbo')
def lme_grafico_chumbo(chartID='chart_ID', chart_type='line',
                       chart_height=350):
    hoje = datetime.now()
    periodo = hoje - timedelta(weeks=4)

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

    chumbo = list(df['Chumbo'])
    data = list(df.index.strftime('%d/%m/%y'))

    chart = {"renderTo": chartID, "type": chart_type, "height": chart_height}
    series = [{"name": 'Chumbo', "data": chumbo}]
    title = {"text": 'Cotação Chumbo'}
    xAxis = {"categories": data, "crosshair": 'true'}
    yAxis = {"title": {"text": 'Valor'}}

    return render_template('grafico_simples.html', chartID=chartID,
                           chart=chart, series=series, title=title,
                           xAxis=xAxis, yAxis=yAxis)


@app.route('/grafico/estanho')
def lme_grafico_estanho(chartID='chart_ID', chart_type='line',
                        chart_height=350):
    hoje = datetime.now()
    periodo = hoje - timedelta(weeks=4)

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

    estanho = list(df['Estanho'])
    data = list(df.index.strftime('%d/%m/%y'))

    chart = {"renderTo": chartID, "type": chart_type, "height": chart_height}
    series = [{"name": 'Estanho', "data": estanho}]
    title = {"text": 'Cotação Estanho'}
    xAxis = {"categories": data, "crosshair": 'true'}
    yAxis = {"title": {"text": 'Valor'}}

    return render_template('grafico_simples.html', chartID=chartID,
                           chart=chart, series=series, title=title,
                           xAxis=xAxis, yAxis=yAxis)


@app.route('/grafico/niquel')
def lme_grafico_niquel(chartID='chart_ID', chart_type='line',
                       chart_height=350):
    hoje = datetime.now()
    periodo = hoje - timedelta(weeks=4)

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

    niquel = list(df['Niquel'])
    data = list(df.index.strftime('%d/%m/%y'))

    chart = {"renderTo": chartID, "type": chart_type, "height": chart_height}
    series = [{"name": 'Níquel', "data": niquel}]
    title = {"text": 'Cotação Níquel'}
    xAxis = {"categories": data, "crosshair": 'true'}
    yAxis = {"title": {"text": 'Valor'}}

    return render_template('grafico_simples.html', chartID=chartID,
                           chart=chart, series=series, title=title,
                           xAxis=xAxis, yAxis=yAxis)


@app.route('/grafico/dolar')
def lme_grafico_dolar(chartID='chart_ID', chart_type='line', chart_height=350):
    hoje = datetime.now()
    periodo = hoje - timedelta(weeks=4)

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

    dolar = list(df['Dolar'])
    data = list(df.index.strftime('%d/%m/%y'))

    chart = {"renderTo": chartID, "type": chart_type, "height": chart_height}
    series = [{"name": 'Dolar', "data": dolar}]
    title = {"text": 'Cotação Dolar'}
    xAxis = {"categories": data, "crosshair": 'true'}
    yAxis = {"title": {"text": 'Valor'}}

    return render_template('grafico_simples.html', chartID=chartID,
                           chart=chart, series=series, title=title,
                           xAxis=xAxis, yAxis=yAxis)


@app.route('/lme/cobre')
def lme_cobre(chartID='chart_ID', chart_type='line', chart_height=350):
    chart = {"renderTo": chartID, "type": chart_type, "height": chart_height}
    series = [{"name": 'Cobre', "data": cobre}]
    title = {"text": 'Cobre'}
    xAxis = {"categories": data, "crosshair": 'true'}
    yAxis = {"title": {"text": 'Valor'}}
    return render_template('cobre.html', chartID=chartID, chart=chart,
                           series=series, title=title, xAxis=xAxis,
                           yAxis=yAxis)


@app.route('/lme/zinco')
def lme_zinco(chartID='chart_ID', chart_type='line', chart_height=350):
    chart = {"renderTo": chartID, "type": chart_type, "height": chart_height}
    series = [{"name": 'Zinco', "data": zinco}]
    title = {"text": 'Zinco'}
    xAxis = {"categories": data, "crosshair": 'true'}
    yAxis = {"title": {"text": 'Valor'}}
    return render_template('zinco.html', chartID=chartID, chart=chart,
                           series=series, title=title, xAxis=xAxis,
                           yAxis=yAxis)


@app.route('/lme/aluminio')
def lme_aluminio(chartID='chart_ID', chart_type='line', chart_height=350):
    chart = {"renderTo": chartID, "type": chart_type, "height": chart_height}
    series = [{"name": 'Alumínio', "data": aluminio}]
    title = {"text": 'Alumínio'}
    xAxis = {"categories": data, "crosshair": 'true'}
    yAxis = {"title": {"text": 'Valor'}}
    return render_template('aluminio.html', chartID=chartID, chart=chart,
                           series=series, title=title, xAxis=xAxis,
                           yAxis=yAxis)


@app.route('/lme/chumbo')
def lme_chumbo(chartID='chart_ID', chart_type='line', chart_height=350):
    chart = {"renderTo": chartID, "type": chart_type, "height": chart_height}
    series = [{"name": 'Chumbo', "data": chumbo}]
    title = {"text": 'Chumbo'}
    xAxis = {"categories": data, "crosshair": 'true'}
    yAxis = {"title": {"text": 'Valor'}}
    return render_template('chumbo.html', chartID=chartID, chart=chart,
                           series=series, title=title, xAxis=xAxis,
                           yAxis=yAxis)


@app.route('/lme/estanho')
def lme_estanho(chartID='chart_ID', chart_type='line', chart_height=350):
    chart = {"renderTo": chartID, "type": chart_type, "height": chart_height}
    series = [{"name": 'Estanho', "data": estanho}]
    title = {"text": 'Estanho'}
    xAxis = {"categories": data, "crosshair": 'true'}
    yAxis = {"title": {"text": 'Valor'}}
    return render_template('estanho.html', chartID=chartID, chart=chart,
                           series=series, title=title, xAxis=xAxis,
                           yAxis=yAxis)


@app.route('/lme/niquel')
def lme_niquel(chartID='chart_ID', chart_type='line', chart_height=350):
    chart = {"renderTo": chartID, "type": chart_type, "height": chart_height}
    series = [{"name": 'Níquel', "data": niquel}]
    title = {"text": 'Níquel'}
    xAxis = {"categories": data, "crosshair": 'true'}
    yAxis = {"title": {"text": 'Valor em USD por tonelada'}}
    return render_template('niquel.html', chartID=chartID, chart=chart,
                           series=series, title=title, xAxis=xAxis,
                           yAxis=yAxis)


@app.route('/lme/dolar')
def lme_dolar(chartID='chart_ID', chart_type='line', chart_height=350):
    chart = {"renderTo": chartID, "type": chart_type, "height": chart_height}
    series = [{"name": 'Dólar', "data": dolar}]
    title = {"text": 'Dólar'}
    xAxis = {"categories": data, "crosshair": 'true'}
    yAxis = {"title": {"text": 'Valor'}}
    return render_template('dolar.html', chartID=chartID, chart=chart,
                           series=series, title=title, xAxis=xAxis,
                           yAxis=yAxis)


@app.route('/lme/all')
def cotacao_completa(chartID='chart_ID', chart_type='line', chart_height=350):
    chart = {"renderTo": chartID, "type": chart_type, "height": chart_height}
    series = [{"name": 'Cobre', "data": cobre_completo},
              {"name": 'Zinco', "data": zinco_completo, "visible": 'false'},
              {"name": 'Alumínio', "data": aluminio_completo,
               "visible": 'false'},
              {"name": 'Chumbo', "data": chumbo_completo, "visible": 'false'},
              {"name": 'Estanho', "data": estanho_completo,
               "visible": 'false'},
              {"name": 'Níquel', "data": niquel_completo, "visible": 'false'},
              {"name": 'Dolar', "data": dolar_completo, "visible": 'false'}
              ]
    title = {"text": 'Cotação LME'}
    xAxis = {"categories": data_completo, "crosshair": 'true'}
    yAxis = {"title": {"text": 'Valor'}}
    return render_template('index.html', chartID=chartID, chart=chart,
                           series=series, title=title, xAxis=xAxis,
                           yAxis=yAxis)


@app.route('/lme/dashboard')
def deshboard(chartID='chart_ID', chart_type='line', chart_height=350):
    chart = {"renderTo": chartID, "type": chart_type, "height": chart_height}
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
    return render_template('dashboard.html', chartID=chartID, chart=chart,
                           series=series, title=title, xAxis=xAxis,
                           yAxis=yAxis)


@app.route('/lme/tabela')
def mostra_tabela():
    return render_template('mesclado.html')


@app.route('/summary', methods=['GET'])
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
            SELECT *
            FROM cotacao_lme
            WHERE "Dolar" IS NOT NULL
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


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
