from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from models.user import User
from extensions import db
import re
from sqlalchemy.exc import IntegrityError


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth"
)


# ==========================================
# EMAIL VALIDATION
# ==========================================

def is_valid_email(email):

    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    return re.fullmatch(pattern, email) is not None


# ==========================================
# REGISTER
# ==========================================

@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name or not email or not password or not confirm_password:
            flash("All fields are required.", "danger")
            return redirect(url_for("auth.register"))

        if not is_valid_email(email):
            flash("Please enter a valid email address.", "danger")
            return redirect(url_for("auth.register"))

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("auth.register"))

        if len(password) < 8:
            flash("Password must be at least 8 characters.", "danger")
            return redirect(url_for("auth.register"))

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash(
                "An account with this email already exists.",
                "warning"
            )
            return redirect(url_for("auth.register"))

        user = User(
            name=name,
            email=email
        )

        user.set_password(password)

        try:

            db.session.add(user)
            db.session.commit()

        except IntegrityError:

            db.session.rollback()

            flash(
                "An account with this email already exists.",
                "warning"
            )

            return redirect(url_for("auth.register"))

        flash(
            "Account created successfully. Please login.",
            "success"
        )

        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


# ==========================================
# LOGIN
# ==========================================

@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        user = User.query.filter_by(
            email=email
        ).first()

        if user and user.check_password(password):

            login_user(user)

            return redirect(
                url_for("dashboard.dashboard")
            )

        flash(
            "Invalid email or password.",
            "danger"
        )

    return render_template("auth/login.html")


# ==========================================
# FORGOT PASSWORD
# ==========================================

@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        # Check empty email
        if not email:

            flash(
                "Please enter your email address.",
                "danger"
            )

            return redirect(
                url_for("auth.forgot_password")
            )

        # Check email format
        if not is_valid_email(email):

            flash(
                "Please enter a valid email address.",
                "danger"
            )

            return redirect(
                url_for("auth.forgot_password")
            )

        # Find user
        user = User.query.filter_by(
            email=email
        ).first()

        if not user:

            flash(
                "No account was found with this email address.",
                "warning"
            )

            return redirect(
                url_for("auth.forgot_password")
            )

        # Temporary step
        # Actual email reset will be added next.
        flash(
            "Email verified. Password reset is ready to be implemented.",
            "success"
        )

        return redirect(
            url_for("auth.reset_password", email=email)
        )

    return render_template(
        "auth/forgot_password.html"
    )


# ==========================================
# RESET PASSWORD
# ==========================================

@auth_bp.route("/reset-password", methods=["GET", "POST"])
def reset_password():

    email = request.args.get(
        "email",
        ""
    ).strip().lower()

    user = User.query.filter_by(
        email=email
    ).first()

    if not user:

        flash(
            "Invalid password reset request.",
            "danger"
        )

        return redirect(
            url_for("auth.login")
        )

    if request.method == "POST":

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        if len(password) < 8:

            flash(
                "Password must be at least 8 characters.",
                "danger"
            )

            return redirect(
                url_for(
                    "auth.reset_password",
                    email=email
                )
            )

        if password != confirm_password:

            flash(
                "Passwords do not match.",
                "danger"
            )

            return redirect(
                url_for(
                    "auth.reset_password",
                    email=email
                )
            )

        user.set_password(password)

        db.session.commit()

        flash(
            "Password changed successfully. Please login.",
            "success"
        )

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "auth/reset_password.html",
        email=email
    )


# ==========================================
# LOGOUT
# ==========================================

@auth_bp.route("/logout")
@login_required
def logout():

    logout_user()

    flash(
        "You have been logged out successfully.",
        "success"
    )

    return redirect(
        url_for("auth.login")
    )