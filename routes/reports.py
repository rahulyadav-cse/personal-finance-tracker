from flask import Blueprint, render_template, request
from flask_login import login_required, current_user

from extensions import db
from models.transaction import Transaction
from flask import (
    Blueprint,
    render_template,
    request,
    Response
)

from flask_login import login_required, current_user

from extensions import db
from models.transaction import Transaction

reports_bp = Blueprint(
    "reports",
    __name__,
    url_prefix="/reports"
)


@reports_bp.route("/")
@login_required
def reports():

    # =====================================================
    # GET FILTER VALUES
    # =====================================================

    selected_month = request.args.get("month", "").strip()
    selected_type = request.args.get("type", "").strip().lower()
    selected_category = request.args.get("category", "").strip()


    # =====================================================
    # BASE QUERY
    # =====================================================

    query = Transaction.query.filter(
        Transaction.user_id == current_user.id
    )


    # =====================================================
    # MONTH FILTER
    # Format: YYYY-MM
    # =====================================================

    if selected_month:

        query = query.filter(
            db.func.strftime(
                "%Y-%m",
                Transaction.transaction_date
            ) == selected_month
        )


    # =====================================================
    # TYPE FILTER
    # =====================================================

    if selected_type in ["income", "expense"]:

        query = query.filter(
            db.func.lower(Transaction.type) == selected_type
        )


    # =====================================================
    # CATEGORY FILTER
    # =====================================================

    if selected_category:

        query = query.filter(
            Transaction.category == selected_category
        )


    # =====================================================
    # GET FILTERED TRANSACTIONS
    # =====================================================

    transactions = query.order_by(
        Transaction.transaction_date.desc(),
        Transaction.id.desc()
    ).all()


    # =====================================================
    # CALCULATE TOTALS
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

    balance = total_income - total_expense


    # =====================================================
    # CATEGORY-WISE EXPENSES
    # =====================================================

    category_expenses = {}


    for transaction in transactions:

        transaction_type = (
            transaction.type or ""
        ).lower()


        if transaction_type != "expense":
            continue


        category = (
            transaction.category
            or "Other"
        )


        if category not in category_expenses:

            category_expenses[category] = 0


        category_expenses[category] += float(
            transaction.amount or 0
        )


    # =====================================================
    # GET ALL USER TRANSACTIONS
    # Used for category dropdown
    # =====================================================

    all_transactions = (
        Transaction.query
        .filter(
            Transaction.user_id == current_user.id
        )
        .all()
    )


    # =====================================================
    # CATEGORY DROPDOWN
    # =====================================================

    categories = sorted(
        {
            transaction.category
            for transaction in all_transactions
            if transaction.category
        }
    )


    # =====================================================
    # MONTHLY CHART DATA
    # =====================================================

    monthly_income = {}
    monthly_expense = {}


    for transaction in all_transactions:

        if not transaction.transaction_date:
            continue


        month_key = transaction.transaction_date.strftime(
            "%Y-%m"
        )


        transaction_type = (
            transaction.type or ""
        ).lower()


        amount = float(
            transaction.amount or 0
        )


        if transaction_type == "income":

            monthly_income[month_key] = (
                monthly_income.get(month_key, 0)
                + amount
            )


        elif transaction_type == "expense":

            monthly_expense[month_key] = (
                monthly_expense.get(month_key, 0)
                + amount
            )


    # =====================================================
    # MONTHLY CHART
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
                monthly_income.get(month, 0),
                2
            )
        )

        expense_data.append(
            round(
                monthly_expense.get(month, 0),
                2
            )
        )


    # =====================================================
    # CATEGORY CHART DATA
    # =====================================================

    category_labels = list(
        category_expenses.keys()
    )

    category_data = [
        round(value, 2)
        for value in category_expenses.values()
    ]


    # =====================================================
    # RENDER
    # =====================================================

    return render_template(

        "reports/reports.html",

        # Transactions
        transactions=transactions,

        # Summary
        total_income=round(total_income, 2),
        total_expense=round(total_expense, 2),
        balance=round(balance, 2),

        # Categories
        categories=categories,
        category_expenses=category_expenses,
        category_labels=category_labels,
        category_data=category_data,

        # Monthly chart
        monthly_labels=monthly_labels,
        income_data=income_data,
        expense_data=expense_data,

        # Current filters
        selected_month=selected_month,
        selected_type=selected_type,
        selected_category=selected_category
    )# =====================================================
# CSV EXPORT
# =====================================================

@reports_bp.route("/export")
@login_required
def export_report():

    import csv
    from io import StringIO
    from flask import Response

    # -----------------------------
    # Get filters
    # -----------------------------

    selected_month = request.args.get(
        "month",
        ""
    ).strip()

    selected_type = request.args.get(
        "type",
        ""
    ).strip().lower()

    selected_category = request.args.get(
        "category",
        ""
    ).strip()


    # -----------------------------
    # Base query
    # -----------------------------

    query = Transaction.query.filter(
        Transaction.user_id == current_user.id
    )


    # -----------------------------
    # Month filter
    # -----------------------------

    if selected_month:

        query = query.filter(
            db.func.strftime(
                "%Y-%m",
                Transaction.transaction_date
            ) == selected_month
        )


    # -----------------------------
    # Type filter
    # -----------------------------

    if selected_type in [
        "income",
        "expense"
    ]:

        query = query.filter(
            db.func.lower(
                Transaction.type
            ) == selected_type
        )


    # -----------------------------
    # Category filter
    # -----------------------------

    if selected_category:

        query = query.filter(
            Transaction.category ==
            selected_category
        )


    # -----------------------------
    # Get transactions
    # -----------------------------

    transactions = query.order_by(
        Transaction.transaction_date.desc(),
        Transaction.id.desc()
    ).all()


    # -----------------------------
    # Create CSV
    # -----------------------------

    output = StringIO()

    writer = csv.writer(output)


    # Header

    writer.writerow([
        "Date",
        "Type",
        "Category",
        "Description",
        "Payment Method",
        "Amount"
    ])


    # Data

    for transaction in transactions:

        writer.writerow([

            transaction.transaction_date,

            transaction.type,

            transaction.category,

            transaction.description or "",

            transaction.payment_method,

            transaction.amount

        ])


    # -----------------------------
    # Response
    # -----------------------------

    response = Response(
        output.getvalue(),
        mimetype="text/csv"
    )


    response.headers[
        "Content-Disposition"
    ] = (
        "attachment; "
        "filename=finance_report.csv"
    )


    return response
# =====================================================
# PDF EXPORT
# =====================================================

@reports_bp.route("/export/pdf")
@login_required
def export_pdf():

    from io import BytesIO
    from datetime import datetime

    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle
    )

    # =================================================
    # GET FILTERS
    # =================================================

    selected_month = request.args.get(
        "month",
        ""
    ).strip()

    selected_type = request.args.get(
        "type",
        ""
    ).strip().lower()

    selected_category = request.args.get(
        "category",
        ""
    ).strip()


    # =================================================
    # BASE QUERY
    # =================================================

    query = Transaction.query.filter(
        Transaction.user_id == current_user.id
    )


    # =================================================
    # MONTH FILTER
    # =================================================

    if selected_month:

        query = query.filter(
            db.func.strftime(
                "%Y-%m",
                Transaction.transaction_date
            ) == selected_month
        )


    # =================================================
    # TYPE FILTER
    # =================================================

    if selected_type in [
        "income",
        "expense"
    ]:

        query = query.filter(
            db.func.lower(
                Transaction.type
            ) == selected_type
        )


    # =================================================
    # CATEGORY FILTER
    # =================================================

    if selected_category:

        query = query.filter(
            Transaction.category ==
            selected_category
        )


    # =================================================
    # GET TRANSACTIONS
    # =================================================

    transactions = query.order_by(
        Transaction.transaction_date.desc(),
        Transaction.id.desc()
    ).all()


    # =================================================
    # CALCULATE TOTALS
    # =================================================

    total_income = 0
    total_expense = 0

    category_expenses = {}


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

            category = (
                transaction.category
                or "Other"
            )

            category_expenses[category] = (
                category_expenses.get(
                    category,
                    0
                )
                + amount
            )


    balance = (
        total_income -
        total_expense
    )


    # =================================================
    # CREATE PDF
    # =================================================

    buffer = BytesIO()


    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm
    )


    styles = getSampleStyleSheet()

    story = []


    # =================================================
    # TITLE
    # =================================================

    story.append(
        Paragraph(
            "Finance Tracker - Financial Report",
            styles["Title"]
        )
    )

    story.append(
        Spacer(1, 8)
    )


    # =================================================
    # USER
    # =================================================

    username = (
        getattr(
            current_user,
            "name",
            None
        )
        or getattr(
            current_user,
            "username",
            "User"
        )
    )


    story.append(
        Paragraph(
            f"<b>User:</b> {username}",
            styles["Normal"]
        )
    )


    story.append(
        Paragraph(
            "<b>Generated:</b> "
            + datetime.now().strftime(
                "%d-%m-%Y %H:%M"
            ),
            styles["Normal"]
        )
    )


    story.append(
        Spacer(1, 12)
    )


    # =================================================
    # FILTER INFORMATION
    # =================================================

    filter_month = (
        selected_month
        if selected_month
        else "All Months"
    )

    filter_type = (
        selected_type.title()
        if selected_type
        else "All Types"
    )

    filter_category = (
        selected_category
        if selected_category
        else "All Categories"
    )


    filter_data = [

        [
            "Month",
            "Type",
            "Category"
        ],

        [
            filter_month,
            filter_type,
            filter_category
        ]

    ]


    filter_table = Table(
        filter_data,
        colWidths=[
            55 * mm,
            55 * mm,
            55 * mm
        ]
    )


    filter_table.setStyle(
        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.lightgrey
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),

            (
                "ALIGN",
                (0, 0),
                (-1, -1),
                "CENTER"
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                7
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                7
            )

        ])
    )


    story.append(
        filter_table
    )


    story.append(
        Spacer(1, 15)
    )


    # =================================================
    # SUMMARY
    # =================================================

    summary_data = [

        [
            "Total Income",
            "Total Expense",
            "Balance"
        ],

        [
            f"Rs. {total_income:.2f}",
            f"Rs. {total_expense:.2f}",
            f"Rs. {balance:.2f}"
        ]

    ]


    summary_table = Table(
        summary_data,
        colWidths=[
            55 * mm,
            55 * mm,
            55 * mm
        ]
    )


    summary_table.setStyle(
        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.lightgrey
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "FONTNAME",
                (0, 1),
                (-1, 1),
                "Helvetica-Bold"
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),

            (
                "ALIGN",
                (0, 0),
                (-1, -1),
                "CENTER"
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                8
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                8
            )

        ])
    )


    story.append(
        summary_table
    )


    story.append(
        Spacer(1, 18)
    )


    # =================================================
    # CATEGORY EXPENSES
    # =================================================

    story.append(
        Paragraph(
            "Expense by Category",
            styles["Heading2"]
        )
    )


    story.append(
        Spacer(1, 8)
    )


    if category_expenses:

        category_data = [

            [
                "Category",
                "Amount"
            ]

        ]


        for category, amount in (
            category_expenses.items()
        ):

            category_data.append([

                category,

                f"Rs. {amount:.2f}"

            ])


        category_table = Table(
            category_data,
            colWidths=[
                100 * mm,
                60 * mm
            ]
        )


        category_table.setStyle(
            TableStyle([

                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey
                ),

                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),

                (
                    "ALIGN",
                    (1, 1),
                    (1, -1),
                    "RIGHT"
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6
                )

            ])
        )


        story.append(
            category_table
        )

    else:

        story.append(
            Paragraph(
                "No expense data available.",
                styles["Normal"]
            )
        )


    story.append(
        Spacer(1, 18)
    )


    # =================================================
    # TRANSACTIONS
    # =================================================

    story.append(
        Paragraph(
            "Transactions",
            styles["Heading2"]
        )
    )


    story.append(
        Spacer(1, 8)
    )


    transaction_data = [

        [
            "Date",
            "Type",
            "Category",
            "Payment",
            "Amount"
        ]

    ]


    for transaction in transactions:

        transaction_data.append([

            transaction.transaction_date.strftime(
                "%d-%m-%Y"
            ),

            transaction.type.title(),

            transaction.category,

            transaction.payment_method,

            f"Rs. {float(transaction.amount):.2f}"

        ])


    if len(transaction_data) == 1:

        transaction_data.append([

            "-",
            "-",
            "No transactions found",
            "-",
            "-"

        ])


    transaction_table = Table(
        transaction_data,
        colWidths=[
            28 * mm,
            27 * mm,
            42 * mm,
            35 * mm,
            35 * mm
        ],
        repeatRows=1
    )


    transaction_table.setStyle(
        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.lightgrey
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),

            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                8
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                5
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                5
            )

        ])
    )


    story.append(
        transaction_table
    )


    # =================================================
    # BUILD
    # =================================================

    document.build(story)


    buffer.seek(0)


    return Response(

        buffer.getvalue(),

        mimetype="application/pdf",

        headers={

            "Content-Disposition":
                "attachment; "
                "filename=finance_report.pdf"

        }

    )