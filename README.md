# 📊 Dashboard Financeiro

> Aplicação completa para controle de finanças pessoais com cadastro de receitas e despesas, gráficos interativos e relatórios exportáveis.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=flat&logo=flask&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3?style=flat&logo=bootstrap&logoColor=white)
![Chart.js](https://img.shields.io/badge/Chart.js-4.4-FF6384?style=flat&logo=chart.js&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=flat&logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

---

## 🚀 Funcionalidades

- **📊 Dashboard Principal** — Cards de resumo (Saldo, Receitas, Despesas) + 3 gráficos interativos (Pizza, Barras, Linha)
- **💰 Gestão de Transações** — CRUD completo com filtros por tipo, categoria e período
- **📈 Relatórios Exportáveis** — Exportação para CSV e Excel (.xlsx), compatível com Power BI
- **🔗 API REST** — Endpoints JSON para alimentar os gráficos e operações CRUD
- **🎨 Tema Dark** — Interface responsiva com Bootstrap 5 dark theme

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Uso |
|---|---|
| **Python 3.10+** | Backend e lógica de negócio |
| **Flask** | Framework web, rotas, templates Jinja2, API REST |
| **Flask-SQLAlchemy** | ORM para banco de dados |
| **SQLite** | Banco de dados local |
| **Chart.js** | Gráficos interativos (pizza, barras, linha) |
| **Bootstrap 5** | UI responsiva com tema dark |
| **openpyxl** | Exportação para Excel (.xlsx) |
| **Power BI** | Compatibilidade via exportação CSV/Excel |

---

## 📁 Estrutura do Projeto

```
├── app.py                     # Aplicação principal Flask
├── config.py                  # Configurações (DB, Secret Key)
├── requirements.txt           # Dependências Python
├── seed.py                    # Script para popular banco de dados
├── models/
│   └── models.py              # Modelos SQLAlchemy (Transaction)
├── routes/
│   ├── dashboard.py           # Rotas do dashboard principal
│   ├── transactions.py        # CRUD de receitas e despesas
│   ├── reports.py             # Exportação de relatórios
│   └── api.py                 # API JSON para os gráficos Chart.js
├── templates/
│   ├── base.html              # Template base com navbar e layout
│   ├── dashboard.html         # Dashboard principal com gráficos
│   ├── transactions.html      # Listagem de transações com CRUD
│   ├── edit_transaction.html  # Formulário de edição
│   └── reports.html           # Relatórios exportáveis
└── static/
    ├── css/
    │   └── style.css          # Estilos customizados (tema escuro)
    └── js/
        ├── charts.js          # Gráficos interativos com Chart.js
        └── app.js             # Lógica frontend (sidebar, modais)
```

---

## ⚙️ Como Instalar e Rodar Localmente

### Pré-requisitos

- Python 3.10 ou superior
- pip

### Passo a passo

```bash
# 1. Clone o repositório
git clone https://github.com/Beto2024/09-Dashboard-Financeiro.git
cd 09-Dashboard-Financeiro

# 2. Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. (Opcional) Popule o banco com dados de demonstração
python seed.py

# 5. Inicie o servidor
python app.py
```

Acesse: **http://localhost:5000**

---

## 🔗 API Endpoints

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/summary` | Resumo financeiro (saldo, receitas, despesas) |
| `GET` | `/api/transactions` | Lista de transações (suporta filtros por query params) |
| `POST` | `/api/transactions` | Criar nova transação |
| `PUT` | `/api/transactions/<id>` | Atualizar transação |
| `DELETE` | `/api/transactions/<id>` | Deletar transação |
| `GET` | `/api/chart/expenses-by-category` | Dados para gráfico de pizza |
| `GET` | `/api/chart/monthly-comparison` | Dados para gráfico de barras |
| `GET` | `/api/chart/balance-evolution` | Dados para gráfico de linha |

### Parâmetros de filtro (query params):
- `month` — número do mês (1–12)
- `year` — ano (ex: 2025)
- `type` — `Receita` ou `Despesa`
- `category` — nome da categoria

---

## 📤 Como Exportar para Power BI

1. Acesse a página **Relatórios** (`/reports`)
2. Aplique os filtros desejados (período, tipo, categoria)
3. Clique em **Exportar CSV** ou **Exportar Excel (.xlsx)**
4. No **Power BI Desktop**:
   - Clique em **Obter Dados** → **Texto/CSV** (ou Excel)
   - Selecione o arquivo exportado e clique em **Carregar**
   - Use as colunas `Tipo`, `Categoria`, `Valor` e `Data` para criar seus visuais
5. Crie medidas DAX para cálculos personalizados:
   ```dax
   Total Receitas = CALCULATE(SUM(transacoes[Valor]), transacoes[Tipo] = "Receita")
   Total Despesas = CALCULATE(SUM(transacoes[Valor]), transacoes[Tipo] = "Despesa")
   Saldo = [Total Receitas] - [Total Despesas]
   ```

---

## 🌱 Dados de Demonstração

Execute `python seed.py` para popular o banco com ~55 transações realistas distribuídas nos últimos 6 meses, incluindo:

- **Receitas:** Salário (R$ 5.500/mês), Freelance, Investimentos (dividendos, CDB)
- **Despesas:** Moradia (Aluguel), Alimentação, Transporte, Saúde, Educação, Lazer

---

## 📄 Licença

Distribuído sob a licença **MIT**. Veja `LICENSE` para mais informações.

---

*Desenvolvido por **[Beto2024](https://github.com/Beto2024)** como projeto de portfólio.*
