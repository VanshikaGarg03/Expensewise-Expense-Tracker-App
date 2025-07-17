from flask import Blueprint, request, jsonify
from extensions import db
from models import Expense

expense_bp = Blueprint('expenses', __name__)

@expense_bp.route('/', methods=['GET'])
def get_expenses():
    expenses = Expense.query.all()
    return jsonify([
        {
            'id': e.id,
            'title': e.title,
            'amount': e.amount,
            'category': e.category
        } for e in expenses
    ])

@expense_bp.route('/', methods=['POST'])
def add_expense():
    data = request.get_json()
    new_expense = Expense(
        title=data['title'],
        amount=data['amount'],
        category=data['category']
    )
    db.session.add(new_expense)
    db.session.commit()
    return jsonify({'message': 'Expense added successfully'}), 201

@expense_bp.route('/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    expense = Expense.query.get(expense_id)
    if expense:
        db.session.delete(expense)
        db.session.commit()
        return jsonify({'message': 'Expense deleted'})
    return jsonify({'message': 'Expense not found'}), 404

# Budget APIs
@expense_bp.route('/budget', methods=['POST'])
def set_budget():
    data = request.get_json()
    budget = Budget(amount=data['amount'], month=data['month'])
    db.session.add(budget)
    db.session.commit()
    return jsonify({'message': 'Budget set successfully'}), 201

@expense_bp.route('/budget/<string:month>', methods=['GET'])
def get_budget(month):
    budget = Budget.query.filter_by(month=month).first()
    if budget:
        return jsonify({'amount': budget.amount})
    return jsonify({'message': 'Budget not found'}), 404


# Reminder APIs
@expense_bp.route('/reminder', methods=['POST'])
def add_reminder():
    data = request.get_json()
    reminder = Reminder(message=data['message'], date=data['date'])
    db.session.add(reminder)
    db.session.commit()
    return jsonify({'message': 'Reminder added'})
