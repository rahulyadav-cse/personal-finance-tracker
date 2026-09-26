from datetime import date
from sqlalchemy import func
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import login_required, current_user

from extensions import db
from models.transaction import Transaction


transactions_bp = Blueprint(
    "transactions",
    __name__,
    url_prefix="/transactions"
)


# --------------------------------
# View All Transactions
# --------------------------------

@transactions_bp.route("/")
@login_required
def transactions():

    transaction_list = (
        Transaction.query
        .filter_by(user_id=current_user.id)
        .order_by(Transaction.transaction_date.desc())
        .all()
    )

    # --------------------------------
    # Calculate Total Income
    # --------------------------------

    total_income = sum(
        transaction.amount
        for transaction in transaction_list
        if transaction.type.lower() == "income"
    )

    # --------------------------------
    # Calculate Total Expenses
    # --------------------------------

    total_expenses = sum(
        transaction.amount
        for transaction in transaction_list
        if transaction.type.lower() == "expense"
    )

    # --------------------------------
    # Calculate Current Balance
    # --------------------------------

    current_balance = total_income - total_expenses

    return render_template(
        "transactions/transactions.html",
        transactions=transaction_list,
        total_income=total_income,
        total_expenses=total_expenses,
        current_balance=current_balance
    )


# --------------------------------
# Add Transaction
# --------------------------------

@transactions_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_transaction():

    if request.method == "POST":

        transaction_type = request.form.get("type")
        amount = request.form.get("amount")
        category = request.form.get("category")
        description = request.form.get("description")
        payment_method = request.form.get("payment_method")
        transaction_date = request.form.get("transaction_date")

        if not all([
            transaction_type,
            amount,
            category,
            payment_method,
            transaction_date
        ]):

            flash(
                "Please fill in all required fields.",
                "danger"
            )

            return redirect(
                url_for("transactions.add_transaction")
            )

        try:

            amount = float(amount)

            if amount <= 0:
                raise ValueError

        except ValueError:

            flash(
                "Amount must be greater than zero.",
                "danger"
            )

            return redirect(
                url_for("transactions.add_transaction")
            )

        try:

            transaction_date = date.fromisoformat(
                transaction_date
            )

        except ValueError:

            flash(
                "Invalid date.",
                "danger"
            )

            return redirect(
                url_for("transactions.add_transaction")
            )

        transaction = Transaction(
            user_id=current_user.id,
            type=transaction_type,
            amount=amount,
            category=category,
            description=description,
            payment_method=payment_method,
            transaction_date=transaction_date
        )

        db.session.add(transaction)
        db.session.commit()

        flash(
            "Transaction added successfully.",
            "success"
        )

        return redirect(
            url_for("transactions.transactions")
        )

    return render_template(
        "transactions/add_transaction.html"
    )


# --------------------------------
# Edit Transaction
# --------------------------------

@transactions_bp.route(
    "/edit/<int:transaction_id>",
    methods=["GET", "POST"]
)
@login_required
def edit_transaction(transaction_id):

    transaction = Transaction.query.filter_by(
        id=transaction_id,
        user_id=current_user.id
    ).first_or_404()

    if request.method == "POST":

        transaction_type = request.form.get("type")
        amount = request.form.get("amount")
        category = request.form.get("category")
        description = request.form.get("description")
        payment_method = request.form.get("payment_method")
        transaction_date = request.form.get("transaction_date")

        if not all([
            transaction_type,
            amount,
            category,
            payment_method,
            transaction_date
        ]):

            flash(
                "Please fill in all required fields.",
                "danger"
            )

            return redirect(
                url_for(
                    "transactions.edit_transaction",
                    transaction_id=transaction_id
                )
            )

        try:

            amount = float(amount)

            if amount <= 0:
                raise ValueError

        except ValueError:

            flash(
                "Amount must be greater than zero.",
                "danger"
            )

            return redirect(
                url_for(
                    "transactions.edit_transaction",
                    transaction_id=transaction_id
                )
            )

        try:

            transaction_date = date.fromisoformat(
                transaction_date
            )

        except ValueError:

            flash(
                "Invalid date.",
                "danger"
            )

            return redirect(
                url_for(
                    "transactions.edit_transaction",
                    transaction_id=transaction_id
                )
            )

        transaction.type = transaction_type
        transaction.amount = amount
        transaction.category = category
        transaction.description = description
        transaction.payment_method = payment_method
        transaction.transaction_date = transaction_date

        db.session.commit()

        flash(
            "Transaction updated successfully.",
            "success"
        )

        return redirect(
            url_for("transactions.transactions")
        )

    return render_template(
        "transactions/edit_transaction.html",
        transaction=transaction
    )


# --------------------------------
# Delete Transaction
# --------------------------------

@transactions_bp.route(
    "/delete/<int:transaction_id>",
    methods=["POST"]
)
@login_required
def delete_transaction(transaction_id):

    transaction = Transaction.query.filter_by(
        id=transaction_id,
        user_id=current_user.id
    ).first_or_404()

    db.session.delete(transaction)
    db.session.commit()

    flash(
        "Transaction deleted successfully.",
        "success"
    )

    return redirect(
        url_for("transactions.transactions")
    )