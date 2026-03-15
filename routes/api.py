from flask import Blueprint, jsonify, request
from models.models import db, Transaction
from sqlalchemy import extract, func
from datetime import datetime, date, timedelta
import calendar

api_bp = Blueprint("api", __name__, url_prefix="/api")

MONTH_NAMES = [
    "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
    "Jul", "Ago", "Set", "Out", "Nov", "Dez"
]


def parse_filters():
    month = request.args.get("month", type=int)
    year = request.args.get("year", type=int)
    return month, year


@api_bp.route("/summary")
def summary():
    month, year = parse_filters()
    today = date.today()
    month = month or today.month
    year = year or today.year

    transactions = Transaction.query.filter(
        extract("month", Transaction.date) == month,
        extract("year", Transaction.date) == year,
    ).all()

    total_income = sum(t.amount for t in transactions if t.type == "Receita")
    total_expense = sum(t.amount for t in transactions if t.type == "Despesa")
    balance = total_income - total_expense

    return jsonify({
        "month": month,
        "year": year,
        "total_income": round(total_income, 2),
        "total_expense": round(total_expense, 2),
        "balance": round(balance, 2),
        "transaction_count": len(transactions),
    })


@api_bp.route("/transactions", methods=["GET"])
def list_transactions():
    month, year = parse_filters()
    t_type = request.args.get("type")
    category = request.args.get("category")

    query = Transaction.query

    if month:
        query = query.filter(extract("month", Transaction.date) == month)
    if year:
        query = query.filter(extract("year", Transaction.date) == year)
    if t_type:
        query = query.filter(Transaction.type == t_type)
    if category:
        query = query.filter(Transaction.category == category)

    transactions = query.order_by(Transaction.date.desc()).all()
    return jsonify([t.to_dict() for t in transactions])


@api_bp.route("/transactions", methods=["POST"])
def create_transaction():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    try:
        transaction = Transaction(
            description=data["description"],
            amount=float(data["amount"]),
            date=datetime.strptime(data["date"], "%Y-%m-%d").date(),
            type=data["type"],
            category=data["category"],
        )
        db.session.add(transaction)
        db.session.commit()
        return jsonify(transaction.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@api_bp.route("/transactions/<int:transaction_id>", methods=["PUT"])
def update_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    try:
        if "description" in data:
            transaction.description = data["description"]
        if "amount" in data:
            transaction.amount = float(data["amount"])
        if "date" in data:
            transaction.date = datetime.strptime(data["date"], "%Y-%m-%d").date()
        if "type" in data:
            transaction.type = data["type"]
        if "category" in data:
            transaction.category = data["category"]
        db.session.commit()
        return jsonify(transaction.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@api_bp.route("/transactions/<int:transaction_id>", methods=["DELETE"])
def delete_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    try:
        db.session.delete(transaction)
        db.session.commit()
        return jsonify({"message": "Transação excluída com sucesso"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@api_bp.route("/chart/expenses-by-category")
def expenses_by_category():
    month, year = parse_filters()
    today = date.today()
    month = month or today.month
    year = year or today.year

    results = db.session.query(
        Transaction.category,
        func.sum(Transaction.amount).label("total")
    ).filter(
        Transaction.type == "Despesa",
        extract("month", Transaction.date) == month,
        extract("year", Transaction.date) == year,
    ).group_by(Transaction.category).all()

    labels = [r.category for r in results]
    data = [round(r.total, 2) for r in results]

    colors = [
        "#7c3aed", "#06b6d4", "#f59e0b", "#ef4444",
        "#10b981", "#6366f1", "#ec4899", "#14b8a6",
        "#f97316", "#8b5cf6"
    ]

    return jsonify({
        "labels": labels,
        "datasets": [{
            "data": data,
            "backgroundColor": colors[:len(labels)],
        }]
    })


@api_bp.route("/chart/monthly-comparison")
def monthly_comparison():
    year = request.args.get("year", date.today().year, type=int)

    income_results = db.session.query(
        extract("month", Transaction.date).label("month"),
        func.sum(Transaction.amount).label("total")
    ).filter(
        Transaction.type == "Receita",
        extract("year", Transaction.date) == year,
    ).group_by("month").all()

    expense_results = db.session.query(
        extract("month", Transaction.date).label("month"),
        func.sum(Transaction.amount).label("total")
    ).filter(
        Transaction.type == "Despesa",
        extract("year", Transaction.date) == year,
    ).group_by("month").all()

    income_map = {int(r.month): round(r.total, 2) for r in income_results}
    expense_map = {int(r.month): round(r.total, 2) for r in expense_results}

    labels = MONTH_NAMES
    incomes = [income_map.get(m, 0) for m in range(1, 13)]
    expenses = [expense_map.get(m, 0) for m in range(1, 13)]

    return jsonify({
        "labels": labels,
        "datasets": [
            {
                "label": "Receitas",
                "data": incomes,
                "backgroundColor": "rgba(40, 199, 111, 0.7)",
                "borderColor": "#28c76f",
            },
            {
                "label": "Despesas",
                "data": expenses,
                "backgroundColor": "rgba(234, 84, 85, 0.7)",
                "borderColor": "#ea5455",
            },
        ]
    })


@api_bp.route("/chart/balance-evolution")
def balance_evolution():
    year = request.args.get("year", date.today().year, type=int)

    income_results = db.session.query(
        extract("month", Transaction.date).label("month"),
        func.sum(Transaction.amount).label("total")
    ).filter(
        Transaction.type == "Receita",
        extract("year", Transaction.date) == year,
    ).group_by("month").all()

    expense_results = db.session.query(
        extract("month", Transaction.date).label("month"),
        func.sum(Transaction.amount).label("total")
    ).filter(
        Transaction.type == "Despesa",
        extract("year", Transaction.date) == year,
    ).group_by("month").all()

    income_map = {int(r.month): r.total for r in income_results}
    expense_map = {int(r.month): r.total for r in expense_results}

    balance = []
    cumulative = 0.0
    for m in range(1, 13):
        cumulative += income_map.get(m, 0) - expense_map.get(m, 0)
        balance.append(round(cumulative, 2))

    return jsonify({
        "labels": MONTH_NAMES,
        "datasets": [{
            "label": "Saldo Acumulado",
            "data": balance,
            "borderColor": "#00b4d8",
            "backgroundColor": "rgba(0, 180, 216, 0.1)",
            "fill": True,
            "tension": 0.4,
        }]
    })


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


@api_bp.route("/seed-demo", methods=["POST"])
def seed_demo():
    """Carrega dados de demonstração no banco."""
    try:
        Transaction.query.delete()

        today = date.today()
        transactions = [
            Transaction(
                description=item["description"],
                amount=item["amount"],
                date=today + timedelta(days=item["day_offset"]),
                type=item["type"],
                category=item["category"],
            )
            for item in DEMO_TRANSACTIONS
        ]
        db.session.add_all(transactions)

        db.session.commit()
        count = Transaction.query.count()
        return jsonify({"message": "Dados de demonstração carregados com sucesso", "count": count}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@api_bp.route("/clear-all", methods=["DELETE"])
def clear_all():
    """Remove todas as transações do banco."""
    try:
        count = Transaction.query.count()
        Transaction.query.delete()
        db.session.commit()
        return jsonify({"message": f"{count} transações removidas com sucesso", "count": count}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
