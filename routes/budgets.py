from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user

from extensions import db
from models.budget import Budget
from models.transaction import Transaction

from datetime import datetime


budgets_bp = Blueprint(
    "budgets",
    __name__,
    url_prefix="/budgets"
)


# =====================================================
# VIEW BUDGETS
# =====================================================

@budgets_bp.route("/")
@login_required
def budgets():

    current_month = datetime.now().month
    current_year = datetime.now().year

    budget_list = Budget.query.filter_by(
        user_id=current_user.id,
        month=current_month,
        year=current_year
    ).all()

    budget_data = []

    for budget in budget_list:

        # ---------------------------------------------
        # Get expenses for this budget category
        # ---------------------------------------------

        transactions = Transaction.query.filter(
            Transaction.user_id == current_user.id,
            Transaction.category == budget.category,
            Transaction.type == "expense"
        ).all()

        spent = 0

        for transaction in transactions:

            if transaction.transaction_date:

                if (
                    transaction.transaction_date.month == current_month
                    and
                    transaction.transaction_date.year == current_year
                ):

                    spent += float(transaction.amount)


        # ---------------------------------------------
        # Remaining amount
        # ---------------------------------------------

        remaining = float(budget.amount) - spent


        # ---------------------------------------------
        # Percentage used
        # ---------------------------------------------

        if float(budget.amount) > 0:

            percentage = (
                spent / float(budget.amount)
            ) * 100

        else:

            percentage = 0


        # ---------------------------------------------
        # Progress bar value
        # ---------------------------------------------

        progress = min(
            max(percentage, 0),
            100
        )


        budget_data.append({

            "id": budget.id,

            "category": budget.category,

            "amount": float(budget.amount),

            "spent": spent,

            "remaining": remaining,

            "percentage": percentage,

            "progress": progress

        })


    return render_template(

        "budgets/budgets.html",

        budgets=budget_data,

        current_month=current_month,

        current_year=current_year

    )


# =====================================================
# ADD BUDGET
# =====================================================

@budgets_bp.route("/add", methods=["POST"])
@login_required
def add_budget():

    category = request.form.get("category")

    amount = request.form.get("amount")


    # ---------------------------------------------
    # Validate input
    # ---------------------------------------------

    if not category or not amount:

        return redirect(
            url_for("budgets.budgets")
        )


    try:

        amount = float(amount)

    except ValueError:

        return redirect(
            url_for("budgets.budgets")
        )


    if amount <= 0:

        return redirect(
            url_for("budgets.budgets")
        )


    # ---------------------------------------------
    # Current month/year
    # ---------------------------------------------

    current_month = datetime.now().month

    current_year = datetime.now().year


    # ---------------------------------------------
    # Create budget
    # ---------------------------------------------

    budget = Budget(

        user_id=current_user.id,

        category=category,

        amount=amount,

        month=current_month,

        year=current_year

    )


    db.session.add(budget)

    db.session.commit()


    return redirect(
        url_for("budgets.budgets")
    )


# =====================================================
# DELETE BUDGET
# =====================================================

@budgets_bp.route("/delete/<int:budget_id>")
@login_required
def delete_budget(budget_id):

    budget = Budget.query.filter_by(

        id=budget_id,

        user_id=current_user.id

    ).first_or_404()


    db.session.delete(budget)

    db.session.commit()


    return redirect(
        url_for("budgets.budgets")
    )