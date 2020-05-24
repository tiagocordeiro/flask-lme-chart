Flask lme
=========
Cotação London Metal Exchange com Flask
---------------------------------------

[![Build Status](https://travis-ci.org/tiagocordeiro/flask-lme-chart.svg?branch=master)](https://travis-ci.org/tiagocordeiro/flask-lme-chart)
[![Updates](https://pyup.io/repos/github/tiagocordeiro/flask-lme-chart/shield.svg)](https://pyup.io/repos/github/tiagocordeiro/flask-lme-chart/)
[![codecov](https://codecov.io/gh/tiagocordeiro/flask-lme-chart/branch/master/graph/badge.svg)](https://codecov.io/gh/tiagocordeiro/flask-lme-chart)
[![Python 3](https://pyup.io/repos/github/tiagocordeiro/flask-lme-chart/python-3-shield.svg)](https://pyup.io/repos/github/tiagocordeiro/flask-lme-chart/)
[![Cobre](https://img.shields.io/badge/LME-Cobre-green.svg)](https://www.quandl.com/data/LME/PR_CU-Copper-Prices)
[![Zinco](https://img.shields.io/badge/LME-Zinco-green.svg)](https://www.quandl.com/data/LME/PR_ZI-Zinc-Prices)
[![Alumínio](https://img.shields.io/badge/LME-Aluminio-green.svg)](https://www.quandl.com/data/LME/PR_AL-Aluminum-Prices)
[![Chumbo](https://img.shields.io/badge/LME-Chumbo-green.svg)](https://www.quandl.com/data/LME/PR_PB-Lead-Prices)
[![Estanho](https://img.shields.io/badge/LME-Estanho-green.svg)](https://www.quandl.com/data/LME/PR_TN-Tin-Prices)
[![Níquel](https://img.shields.io/badge/LME-Niquel-green.svg)](https://www.quandl.com/data/LME/PR_NI-Nickel-Prices)

## Live demo
https://lme-flask.herokuapp.com/

### Outros Endpoints
```
/cotacao
/grafico
/json/v2
/json/v3
/summary
```

Você precisa de uma conta (gratuita) na [Quandl](https://www.quandl.com)

-  Register an account on Quandl
-  After logging in, click on Me and then Account settings to find the API key

[Quandl in Github](https://github.com/quandl/quandl-python)

### Como rodar o projeto

* Clone esse repositório.
* Crie um virtualenv com Python 3.
* Ative o virtualenv.
* Instale as dependências.
* Configure as variáveis de ambiente.

```
git clone https://github.com/tiagocordeiro/flask-lme-chart.git
cd flask-lme-chart
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp contrib/env-sample .env
```

### Rodar em ambiente de desenvolvimento
Para rodar o projeto localmente
```
flask run
```

Banco de dados para desenvolvimento com Docker
```
docker-compose up -d
```

### Testes, contribuição e dependências de desenvolvimento
Para instalar as dependências de desenvolvimento
```
pip install -r requirements-dev.txt
```

Para rodar os testes
```
pytest
```

Verificando o `Code style`
```
pycodestyle .
flake8 .
```

#### Thanx
[ ~ Dependencies scanned by PyUp.io ~ ]