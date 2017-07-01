from flask import Flask, render_template
import pandas as pd
import os

app = Flask(__name__)

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


@app.route('/')
@app.route('/index')
@app.route('/lme')
def index(chartID='chart_ID', chart_type='line', chart_height=350):
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
    return render_template('index.html', chartID=chartID, chart=chart,
                           series=series, title=title, xAxis=xAxis, yAxis=yAxis)

@app.route('/lme/cobre')
def lme_cobre(chartID='chart_ID', chart_type='line', chart_height=350):
    chart = {"renderTo": chartID, "type": chart_type, "height": chart_height}
    series = [{"name": 'Cobre', "data": cobre}]
    title = {"text": 'Cobre'}
    xAxis = {"categories": data, "crosshair": 'true'}
    yAxis = {"title": {"text": 'Valor'}}
    return render_template('cobre.html', chartID=chartID, chart=chart,
                           series=series, title=title, xAxis=xAxis, yAxis=yAxis)


@app.route('/lme/zinco')
def lme_zinco(chartID='chart_ID', chart_type='line', chart_height=350):
    chart = {"renderTo": chartID, "type": chart_type, "height": chart_height}
    series = [{"name": 'Zinco', "data": zinco}]
    title = {"text": 'Zinco'}
    xAxis = {"categories": data, "crosshair": 'true'}
    yAxis = {"title": {"text": 'Valor'}}
    return render_template('zinco.html', chartID=chartID, chart=chart,
                           series=series, title=title, xAxis=xAxis, yAxis=yAxis)


@app.route('/lme/aluminio')
def lme_aluminio(chartID='chart_ID', chart_type='line', chart_height=350):
    chart = {"renderTo": chartID, "type": chart_type, "height": chart_height}
    series = [{"name": 'Alumínio', "data": aluminio}]
    title = {"text": 'Alumínio'}
    xAxis = {"categories": data, "crosshair": 'true'}
    yAxis = {"title": {"text": 'Valor'}}
    return render_template('aluminio.html', chartID=chartID, chart=chart,
                           series=series, title=title, xAxis=xAxis, yAxis=yAxis)


@app.route('/lme/chumbo')
def lme_chumbo(chartID='chart_ID', chart_type='line', chart_height=350):
    chart = {"renderTo": chartID, "type": chart_type, "height": chart_height}
    series = [{"name": 'Chumbo', "data": chumbo}]
    title = {"text": 'Chumbo'}
    xAxis = {"categories": data, "crosshair": 'true'}
    yAxis = {"title": {"text": 'Valor'}}
    return render_template('chumbo.html', chartID=chartID, chart=chart,
                           series=series, title=title, xAxis=xAxis, yAxis=yAxis)


@app.route('/lme/estanho')
def lme_estanho(chartID='chart_ID', chart_type='line', chart_height=350):
    chart = {"renderTo": chartID, "type": chart_type, "height": chart_height}
    series = [{"name": 'Estanho', "data": estanho}]
    title = {"text": 'Estanho'}
    xAxis = {"categories": data, "crosshair": 'true'}
    yAxis = {"title": {"text": 'Valor'}}
    return render_template('estanho.html', chartID=chartID, chart=chart,
                           series=series, title=title, xAxis=xAxis, yAxis=yAxis)


@app.route('/lme/niquel')
def lme_niquel(chartID='chart_ID', chart_type='line', chart_height=350):
    chart = {"renderTo": chartID, "type": chart_type, "height": chart_height}
    series = [{"name": 'Níquel', "data": niquel}]
    title = {"text": 'Níquel'}
    xAxis = {"categories": data, "crosshair": 'true'}
    yAxis = {"title": {"text": 'Valor em USD por tonelada'}}
    return render_template('niquel.html', chartID=chartID, chart=chart,
                           series=series, title=title, xAxis=xAxis, yAxis=yAxis)


@app.route('/lme/dolar')
def lme_dolar(chartID='chart_ID', chart_type='line', chart_height=350):
    chart = {"renderTo": chartID, "type": chart_type, "height": chart_height}
    series = [{"name": 'Dólar', "data": dolar}]
    title = {"text": 'Dólar'}
    xAxis = {"categories": data, "crosshair": 'true'}
    yAxis = {"title": {"text": 'Valor'}}
    return render_template('dolar.html', chartID=chartID, chart=chart,
                           series=series, title=title, xAxis=xAxis, yAxis=yAxis)


@app.route('/lme/tabela')
def mostra_tabela():
    return render_template('mesclado.html')


@app.route('/lme/periodo/<data_inicio>/<data_fim>')
def mostra_periodo(data_inicio, data_fim):
    return f'Cotação do perídodo: {data_inicio} até {data_fim}'


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
