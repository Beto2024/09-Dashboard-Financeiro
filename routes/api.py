from flask import Blueprint, jsonify, request
from models.models import db, Transaction
from sqlalchemy import extract, func
from datetime import datetime, date
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
        "#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0",
        "#9966FF", "#FF9F40", "#FF6384", "#C9CBCF",
        "#4BC0C0", "#36A2EB"
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
            "borderColor": "#7367f0",
            "backgroundColor": "rgba(115, 103, 240, 0.1)",
            "fill": True,
            "tension": 0.4,
        }]
    })
