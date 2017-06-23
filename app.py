from flask import Flask, render_template
import pandas as pd

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


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080, passthrough_errors=True)
