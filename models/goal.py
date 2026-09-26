from extensions import db


class Goal(db.Model):

    __tablename__ = "goals"

    # ==========================================
    # PRIMARY KEY
    # ==========================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # ==========================================
    # USER
    # ==========================================

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    # ==========================================
    # GOAL NAME
    # ==========================================

    name = db.Column(
        db.String(100),
        nullable=False
    )

    # ==========================================
    # TARGET AMOUNT
    # ==========================================

    target_amount = db.Column(
        db.Float,
        nullable=False
    )

    # ==========================================
    # CURRENT SAVED AMOUNT
    # ==========================================

    current_amount = db.Column(
        db.Float,
        default=0,
        nullable=False
    )

    # ==========================================
    # CATEGORY
    # ==========================================

    category = db.Column(
        db.String(50),
        nullable=False
    )

    # ==========================================
    # TARGET DATE
    # ==========================================

    target_date = db.Column(
        db.Date,
        nullable=False
    )

    # ==========================================
    # PROGRESS
    # ==========================================

    progress = db.Column(
        db.Float,
        default=0,
        nullable=False
    )

    # ==========================================
    # COMPLETED
    # ==========================================

    completed = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    # ==========================================
    # CREATED DATE
    # ==========================================

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    # ==========================================
    # USER RELATIONSHIP
    # ==========================================

    user = db.relationship(
        "User",
        backref=db.backref(
            "goals",
            lazy=True
        )
    )