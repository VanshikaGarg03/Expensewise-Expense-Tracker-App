from flask_migrate import Migrate
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Ensure instance folder exists
os.makedirs(os.path.join(app.instance_path), exist_ok=True)

# SQLite database inside instance folder
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(os.path.join(app.instance_path, 'expensewise.db'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    amount = db.Column(db.Float)
    category = db.Column(db.String(50))
    date = db.Column(db.String(20))

with app.app_context():
    db.create_all()

@app.route('/expenses', methods=['GET'])
def get_expenses():
    expenses = Expense.query.all()
    return jsonify([{
        'id': e.id,
        'title': e.title,
        'amount': e.amount,
        'category': e.category,
        'date': e.date
    } for e in expenses])

@app.route('/expenses', methods=['POST'])
def add_expense():
    data = request.get_json()
    new_expense = Expense(
        title=data['title'],
        amount=data['amount'],
        category=data['category'],
        date=data['date']
    )
    db.session.add(new_expense)
    db.session.commit()
    return jsonify({'message': 'Expense added successfully'})

@app.route('/expenses/<int:id>', methods=['DELETE'])
def delete_expense(id):
    expense = Expense.query.get_or_404(id)
    db.session.delete(expense)
    db.session.commit()
    return jsonify({'message': 'Expense deleted successfully'})

@app.route('/expenses/<int:id>', methods=['PUT'])
def update_expense(id):
    expense = Expense.query.get_or_404(id)
    data = request.get_json()

    expense.title = data.get('title', expense.title)
    expense.amount = data.get('amount', expense.amount)
    expense.category = data.get('category', expense.category)
    expense.date = data.get('date', expense.date)

    db.session.commit()
    return jsonify({'message': 'Expense updated successfully'})

@app.route('/budget', methods=['POST'])
def set_budget():
    data = request.get_json()
    month = data['month']
    amount = data['amount']

    existing = MonthlyBudget.query.filter_by(month=month).first()
    if existing:
        existing.budget_amount = amount
    else:
        new_budget = MonthlyBudget(month=month, budget_amount=amount)
        db.session.add(new_budget)

    db.session.commit()
    return jsonify({'message': 'Budget saved successfully'}), 200


@app.route('/budget/<month>', methods=['GET'])
def get_budget(month):
    budget = MonthlyBudget.query.filter_by(month=month).first()
    if budget:
        return jsonify({'month': budget.month, 'amount': budget.budget_amount}), 200
    else:
        return jsonify({'message': 'No budget found'}), 404


if __name__ == '__main__':
    app.run(debug=True)
