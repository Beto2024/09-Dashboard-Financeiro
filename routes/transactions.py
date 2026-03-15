from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models.models import db, Transaction, CATEGORIES, TRANSACTION_TYPES
from datetime import datetime, date

transactions_bp = Blueprint("transactions", __name__)


@transactions_bp.route("/transactions")
def index():
    type_filter = request.args.get("type", "")
    category_filter = request.args.get("category", "")
    month_filter = request.args.get("month", "")
    year_filter = request.args.get("year", "")

    query = Transaction.query

    if type_filter:
        query = query.filter(Transaction.type == type_filter)
    if category_filter:
        query = query.filter(Transaction.category == category_filter)
    if month_filter:
        from sqlalchemy import extract
        query = query.filter(extract("month", Transaction.date) == int(month_filter))
    if year_filter:
        from sqlalchemy import extract
        query = query.filter(extract("year", Transaction.date) == int(year_filter))

    transactions = query.order_by(Transaction.date.desc()).all()

    total_income = sum(t.amount for t in transactions if t.type == "Receita")
    total_expense = sum(t.amount for t in transactions if t.type == "Despesa")

    today = date.today()
    months = [
        (1, "Janeiro"), (2, "Fevereiro"), (3, "Março"), (4, "Abril"),
        (5, "Maio"), (6, "Junho"), (7, "Julho"), (8, "Agosto"),
        (9, "Setembro"), (10, "Outubro"), (11, "Novembro"), (12, "Dezembro"),
    ]
    years = list(range(today.year - 3, today.year + 2))

    return render_template(
        "transactions.html",
        transactions=transactions,
        categories=CATEGORIES,
        types=TRANSACTION_TYPES,
        total_income=total_income,
        total_expense=total_expense,
        selected_type=type_filter,
        selected_category=category_filter,
        selected_month=month_filter,
        selected_year=year_filter,
        months=months,
        years=years,
    )


@transactions_bp.route("/transactions/create", methods=["POST"])
def create():
    try:
        description = request.form.get("description", "").strip()
        amount = float(request.form.get("amount", 0))
        date_str = request.form.get("date", "")
        t_type = request.form.get("type", "")
        category = request.form.get("category", "")

        if not description or amount <= 0 or not date_str or not t_type or not category:
            flash("Todos os campos são obrigatórios e o valor deve ser positivo.", "danger")
            return redirect(url_for("transactions.index"))

        transaction_date = datetime.strptime(date_str, "%Y-%m-%d").date()

        transaction = Transaction(
            description=description,
            amount=amount,
            date=transaction_date,
            type=t_type,
            category=category,
        )
        db.session.add(transaction)
        db.session.commit()
        flash("Transação criada com sucesso!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao criar transação: {str(e)}", "danger")

    return redirect(url_for("transactions.index"))


@transactions_bp.route("/transactions/<int:transaction_id>/edit", methods=["GET", "POST"])
def edit(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)

    if request.method == "POST":
        try:
            transaction.description = request.form.get("description", "").strip()
            transaction.amount = float(request.form.get("amount", 0))
            date_str = request.form.get("date", "")
            transaction.type = request.form.get("type", "")
            transaction.category = request.form.get("category", "")

            if not transaction.description or transaction.amount <= 0 or not date_str:
                flash("Todos os campos são obrigatórios.", "danger")
                return redirect(url_for("transactions.edit", transaction_id=transaction_id))

            transaction.date = datetime.strptime(date_str, "%Y-%m-%d").date()
            db.session.commit()
            flash("Transação atualizada com sucesso!", "success")
            return redirect(url_for("transactions.index"))
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao atualizar transação: {str(e)}", "danger")

    return render_template(
        "edit_transaction.html",
        transaction=transaction,
        categories=CATEGORIES,
        types=TRANSACTION_TYPES,
    )


@transactions_bp.route("/transactions/<int:transaction_id>/delete", methods=["POST"])
def delete(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    try:
        db.session.delete(transaction)
        db.session.commit()
        flash("Transação excluída com sucesso!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao excluir transação: {str(e)}", "danger")
    return redirect(url_for("transactions.index"))
