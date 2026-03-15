from flask import Blueprint, render_template, request
from models.models import db, Transaction
from sqlalchemy import extract, func
from datetime import datetime, date

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def index():
    today = date.today()
    month = request.args.get("month", today.month, type=int)
    year = request.args.get("year", today.year, type=int)

    transactions = Transaction.query.filter(
        extract("month", Transaction.date) == month,
        extract("year", Transaction.date) == year,
    ).all()

    total_income = sum(t.amount for t in transactions if t.type == "Receita")
    total_expense = sum(t.amount for t in transactions if t.type == "Despesa")
    balance = total_income - total_expense

    months = [
        (1, "Janeiro"), (2, "Fevereiro"), (3, "Março"), (4, "Abril"),
        (5, "Maio"), (6, "Junho"), (7, "Julho"), (8, "Agosto"),
        (9, "Setembro"), (10, "Outubro"), (11, "Novembro"), (12, "Dezembro"),
    ]
    current_year = today.year
    years = list(range(current_year - 3, current_year + 2))

    return render_template(
        "dashboard.html",
        total_income=total_income,
        total_expense=total_expense,
        balance=balance,
        selected_month=month,
        selected_year=year,
        months=months,
        years=years,
    )
