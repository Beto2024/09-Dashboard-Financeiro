"""
seed.py — Popula o banco de dados com transações de demonstração.
Execute: python seed.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from models.models import db, Transaction
from datetime import date, timedelta
import random

app = create_app()

DEMO_TRANSACTIONS = [
    # --- Mês -5 ---
    {"description": "Salário", "amount": 5500.00, "type": "Receita", "category": "Salário", "day_offset": -150},
    {"description": "Aluguel", "amount": 1200.00, "type": "Despesa", "category": "Moradia", "day_offset": -148},
    {"description": "Supermercado Pão de Açúcar", "amount": 420.50, "type": "Despesa", "category": "Alimentação", "day_offset": -145},
    {"description": "Uber", "amount": 65.00, "type": "Despesa", "category": "Transporte", "day_offset": -143},
    {"description": "Netflix", "amount": 39.90, "type": "Despesa", "category": "Lazer", "day_offset": -140},
    {"description": "Plano de Saúde", "amount": 280.00, "type": "Despesa", "category": "Saúde", "day_offset": -138},
    {"description": "Freelance — Logo Design", "amount": 800.00, "type": "Receita", "category": "Freelance", "day_offset": -135},
    {"description": "Farmácia", "amount": 95.30, "type": "Despesa", "category": "Saúde", "day_offset": -133},
    {"description": "Restaurante", "amount": 110.00, "type": "Despesa", "category": "Alimentação", "day_offset": -130},

    # --- Mês -4 ---
    {"description": "Salário", "amount": 5500.00, "type": "Receita", "category": "Salário", "day_offset": -120},
    {"description": "Aluguel", "amount": 1200.00, "type": "Despesa", "category": "Moradia", "day_offset": -118},
    {"description": "Supermercado Extra", "amount": 380.00, "type": "Despesa", "category": "Alimentação", "day_offset": -115},
    {"description": "Gasolina", "amount": 200.00, "type": "Despesa", "category": "Transporte", "day_offset": -112},
    {"description": "Curso Python — Udemy", "amount": 89.90, "type": "Despesa", "category": "Educação", "day_offset": -110},
    {"description": "Freelance — Site Institucional", "amount": 1500.00, "type": "Receita", "category": "Freelance", "day_offset": -108},
    {"description": "Cinema e Lazer", "amount": 150.00, "type": "Despesa", "category": "Lazer", "day_offset": -105},
    {"description": "Conta de Luz", "amount": 145.00, "type": "Despesa", "category": "Moradia", "day_offset": -102},
    {"description": "Internet", "amount": 99.90, "type": "Despesa", "category": "Moradia", "day_offset": -100},
    {"description": "Dividendos — Ações", "amount": 320.00, "type": "Receita", "category": "Investimentos", "day_offset": -98},

    # --- Mês -3 ---
    {"description": "Salário", "amount": 5500.00, "type": "Receita", "category": "Salário", "day_offset": -90},
    {"description": "13º Salário (parcial)", "amount": 2750.00, "type": "Receita", "category": "Salário", "day_offset": -88},
    {"description": "Aluguel", "amount": 1200.00, "type": "Despesa", "category": "Moradia", "day_offset": -87},
    {"description": "Supermercado", "amount": 445.70, "type": "Despesa", "category": "Alimentação", "day_offset": -85},
    {"description": "IPTU (parcela)", "amount": 380.00, "type": "Despesa", "category": "Moradia", "day_offset": -82},
    {"description": "Médico — Consulta", "amount": 250.00, "type": "Despesa", "category": "Saúde", "day_offset": -80},
    {"description": "Show — Ingresso", "amount": 200.00, "type": "Despesa", "category": "Lazer", "day_offset": -78},
    {"description": "Freelance — App Mobile", "amount": 2200.00, "type": "Receita", "category": "Freelance", "day_offset": -75},
    {"description": "Livros Técnicos", "amount": 180.00, "type": "Despesa", "category": "Educação", "day_offset": -72},
    {"description": "Delivery iFood", "amount": 85.00, "type": "Despesa", "category": "Alimentação", "day_offset": -70},

    # --- Mês -2 ---
    {"description": "Salário", "amount": 5500.00, "type": "Receita", "category": "Salário", "day_offset": -60},
    {"description": "Aluguel", "amount": 1200.00, "type": "Despesa", "category": "Moradia", "day_offset": -58},
    {"description": "Supermercado Atacadão", "amount": 520.00, "type": "Despesa", "category": "Alimentação", "day_offset": -55},
    {"description": "Manutenção Carro", "amount": 350.00, "type": "Despesa", "category": "Transporte", "day_offset": -52},
    {"description": "Plano de Saúde", "amount": 280.00, "type": "Despesa", "category": "Saúde", "day_offset": -50},
    {"description": "Spotify Premium", "amount": 21.90, "type": "Despesa", "category": "Lazer", "day_offset": -48},
    {"description": "Rendimento CDB", "amount": 420.00, "type": "Receita", "category": "Investimentos", "day_offset": -45},
    {"description": "Academia", "amount": 110.00, "type": "Despesa", "category": "Saúde", "day_offset": -42},
    {"description": "Restaurante Japones", "amount": 180.00, "type": "Despesa", "category": "Alimentação", "day_offset": -40},
    {"description": "Curso JavaScript — DIO", "amount": 59.90, "type": "Despesa", "category": "Educação", "day_offset": -38},

    # --- Mês -1 ---
    {"description": "Salário", "amount": 5500.00, "type": "Receita", "category": "Salário", "day_offset": -30},
    {"description": "Aluguel", "amount": 1200.00, "type": "Despesa", "category": "Moradia", "day_offset": -28},
    {"description": "Supermercado", "amount": 398.00, "type": "Despesa", "category": "Alimentação", "day_offset": -25},
    {"description": "Passagem Aérea Viagem", "amount": 780.00, "type": "Despesa", "category": "Lazer", "day_offset": -22},
    {"description": "Freelance — Consultoria", "amount": 1200.00, "type": "Receita", "category": "Freelance", "day_offset": -20},
    {"description": "Conta de Água", "amount": 75.00, "type": "Despesa", "category": "Moradia", "day_offset": -18},
    {"description": "Delivery", "amount": 65.00, "type": "Despesa", "category": "Alimentação", "day_offset": -15},
    {"description": "Dividendos FII", "amount": 280.00, "type": "Receita", "category": "Investimentos", "day_offset": -12},
    {"description": "Vestuário — Roupa", "amount": 320.00, "type": "Despesa", "category": "Outros", "day_offset": -10},

    # --- Mês atual ---
    {"description": "Salário", "amount": 5500.00, "type": "Receita", "category": "Salário", "day_offset": -5},
    {"description": "Aluguel", "amount": 1200.00, "type": "Despesa", "category": "Moradia", "day_offset": -4},
    {"description": "Supermercado", "amount": 310.00, "type": "Despesa", "category": "Alimentação", "day_offset": -3},
    {"description": "Combustível", "amount": 180.00, "type": "Despesa", "category": "Transporte", "day_offset": -2},
    {"description": "Freelance — Dashboard Web", "amount": 1800.00, "type": "Receita", "category": "Freelance", "day_offset": -1},
    {"description": "Restaurante Almoço", "amount": 55.00, "type": "Despesa", "category": "Alimentação", "day_offset": 0},
]


def seed():
    with app.app_context():
        existing = Transaction.query.count()
        if existing > 0:
            print(f"⚠️  Banco já possui {existing} transações. Limpando para novo seed...")
            Transaction.query.delete()
            db.session.commit()

        today = date.today()
        for item in DEMO_TRANSACTIONS:
            transaction = Transaction(
                description=item["description"],
                amount=item["amount"],
                date=today + timedelta(days=item["day_offset"]),
                type=item["type"],
                category=item["category"],
            )
            db.session.add(transaction)

        db.session.commit()
        total = Transaction.query.count()
        print(f"✅ Seed concluído! {total} transações inseridas no banco.")
        print(f"   Execute 'flask run' ou 'python app.py' para iniciar o servidor.")


if __name__ == "__main__":
    seed()
