from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

CATEGORIES = [
    "Alimentação",
    "Transporte",
    "Moradia",
    "Lazer",
    "Saúde",
    "Educação",
    "Salário",
    "Freelance",
    "Investimentos",
    "Outros",
]

TRANSACTION_TYPES = ["Receita", "Despesa"]


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    type = db.Column(db.String(10), nullable=False)  # 'Receita' or 'Despesa'
    category = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "description": self.description,
            "amount": self.amount,
            "date": self.date.strftime("%Y-%m-%d"),
            "type": self.type,
            "category": self.category,
        }
