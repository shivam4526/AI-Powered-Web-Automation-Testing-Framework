from __future__ import annotations

from functools import wraps

from flask import Flask, jsonify, render_template, request, session

from .db import add_to_cart, clear_cart, get_cart, get_products, init_db


app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.config["SECRET_KEY"] = "demo-secret-key"

init_db()


def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        username = session.get("username")
        if not username:
            return jsonify({"error": "Authentication required"}), 401
        return view_func(*args, **kwargs)

    return wrapper


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/login")
def login():
    payload = request.get_json(silent=True) or request.form
    username = payload.get("username", "").strip()
    password = payload.get("password", "").strip()

    if username == "demouser" and password == "Password123":
        session["username"] = username
        return jsonify({"message": "Login successful", "username": username})

    return jsonify({"error": "Invalid username or password"}), 401


@app.post("/logout")
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})


@app.get("/products")
@login_required
def products():
    search = request.args.get("search", "")
    return jsonify({"products": get_products(search)})


@app.get("/cart")
@login_required
def cart():
    username = session["username"]
    items = get_cart(username)
    total = round(sum(item["line_total"] for item in items), 2)
    return jsonify({"items": items, "total": total})


@app.post("/cart")
@login_required
def add_cart():
    payload = request.get_json(silent=True) or {}
    product_id = int(payload.get("product_id", 0))
    quantity = int(payload.get("quantity", 1))

    if product_id <= 0 or quantity <= 0:
        return jsonify({"error": "Invalid cart payload"}), 400

    add_to_cart(session["username"], product_id, quantity)
    items = get_cart(session["username"])
    return jsonify({"message": "Product added to cart", "items": items})


@app.post("/checkout")
@login_required
def checkout():
    username = session["username"]
    items = get_cart(username)
    if not items:
        return jsonify({"error": "Cart is empty"}), 400

    total = round(sum(item["line_total"] for item in items), 2)
    clear_cart(username)
    return jsonify(
        {
            "message": "Checkout complete",
            "order_summary": {
                "items_count": len(items),
                "total": total,
                "status": "confirmed",
            },
        }
    )
