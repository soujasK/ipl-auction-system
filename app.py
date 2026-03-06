import os
from datetime import datetime
from decimal import Decimal, InvalidOperation

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func


db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

    # Local PostgreSQL default
    database_url = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres123@localhost:5432/iplauction"
    )

    # Render may provide postgres://, SQLAlchemy expects postgresql://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()
        seed_players_if_empty()

    register_routes(app)
    return app


class Player(db.Model):
    __tablename__ = "players"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    nationality = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(80), nullable=False)
    team = db.Column(db.String(80), nullable=False)
    batting_style = db.Column(db.String(80), nullable=False)
    bowling_style = db.Column(db.String(120), nullable=True)
    matches = db.Column(db.Integer, nullable=False, default=0)
    strike_rate = db.Column(db.Float, nullable=False, default=0.0)
    base_price = db.Column(db.Numeric(12, 2), nullable=False)
    current_price = db.Column(db.Numeric(12, 2), nullable=False)
    status = db.Column(db.String(40), nullable=False, default="Available")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bids = db.relationship(
        "BidHistory",
        backref="player",
        lazy=True,
        cascade="all, delete-orphan"
    )

    @property
    def display_bowling_style(self):
        return self.bowling_style if self.bowling_style else "Not Applicable"


class BidHistory(db.Model):
    __tablename__ = "bid_history"

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey("players.id"), nullable=False)
    bid_amount = db.Column(db.Numeric(12, 2), nullable=False)
    bidder_name = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


SEED_PLAYERS = [
    {
        "name": "Virat Kohli", "nationality": "Indian", "role": "Batsman", "team": "RCB",
        "batting_style": "Right-hand bat", "bowling_style": "Right-arm medium",
        "matches": 252, "strike_rate": 131.97, "base_price": 50000, "current_price": 50000,
    },
    {
        "name": "Rohit Sharma", "nationality": "Indian", "role": "Batsman", "team": "MI",
        "batting_style": "Right-hand bat", "bowling_style": "Right-arm off break",
        "matches": 257, "strike_rate": 131.14, "base_price": 50000, "current_price": 50000,
    },
    {
        "name": "Suryakumar Yadav", "nationality": "Indian", "role": "Batsman", "team": "MI",
        "batting_style": "Right-hand bat", "bowling_style": "Right-arm medium",
        "matches": 150, "strike_rate": 145.32, "base_price": 50000, "current_price": 50000,
    },
    {
        "name": "KL Rahul", "nationality": "Indian", "role": "Wicketkeeper-Batsman", "team": "DC",
        "batting_style": "Right-hand bat", "bowling_style": "Not Applicable",
        "matches": 132, "strike_rate": 134.61, "base_price": 50000, "current_price": 50000,
    },
    {
        "name": "Rishabh Pant", "nationality": "Indian", "role": "Wicketkeeper-Batsman", "team": "LSG",
        "batting_style": "Left-hand bat", "bowling_style": "Not Applicable",
        "matches": 111, "strike_rate": 147.96, "base_price": 50000, "current_price": 50000,
    },
    {
        "name": "Shubman Gill", "nationality": "Indian", "role": "Batsman", "team": "GT",
        "batting_style": "Right-hand bat", "bowling_style": "Right-arm off break",
        "matches": 103, "strike_rate": 135.70, "base_price": 50000, "current_price": 50000,
    },
    {
        "name": "Hardik Pandya", "nationality": "Indian", "role": "All-Rounder", "team": "MI",
        "batting_style": "Right-hand bat", "bowling_style": "Right-arm fast-medium",
        "matches": 137, "strike_rate": 146.32, "base_price": 50000, "current_price": 50000,
    },
    {
        "name": "Jasprit Bumrah", "nationality": "Indian", "role": "Bowler", "team": "MI",
        "batting_style": "Right-hand bat", "bowling_style": "Right-arm fast",
        "matches": 133, "strike_rate": 89.50, "base_price": 50000, "current_price": 50000,
    },
    {
        "name": "Mohammed Siraj", "nationality": "Indian", "role": "Bowler", "team": "GT",
        "batting_style": "Right-hand bat", "bowling_style": "Right-arm fast",
        "matches": 93, "strike_rate": 82.40, "base_price": 50000, "current_price": 50000,
    },
    {
        "name": "Yashasvi Jaiswal", "nationality": "Indian", "role": "Batsman", "team": "RR",
        "batting_style": "Left-hand bat", "bowling_style": "Leg break",
        "matches": 52, "strike_rate": 150.12, "base_price": 50000, "current_price": 50000,
    },
    {
        "name": "MS Dhoni", "nationality": "Indian", "role": "Wicketkeeper-Batsman", "team": "CSK",
        "batting_style": "Right-hand bat", "bowling_style": "Not Applicable",
        "matches": 264, "strike_rate": 137.53, "base_price": 50000, "current_price": 50000,
    },
    {
        "name": "Ravindra Jadeja", "nationality": "Indian", "role": "All-Rounder", "team": "CSK",
        "batting_style": "Left-hand bat", "bowling_style": "Slow left-arm orthodox",
        "matches": 240, "strike_rate": 129.82, "base_price": 50000, "current_price": 50000,
    },
    {
        "name": "Sanju Samson", "nationality": "Indian", "role": "Wicketkeeper-Batsman", "team": "RR",
        "batting_style": "Right-hand bat", "bowling_style": "Not Applicable",
        "matches": 168, "strike_rate": 139.14, "base_price": 50000, "current_price": 50000,
    },
    {
        "name": "Jos Buttler", "nationality": "Overseas", "role": "Wicketkeeper-Batsman", "team": "GT",
        "batting_style": "Right-hand bat", "bowling_style": "Not Applicable",
        "matches": 121, "strike_rate": 147.80, "base_price": 75000, "current_price": 75000,
    },
    {
        "name": "Travis Head", "nationality": "Overseas", "role": "Batsman", "team": "SRH",
        "batting_style": "Left-hand bat", "bowling_style": "Right-arm off break",
        "matches": 35, "strike_rate": 174.42, "base_price": 75000, "current_price": 75000,
    },
    {
        "name": "David Warner", "nationality": "Overseas", "role": "Batsman", "team": "Unsold Pool",
        "batting_style": "Left-hand bat", "bowling_style": "Leg break",
        "matches": 184, "strike_rate": 139.77, "base_price": 75000, "current_price": 75000,
    },
    {
        "name": "Glenn Maxwell", "nationality": "Overseas", "role": "All-Rounder", "team": "PBKS",
        "batting_style": "Right-hand bat", "bowling_style": "Right-arm off break",
        "matches": 134, "strike_rate": 156.73, "base_price": 75000, "current_price": 75000,
    },
    {
        "name": "Andre Russell", "nationality": "Overseas", "role": "All-Rounder", "team": "KKR",
        "batting_style": "Right-hand bat", "bowling_style": "Right-arm fast",
        "matches": 127, "strike_rate": 174.92, "base_price": 75000, "current_price": 75000,
    },
    {
        "name": "Sunil Narine", "nationality": "Overseas", "role": "All-Rounder", "team": "KKR",
        "batting_style": "Left-hand bat", "bowling_style": "Right-arm off break",
        "matches": 179, "strike_rate": 167.28, "base_price": 75000, "current_price": 75000,
    },
    {
        "name": "Pat Cummins", "nationality": "Overseas", "role": "Bowler", "team": "SRH",
        "batting_style": "Right-hand bat", "bowling_style": "Right-arm fast",
        "matches": 67, "strike_rate": 152.11, "base_price": 75000, "current_price": 75000,
    },
    {
        "name": "Mitchell Starc", "nationality": "Overseas", "role": "Bowler", "team": "DC",
        "batting_style": "Left-hand bat", "bowling_style": "Left-arm fast",
        "matches": 46, "strike_rate": 117.00, "base_price": 75000, "current_price": 75000,
    },
    {
        "name": "Phil Salt", "nationality": "Overseas", "role": "Wicketkeeper-Batsman", "team": "RCB",
        "batting_style": "Right-hand bat", "bowling_style": "Not Applicable",
        "matches": 30, "strike_rate": 175.40, "base_price": 75000, "current_price": 75000,
    },
    {
        "name": "Heinrich Klaasen", "nationality": "Overseas", "role": "Wicketkeeper-Batsman", "team": "SRH",
        "batting_style": "Right-hand bat", "bowling_style": "Not Applicable",
        "matches": 35, "strike_rate": 168.76, "base_price": 75000, "current_price": 75000,
    },
    {
        "name": "Nicholas Pooran", "nationality": "Overseas", "role": "Wicketkeeper-Batsman", "team": "LSG",
        "batting_style": "Left-hand bat", "bowling_style": "Not Applicable",
        "matches": 76, "strike_rate": 162.84, "base_price": 75000, "current_price": 75000,
    },
]


def seed_players_if_empty():
    if Player.query.count() > 0:
        return

    for item in SEED_PLAYERS:
        player = Player(
            name=item["name"],
            nationality=item["nationality"],
            role=item["role"],
            team=item["team"],
            batting_style=item["batting_style"],
            bowling_style=None if item["bowling_style"] == "Not Applicable" else item["bowling_style"],
            matches=item["matches"],
            strike_rate=item["strike_rate"],
            base_price=Decimal(str(item["base_price"])),
            current_price=Decimal(str(item["current_price"])),
            status="Available",
        )
        db.session.add(player)

    db.session.commit()


def parse_amount(value: str):
    try:
        return Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        return None


def register_routes(app: Flask):
    @app.route("/")
    def index():
        search = request.args.get("search", "").strip()
        nationality = request.args.get("nationality", "").strip()
        role = request.args.get("role", "").strip()
        team = request.args.get("team", "").strip()
        sort_by = request.args.get("sort_by", "name")

        query = Player.query

        if search:
            query = query.filter(Player.name.ilike(f"%{search}%"))
        if nationality:
            query = query.filter(Player.nationality == nationality)
        if role:
            query = query.filter(Player.role == role)
        if team:
            query = query.filter(Player.team == team)

        if sort_by == "price_desc":
            query = query.order_by(Player.current_price.desc())
        elif sort_by == "strike_rate_desc":
            query = query.order_by(Player.strike_rate.desc())
        else:
            query = query.order_by(Player.name.asc())

        players = query.all()
        nationalities = [
            item[0]
            for item in db.session.query(Player.nationality)
            .distinct()
            .order_by(Player.nationality)
            .all()
        ]
        roles = [
            item[0]
            for item in db.session.query(Player.role)
            .distinct()
            .order_by(Player.role)
            .all()
        ]
        teams = [
            item[0]
            for item in db.session.query(Player.team)
            .distinct()
            .order_by(Player.team)
            .all()
        ]

        total_players = Player.query.count()
        indian_players = Player.query.filter_by(nationality="Indian").count()
        highest_bid = db.session.query(func.max(Player.current_price)).scalar() or Decimal("0")

        return render_template(
            "index.html",
            players=players,
            nationalities=nationalities,
            roles=roles,
            teams=teams,
            total_players=total_players,
            indian_players=indian_players,
            highest_bid=highest_bid,
            selected_nationality=nationality,
            selected_role=role,
            selected_team=team,
            selected_sort=sort_by,
            search=search,
        )

    @app.route("/player/<int:player_id>")
    def player_detail(player_id):
        player = Player.query.get_or_404(player_id)
        history = (
            BidHistory.query
            .filter_by(player_id=player.id)
            .order_by(BidHistory.created_at.desc())
            .all()
        )
        return render_template("player_detail.html", player=player, history=history)

    @app.route("/player/<int:player_id>/bid", methods=["POST"])
    def place_bid(player_id):
        player = Player.query.get_or_404(player_id)
        bidder_name = request.form.get("bidder_name", "").strip() or "Anonymous Bidder"
        bid_amount = parse_amount(request.form.get("bid_amount", ""))

        if bid_amount is None:
            flash("Please enter a valid bid amount.", "danger")
            return redirect(url_for("player_detail", player_id=player.id))

        current_price = Decimal(str(player.current_price))
        base_price = Decimal(str(player.base_price))

        if bid_amount < base_price:
            flash(f"Bid cannot go below the auction starting price ₹{base_price:,.2f}.", "danger")
            return redirect(url_for("player_detail", player_id=player.id))

        if bid_amount < current_price:
            flash(f"Bid cannot go downward. Current quotation is ₹{current_price:,.2f}.", "danger")
            return redirect(url_for("player_detail", player_id=player.id))

        if bid_amount == current_price:
            flash("New quotation must be greater than the current quotation.", "warning")
            return redirect(url_for("player_detail", player_id=player.id))

        player.current_price = bid_amount
        player.status = "Bidding Active"

        bid = BidHistory(
            player_id=player.id,
            bidder_name=bidder_name,
            bid_amount=bid_amount
        )
        db.session.add(bid)
        db.session.commit()

        flash(
            f"Bid placed successfully for {player.name}. New quotation: ₹{bid_amount:,.2f}",
            "success"
        )
        return redirect(url_for("player_detail", player_id=player.id))

    @app.route("/seed/reset", methods=["POST"])
    def reset_demo_data():
        BidHistory.query.delete()
        Player.query.delete()
        db.session.commit()
        seed_players_if_empty()
        flash("Demo data reset successfully.", "success")
        return redirect(url_for("index"))


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)