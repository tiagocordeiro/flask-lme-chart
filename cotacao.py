#!/usr/bin/env python3
# coding: utf-8

from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import os
import pandas as pd
import sqlite3 as db
import quandl

quandl.ApiConfig.api_key = os.environ.get('QUANDL_KEY')

pd.options.display.float_format = '{:,.2f}'.format

pd.set_option('colheader_justify', 'right')

html_files = 'static'


def check_html_folder():
    if not os.path.exists(html_files):
        os.makedirs(html_files)


def cotacaoAtualizada():
    """ Pega a cotação atualizada da quandl
    :return: Salva arquivo cotacao-atual.csv e lme.db
    """
    check_html_folder()
    cnx = db.connect('lme.db')

    # Parametros de inicio e fim do periodo pode ser usado
    now = datetime.now()
    periodo = now - timedelta(weeks=4)
    #
    # start_date = periodo.strftime("%Y-%m-%d"),
    # end_date = now.strftime("%Y-%m-%d")

    merged_data = quandl.get(["LME/PR_CU.2", "LME/PR_ZI.2", "LME/PR_AL.2",
                              "LME/PR_PB.2", "LME/PR_TN.2", "LME/PR_NI.2",
                              "CURRFX/USDBRL.1"],
                             start_date=periodo,
                             end_date=now,
                             returns="pandas"
                             )

    todo_periodo = quandl.get(["LME/PR_CU.2", "LME/PR_ZI.2", "LME/PR_AL.2",
                               "LME/PR_PB.2", "LME/PR_TN.2", "LME/PR_NI.2",
                               "CURRFX/USDBRL.1"], start_date="2012-01-03",
                              returns="pandas")

    todo_periodo.columns = ['Cobre', 'Zinco', 'Aluminio', 'Chumbo',
                           'Estanho', 'Niquel', 'Dolar']

    merged_data.columns = ['Cobre', 'Zinco', 'Aluminio', 'Chumbo',
                           'Estanho', 'Niquel', 'Dolar']

    todo_periodo.to_csv('static/todo-periodo.csv', encoding='utf-8')

    merged_data.to_csv('static/cotacao-atual.csv', encoding='utf-8')

    # merged_data.to_sql('cotacoes', cnx, if_exists='replace')
    todo_periodo.to_sql('cotacoes', cnx, if_exists='replace')

    cnx.commit()
    print("Cotação atualizada...")
    cnx.close()


def pegaCotacao():
    cnx = db.connect('lme.db')
    df = pd.read_sql_query("select * from cotacoes", cnx)
    cnx.close()
    return df


def cotacaoPeriodo(qt_semanas=4):
    """ Retorna a cotação dos metais na London Metal Exchange
    Ex: cotacao_periodo(5)
    :param qt_semanas: Padrão 4 semanas, incluindo a semana atual.
    :return: Gera arquivos html
    """
    cnx = db.connect('lme.db')

    if not os.path.exists(html_files):
        os.makedirs(html_files)

    hoje = datetime.now()

    diadasemana = hoje.isoweekday()

    if diadasemana == 1:
        hoje = datetime.now() - timedelta(weeks=1)
    else:
        pass

    semana01_inicio = hoje - timedelta(days=hoje.isoweekday() - 1)
    semana01_fim = semana01_inicio + timedelta(days=4)

    semanas = {}

    semanas[1] = (semana01_inicio, semana01_fim)

    for i in range(2, qt_semanas + 1):
        semanas[i] = (semanas[i - 1][0] - timedelta(weeks=1),
                      semanas[i - 1][1] - timedelta(weeks=1))

    # cotacaoatual = pd.read_csv('cotacao-atual.csv')
    cotacaoatual = pd.read_sql_query("select * from cotacoes", cnx)

    cotacaoatual.columns = ['Data', 'Cobre', 'Zinco', 'Aluminio', 'Chumbo',
                            'Estanho', 'Niquel', 'Dolar']

    df = pd.DataFrame(cotacaoatual)

    df['Data'] = pd.to_datetime(df['Data'])

    df = df.set_index(df['Data'])

    df = df.drop('Data', axis=1)

    df.fillna(method='ffill', inplace=True)

    datas = qt_semanas

    # imprime na tela
    for i in range(datas, 0, -1):
        print('\u2554' + ('\u2550' * 33) +
              '\u2566' + ('\u2550' * 20) +
              '\u2566' + ('\u2550' * 17) + '\u2557')

        print('\u2551 Semana do ano:', semanas[i][0].strftime("%U"), ' ' * 13,
              '\u2551 Início:', semanas[i][0].strftime("%d-%m-%Y"),
              '\u2551 Fim:', semanas[i][1].strftime("%d-%m-%Y"), '\u2551')

        print('\u255A' + ('\u2550' * 33) + '\u2569' + ('\u2550' * 20) +
              '\u2569' + ('\u2550' * 17) + '\u255D')

        print(df[semanas[i][0].strftime("%Y-%m-%d"):semanas[i][1].strftime(
            "%Y-%m-%d")])

        media_semana = df[semanas[i][0].strftime("%Y-%m-%d"):semanas[i][
            1].strftime("%Y-%m-%d")]

        media_semana = pd.DataFrame(media_semana.mean())

        media_semana_tela = media_semana
        media_semana_tela.rename(columns={0: 'Média:    '}, inplace=True)
        media_semana_pivot = pd.pivot_table(media_semana_tela,
                                            columns=['Cobre', 'Zinco',
                                                     'Aluminio', 'Chumbo',
                                                     'Estanho', 'Niquel',
                                                     'Dolar'])

        media_semana_pivot = media_semana_pivot[
            ['Cobre', 'Zinco', 'Aluminio', 'Chumbo', 'Estanho', 'Niquel',
             'Dolar']]

        print('\u2550' * 73)
        print(media_semana_pivot)
        print('\n')

    # Salva HTML Semana
    for i in range(datas, 0, -1):
        # Pode ser usado outro local para salvar os HTML
        # Ex: ../public_html/static/
        # versão com o número da semana do ano
        # fo = open('static/semana'
        # + str(semanas[i][0].strftime("%U")) + '.html', "w")
        fo = open('static/semana' + '{num:02d}'.format(num=i) + '.html', 'w')
        fo.write(df[semanas[i][0].strftime("%Y-%m-%d"):
        semanas[i][1].strftime("%Y-%m-%d")].to_html(
            classes=['semanal', 'table-striped', 'table-responsive']))
        fo.close()

    # Salva HTML da Média Semanal
    for i in range(datas, 0, -1):
        media_semana = df[semanas[i][0].strftime("%Y-%m-%d"):
        semanas[i][1].strftime("%Y-%m-%d")]
        media_semana = pd.DataFrame(media_semana.mean())
        media_semana.rename(
            columns={0: 'Semana:' + semanas[i][0].strftime("%U")},
            inplace=True)
        media_semana_pivot = pd.pivot_table(media_semana,
                                            columns=['Cobre', 'Zinco',
                                                     'Aluminio', 'Chumbo',
                                                     'Estanho', 'Niquel',
                                                     'Dolar'])
        media_semana_pivot = media_semana_pivot[
            ['Cobre', 'Zinco', 'Aluminio', 'Chumbo', 'Estanho', 'Niquel',
             'Dolar']]
        # versão com número da semana do ano
        # fo = open('static/semana' + str(semanas[i][0].strftime("%U")) +
        #  'media.html', "w")
        fo = open('static/semana' + '{num:02d}'.format(num=i) + 'media.html',
                  'w')
        fo.write(media_semana_pivot.to_html(
            classes=['semanal', 'table-striped', 'table-responsive']))
        fo.close()

        # return 'exibindo {} semanas'.format(len(semanas))
        cnx.close()


def merge_html():
    #TODO Melhorar função com loop

    htmls01 = open("static/semana01.html", "r").read()
    htmls01m = open("static/semana01media.html", "r").read()
    htmls02 = open("static/semana02.html", "r").read()
    htmls02m = open("static/semana02media.html", "r").read()
    htmls03 = open("static/semana03.html", "r").read()
    htmls03m = open("static/semana03media.html", "r").read()
    htmls04 = open("static/semana04.html", "r").read()
    htmls04m = open("static/semana04media.html", "r").read()

    # Limpeza de tabelas e merge por semana (Dias da semana + Media da Semana)
    htmls01 = htmls01.replace(
        '<table border="1" class="dataframe semanal table-striped table-responsive">',
        '<table style="text-align: right;" width="100%" border="1" class="dataframe semanal table-striped table-responsive">')

    htmls01 = htmls01.replace('<th></th>', '<th>Data</th>')

    htmls01m = htmls01m.replace('<tr style="text-align: right;">',
                                '<tr style="text-align: right; background-color: #d4c97e !important;">')

    htmls01m = htmls01m.replace('<th></th>', '<th>Média</th>')

    htmls01m = htmls01m.replace('<tr>', '<tr class="media" style="background-color: #d4c97e !important;">')

    htmls01 = htmls01.replace('</table>', '')

    htmls01m = htmls01m.replace(
        '<table border="1" class="dataframe semanal table-striped table-responsive">',
        '')

    htmls01merged = htmls01 + htmls01m

    #TODO padrão de data deve ser definido com varialvel e usando strftime
    #Alterando datas para o padrão pt_BR (hard mode) Semana 01
    htmls01merged = BeautifulSoup(htmls01merged, 'html.parser')
    datas = htmls01merged.findAll('th')
    tabela = htmls01merged.find('table')
    colunadata = tabela.find('tbody').findAll('th')

    for data in colunadata:
        databr = data.string.split("-")
        data.string = str(databr[2]+"/"+databr[1]+"/"+databr[0])

    htmls01merged = str(htmls01merged)


    # Limpeza de tabelas e merge por semana (Dias da semana + Media da Semana)
    htmls02 = htmls02.replace(
        '<table border="1" class="dataframe semanal table-striped table-responsive">',
        '<table style="text-align: right;" width="100%" border="1" class="dataframe semanal table-striped table-responsive">')

    htmls02 = htmls02.replace('<th></th>', '<th>Data</th>')

    htmls02m = htmls02m.replace('<tr style="text-align: right;">',
                                '<tr style="text-align: right; background-color: #d4c97e !important;">')

    htmls02m = htmls02m.replace('<th></th>', '<th>Média</th>')

    htmls02m = htmls02m.replace('<tr>', '<tr class="media" style="background-color: #d4c97e !important;">')

    htmls02 = htmls02.replace('</table>', '')

    htmls02m = htmls02m.replace(
        '<table border="1" class="dataframe semanal table-striped table-responsive">',
        '')

    htmls02merged = htmls02 + htmls02m

    # Alterando datas para o padrão pt_BR (hard mode) Semana 02
    htmls02merged = BeautifulSoup(htmls02merged, 'html.parser')
    datas = htmls02merged.findAll('th')
    tabela = htmls02merged.find('table')
    colunadata = tabela.find('tbody').findAll('th')

    for data in colunadata:
        databr = data.string.split("-")
        data.string = str(databr[2] + "/" + databr[1] + "/" + databr[0])

    htmls02merged = str(htmls02merged)

    # Limpeza de tabelas e merge por semana (Dias da semana + Media da Semana)
    htmls03 = htmls03.replace(
        '<table border="1" class="dataframe semanal table-striped table-responsive">',
        '<table style="text-align: right;" width="100%" border="1" class="dataframe semanal table-striped table-responsive">')

    htmls03 = htmls03.replace('<th></th>', '<th>Data</th>')

    htmls03m = htmls03m.replace('<tr style="text-align: right;">',
                                '<tr style="text-align: right; background-color: #d4c97e !important;">')

    htmls03m = htmls03m.replace('<th></th>', '<th>Média</th>')

    htmls03m = htmls03m.replace('<tr>', '<tr class="media" style="background-color: #d4c97e !important;">')

    htmls03 = htmls03.replace('</table>', '')

    htmls03m = htmls03m.replace(
        '<table border="1" class="dataframe semanal table-striped table-responsive">',
        '')

    htmls03merged = htmls03 + htmls03m

    # Alterando datas para o padrão pt_BR (hard mode) Semana 03
    htmls03merged = BeautifulSoup(htmls03merged, 'html.parser')
    datas = htmls03merged.findAll('th')
    tabela = htmls03merged.find('table')
    colunadata = tabela.find('tbody').findAll('th')

    for data in colunadata:
        databr = data.string.split("-")
        data.string = str(databr[2] + "/" + databr[1] + "/" + databr[0])

    htmls03merged = str(htmls03merged)

    # Limpeza de tabelas e merge por semana (Dias da semana + Media da Semana)
    htmls04 = htmls04.replace(
        '<table border="1" class="dataframe semanal table-striped table-responsive">',
        '<table style="text-align: right;" width="100%" border="1" class="dataframe semanal table-striped table-responsive">')

    htmls04 = htmls04.replace('<th></th>', '<th>Data</th>')

    htmls04m = htmls04m.replace('<tr style="text-align: right;">',
                                '<tr style="text-align: right; background-color: #d4c97e !important;">')

    htmls04m = htmls04m.replace('<th></th>', '<th>Média</th>')

    htmls04m = htmls04m.replace('<tr>', '<tr class="media" style="background-color: #d4c97e !important;">')

    htmls04 = htmls04.replace('</table>', '')

    htmls04m = htmls04m.replace(
        '<table border="1" class="dataframe semanal table-striped table-responsive">',
        '')

    htmls04merged = htmls04 + htmls04m

    # Alterando datas para o padrão pt_BR (hard mode) Semana 01
    htmls04merged = BeautifulSoup(htmls04merged, 'html.parser')
    datas = htmls04merged.findAll('th')
    tabela = htmls04merged.find('table')
    colunadata = tabela.find('tbody').findAll('th')

    for data in colunadata:
        databr = data.string.split("-")
        data.string = str(databr[2] + "/" + databr[1] + "/" + databr[0])

    htmls04merged = str(htmls04merged)

    mesclado = BeautifulSoup(
        htmls04merged + htmls03merged + htmls02merged + htmls01merged,
        'html.parser')

    # mesclado = BeautifulSoup(htmls01 + htmls01m, 'html.parser')

    mesclado.find_all('th')[0].string = 'Data'

    mesclado.find_all('tr')[1].string = ''

    mesclado.find_all('tr')[10].string = ''

    mesclado.find_all('tr')[19].string = ''

    mesclado.find_all('tr')[28].string = ''

    fo = open('templates/mesclado.html', "w")
    fo.write(mesclado.prettify())
    fo.close()


if __name__ == '__main__':
    # cotacao = pegaCotacao()
    # print(cotacao)
    # cotacaoPeriodo(4)
    cotacaoAtualizada()
    cotacaoPeriodo(4)
    merge_html()
