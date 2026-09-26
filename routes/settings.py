from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user


settings_bp = Blueprint(
    "settings",
    __name__,
    url_prefix="/settings"
)


# ==========================================
# SETTINGS PAGE
# ==========================================

@settings_bp.route("/", methods=["GET", "POST"])
@login_required
def settings():

    if request.method == "POST":

        currency = request.form.get("currency", "INR")
        theme = request.form.get("theme", "light")
        date_format = request.form.get("date_format", "DD-MM-YYYY")
        notifications = request.form.get("notifications") == "on"

        # Store settings in session
        session["currency"] = currency
        session["theme"] = theme
        session["date_format"] = date_format
        session["notifications"] = notifications

        flash("Settings saved successfully.", "success")

        return redirect(url_for("settings.settings"))

    # Load saved settings
    settings_data = {
        "currency": session.get("currency", "INR"),
        "theme": session.get("theme", "light"),
        "date_format": session.get("date_format", "DD-MM-YYYY"),
        "notifications": session.get("notifications", True)
    }

    return render_template(
        "settings/settings.html",
        settings=settings_data,
        user=current_user
    )