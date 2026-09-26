from datetime import date

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
from models.goal import Goal


# =========================================================
# BLUEPRINT
# =========================================================

goals_bp = Blueprint(
    "goals",
    __name__,
    url_prefix="/goals"
)


# =========================================================
# GOALS PAGE
# =========================================================

@goals_bp.route("/")
@login_required
def goals():

    goal_list = (
        Goal.query
        .filter_by(user_id=current_user.id)
        .order_by(Goal.target_date.asc())
        .all()
    )

    total_target = 0
    total_saved = 0
    completed_goals = 0

    # -----------------------------------------------------
    # Calculate totals and progress
    # -----------------------------------------------------

    for goal in goal_list:

        target = float(goal.target_amount or 0)
        current = float(goal.current_amount or 0)

        total_target += target
        total_saved += current

        if target > 0:
            progress = (current / target) * 100
        else:
            progress = 0

        # Never allow progress above 100
        if progress >= 100:

            progress = 100
            goal.completed = True
            completed_goals += 1

        else:

            goal.completed = False

        goal.progress = progress

    # Save calculated progress
    db.session.commit()

    # -----------------------------------------------------
    # Remaining amount
    # -----------------------------------------------------

    total_remaining = total_target - total_saved

    if total_remaining < 0:
        total_remaining = 0

    # -----------------------------------------------------
    # Render page
    # -----------------------------------------------------

    return render_template(
        "goals/goals.html",
        goals=goal_list,
        total_target=total_target,
        total_saved=total_saved,
        total_remaining=total_remaining,
        completed_goals=completed_goals
    )


# =========================================================
# ADD GOAL
# =========================================================

@goals_bp.route("/add", methods=["POST"])
@login_required
def add_goal():

    # -----------------------------------------------------
    # Get form values
    # -----------------------------------------------------

    name = request.form.get(
        "name",
        ""
    ).strip()

    target_amount = request.form.get(
        "target_amount",
        ""
    ).strip()

    current_amount = request.form.get(
        "current_amount",
        "0"
    ).strip()

    # Category is optional because your current
    # goals.html does not contain a category field.
    category = request.form.get(
        "category",
        "General"
    ).strip()

    target_date = request.form.get(
        "target_date",
        ""
    ).strip()

    # -----------------------------------------------------
    # Required fields
    # -----------------------------------------------------

    if not name:

        flash(
            "Please enter a goal name.",
            "danger"
        )

        return redirect(
            url_for("goals.goals")
        )

    if not target_amount:

        flash(
            "Please enter the target amount.",
            "danger"
        )

        return redirect(
            url_for("goals.goals")
        )

    if not target_date:

        flash(
            "Please select a target date.",
            "danger"
        )

        return redirect(
            url_for("goals.goals")
        )

    # -----------------------------------------------------
    # Validate amounts
    # -----------------------------------------------------

    try:

        target_amount = float(
            target_amount
        )

        current_amount = float(
            current_amount or 0
        )

        if target_amount <= 0:
            raise ValueError

        if current_amount < 0:
            raise ValueError

    except (ValueError, TypeError):

        flash(
            "Please enter valid amounts.",
            "danger"
        )

        return redirect(
            url_for("goals.goals")
        )

    # -----------------------------------------------------
    # Validate date
    # -----------------------------------------------------

    try:

        target_date = date.fromisoformat(
            target_date
        )

    except (ValueError, TypeError):

        flash(
            "Please select a valid target date.",
            "danger"
        )

        return redirect(
            url_for("goals.goals")
        )

    # -----------------------------------------------------
    # Don't allow current amount above target
    # -----------------------------------------------------

    if current_amount > target_amount:

        current_amount = target_amount

    # -----------------------------------------------------
    # Calculate progress
    # -----------------------------------------------------

    progress = (
        current_amount /
        target_amount
    ) * 100

    progress = min(
        progress,
        100
    )

    completed = progress >= 100

    # -----------------------------------------------------
    # Create goal
    # -----------------------------------------------------

    goal = Goal(
        user_id=current_user.id,
        name=name,
        target_amount=target_amount,
        current_amount=current_amount,
        category=category or "General",
        target_date=target_date,
        progress=progress,
        completed=completed
    )

    # -----------------------------------------------------
    # Save
    # -----------------------------------------------------

    db.session.add(goal)
    db.session.commit()

    flash(
        "Goal created successfully.",
        "success"
    )

    return redirect(
        url_for("goals.goals")
    )


# =========================================================
# ADD MONEY TO GOAL
# =========================================================

@goals_bp.route(
    "/add-money/<int:goal_id>",
    methods=["POST"]
)
@login_required
def add_money(goal_id):

    goal = (
        Goal.query
        .filter_by(
            id=goal_id,
            user_id=current_user.id
        )
        .first_or_404()
    )

    # -----------------------------------------------------
    # Get amount
    # -----------------------------------------------------

    amount = request.form.get(
        "amount",
        ""
    ).strip()

    # -----------------------------------------------------
    # Validate amount
    # -----------------------------------------------------

    try:

        amount = float(amount)

        if amount <= 0:
            raise ValueError

    except (ValueError, TypeError):

        flash(
            "Please enter a valid amount.",
            "danger"
        )

        return redirect(
            url_for("goals.goals")
        )

    # -----------------------------------------------------
    # Add money
    # -----------------------------------------------------

    goal.current_amount = (
        float(goal.current_amount or 0)
        + amount
    )

    # -----------------------------------------------------
    # Check completion
    # -----------------------------------------------------

    target = float(
        goal.target_amount or 0
    )

    if target > 0:

        if goal.current_amount >= target:

            goal.current_amount = target
            goal.progress = 100
            goal.completed = True

            flash(
                "Congratulations! Goal completed.",
                "success"
            )

        else:

            goal.progress = (
                goal.current_amount /
                target
            ) * 100

            goal.progress = min(
                goal.progress,
                100
            )

            goal.completed = False

            flash(
                "Money added successfully.",
                "success"
            )

    else:

        goal.progress = 0
        goal.completed = False

    # -----------------------------------------------------
    # Save
    # -----------------------------------------------------

    db.session.commit()

    return redirect(
        url_for("goals.goals")
    )


# =========================================================
# EDIT GOAL
# =========================================================

@goals_bp.route(
    "/edit/<int:goal_id>",
    methods=["GET", "POST"]
)
@login_required
def edit_goal(goal_id):

    goal = (
        Goal.query
        .filter_by(
            id=goal_id,
            user_id=current_user.id
        )
        .first_or_404()
    )

    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":

        # -------------------------------------------------
        # Get form values
        # -------------------------------------------------

        name = request.form.get(
            "name",
            ""
        ).strip()

        target_amount = request.form.get(
            "target_amount",
            ""
        ).strip()

        current_amount = request.form.get(
            "current_amount",
            "0"
        ).strip()

        category = request.form.get(
            "category",
            "General"
        ).strip()

        target_date = request.form.get(
            "target_date",
            ""
        ).strip()

        # -------------------------------------------------
        # Required fields
        # -------------------------------------------------

        if not name:

            flash(
                "Please enter a goal name.",
                "danger"
            )

            return redirect(
                url_for(
                    "goals.edit_goal",
                    goal_id=goal_id
                )
            )

        if not target_amount:

            flash(
                "Please enter the target amount.",
                "danger"
            )

            return redirect(
                url_for(
                    "goals.edit_goal",
                    goal_id=goal_id
                )
            )

        if not target_date:

            flash(
                "Please select a target date.",
                "danger"
            )

            return redirect(
                url_for(
                    "goals.edit_goal",
                    goal_id=goal_id
                )
            )

        # -------------------------------------------------
        # Validate amounts
        # -------------------------------------------------

        try:

            target_amount = float(
                target_amount
            )

            current_amount = float(
                current_amount or 0
            )

            if target_amount <= 0:
                raise ValueError

            if current_amount < 0:
                raise ValueError

        except (ValueError, TypeError):

            flash(
                "Please enter valid amounts.",
                "danger"
            )

            return redirect(
                url_for(
                    "goals.edit_goal",
                    goal_id=goal_id
                )
            )

        # -------------------------------------------------
        # Validate date
        # -------------------------------------------------

        try:

            target_date = date.fromisoformat(
                target_date
            )

        except (ValueError, TypeError):

            flash(
                "Please select a valid target date.",
                "danger"
            )

            return redirect(
                url_for(
                    "goals.edit_goal",
                    goal_id=goal_id
                )
            )

        # -------------------------------------------------
        # Limit current amount
        # -------------------------------------------------

        if current_amount > target_amount:

            current_amount = target_amount

        # -------------------------------------------------
        # Calculate progress
        # -------------------------------------------------

        progress = (
            current_amount /
            target_amount
        ) * 100

        progress = min(
            progress,
            100
        )

        completed = progress >= 100

        # -------------------------------------------------
        # Update goal
        # -------------------------------------------------

        goal.name = name

        goal.target_amount = target_amount

        goal.current_amount = current_amount

        goal.category = category or "General"

        goal.target_date = target_date

        goal.progress = progress

        goal.completed = completed

        # -------------------------------------------------
        # Save
        # -------------------------------------------------

        db.session.commit()

        flash(
            "Goal updated successfully.",
            "success"
        )

        return redirect(
            url_for("goals.goals")
        )

    # =====================================================
    # GET
    # =====================================================

    return render_template(
        "goals/edit_goal.html",
        goal=goal
    )


# =========================================================
# DELETE GOAL
# =========================================================

@goals_bp.route(
    "/delete/<int:goal_id>",
    methods=["POST"]
)
@login_required
def delete_goal(goal_id):

    goal = (
        Goal.query
        .filter_by(
            id=goal_id,
            user_id=current_user.id
        )
        .first_or_404()
    )

    # -----------------------------------------------------
    # Delete
    # -----------------------------------------------------

    db.session.delete(goal)
    db.session.commit()

    flash(
        "Goal deleted successfully.",
        "success"
    )

    return redirect(
        url_for("goals.goals")
    )