from flask import Flask, render_template
from flask_login import LoginManager

from config import Config
from extensions import db


# ==========================================
# LOGIN MANAGER
# ==========================================

login_manager = LoginManager()


# ==========================================
# CREATE FLASK APPLICATION
# ==========================================

def create_app():

    app = Flask(__name__)

    # ==========================================
    # LOAD CONFIGURATION
    # ==========================================

    app.config.from_object(Config)

    # ==========================================
    # INITIALIZE DATABASE
    # ==========================================

    db.init_app(app)

    # ==========================================
    # INITIALIZE LOGIN MANAGER
    # ==========================================

    login_manager.init_app(app)

    # Login required user ko yahan redirect karega
    login_manager.login_view = "auth.login"

    # ==========================================
    # IMPORT MODELS
    # ==========================================

    from models.user import User
    from models.transaction import Transaction

    # ==========================================
    # LOAD LOGGED-IN USER
    # ==========================================

    @login_manager.user_loader
    def load_user(user_id):

        return User.query.get(int(user_id))

    # ==========================================
    # REGISTER AUTH BLUEPRINT
    # ==========================================

    from routes.auth import auth_bp

    app.register_blueprint(auth_bp)

    # ==========================================
    # REGISTER DASHBOARD BLUEPRINT
    # ==========================================

    from routes.dashboard import dashboard_bp

    app.register_blueprint(dashboard_bp)

    # ==========================================
    # REGISTER TRANSACTIONS BLUEPRINT
    # ==========================================

    from routes.transactions import transactions_bp

    app.register_blueprint(transactions_bp)

    # ==========================================
    # REGISTER BUDGETS BLUEPRINT
    # ==========================================

    from routes.budgets import budgets_bp

    app.register_blueprint(budgets_bp)

    # ==========================================
    # REGISTER GOALS BLUEPRINT
    # ==========================================

    from routes.goals import goals_bp

    app.register_blueprint(goals_bp)

    # ==========================================
    # REGISTER REPORTS BLUEPRINT
    # ==========================================

    from routes.reports import reports_bp

    app.register_blueprint(reports_bp)

    # ==========================================
    # REGISTER SETTINGS BLUEPRINT
    # ==========================================

    from routes.settings import settings_bp

    app.register_blueprint(settings_bp)

    # ==========================================
    # HOME PAGE
    # ==========================================

    @app.route("/")
    def home():

        return render_template("home.html")

    # ==========================================
    # CREATE DATABASE TABLES
    # ==========================================

    with app.app_context():

        db.create_all()

    # ==========================================
    # RETURN APPLICATION
    # ==========================================

    return app


# ==========================================
# CREATE APPLICATION
# ==========================================

app = create_app()


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":

    app.run(debug=True)