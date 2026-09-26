from flask import Blueprint, render_template
from flask_login import login_required, current_user

from extensions import db
from models.transaction import Transaction


dashboard_bp = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/dashboard"
)


@dashboard_bp.route("/")
@login_required
def dashboard():

    # =====================================================
    # ALL USER TRANSACTIONS
    # =====================================================

    transactions = (
        Transaction.query
        .filter_by(user_id=current_user.id)
        .order_by(
            Transaction.transaction_date.desc(),
            Transaction.id.desc()
        )
        .all()
    )


    # =====================================================
    # TOTAL INCOME / EXPENSE
    # =====================================================

    total_income = 0
    total_expense = 0


    for transaction in transactions:

        transaction_type = (
            transaction.type or ""
        ).lower()

        amount = float(
            transaction.amount or 0
        )


        if transaction_type == "income":

            total_income += amount


        elif transaction_type == "expense":

            total_expense += amount


    # =====================================================
    # BALANCE
    # =====================================================

    balance = (
        total_income -
        total_expense
    )


    # =====================================================
    # RECENT TRANSACTIONS
    # =====================================================

    recent_transactions = transactions[:5]


    # =====================================================
    # MONTHLY DATA
    # =====================================================

    monthly_income = {}
    monthly_expense = {}


    for transaction in transactions:

        if not transaction.transaction_date:
            continue


        month = transaction.transaction_date.strftime(
            "%Y-%m"
        )


        transaction_type = (
            transaction.type or ""
        ).lower()


        amount = float(
            transaction.amount or 0
        )


        if transaction_type == "income":

            monthly_income[month] = (
                monthly_income.get(month, 0)
                + amount
            )


        elif transaction_type == "expense":

            monthly_expense[month] = (
                monthly_expense.get(month, 0)
                + amount
            )


    # =====================================================
    # MONTH LABELS + CHART DATA
    # =====================================================

    all_months = sorted(
        set(monthly_income.keys())
        |
        set(monthly_expense.keys())
    )


    monthly_labels = []
    income_data = []
    expense_data = []


    for month in all_months:

        monthly_labels.append(month)

        income_data.append(
            round(
                monthly_income.get(
                    month,
                    0
                ),
                2
            )
        )

        expense_data.append(
            round(
                monthly_expense.get(
                    month,
                    0
                ),
                2
            )
        )


    # =====================================================
    # CATEGORY EXPENSES
    # =====================================================

    category_expenses = {}


    for transaction in transactions:

        if (
            transaction.type or ""
        ).lower() != "expense":

            continue


        category = (
            transaction.category
            or "Other"
        )


        category_expenses[category] = (
            category_expenses.get(
                category,
                0
            )
            + float(
                transaction.amount or 0
            )
        )


    category_labels = list(
        category_expenses.keys()
    )


    category_data = [

        round(value, 2)

        for value in category_expenses.values()

    ]


    # =====================================================
    # DASHBOARD
    # =====================================================

    return render_template(

        "dashboard/dashboard.html",

        # Summary
        total_income=round(
            total_income,
            2
        ),

        total_expense=round(
            total_expense,
            2
        ),

        balance=round(
            balance,
            2
        ),

        # Transactions
        transactions=transactions,

        recent_transactions=recent_transactions,

        # Monthly chart
        monthly_labels=monthly_labels,

        income_data=income_data,

        expense_data=expense_data,

        # Category chart
        category_labels=category_labels,

        category_data=category_data,

        category_expenses=category_expenses

    )