# game_service/app.py
from flask import Flask, render_template, request, redirect, url_for, session
from common.broker import publish_game_result
import json

# Указываем явный путь к шаблонам
app = Flask(__name__, template_folder="game_service/templates")
app.secret_key = "your_secret_key"

# … Остальной код приложения


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["username"] = request.form.get("username")
        return redirect(url_for("game"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("home"))

@app.route("/game")
def game():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("game.html")

@app.route("/submit_score", methods=["POST"])
def submit_score():
    if "username" not in session:
        return ("Пользователь не авторизован", 401)
    data = request.get_json()
    score = data.get("score")
    username = session["username"]
    # Формируем сообщение для отправки в RabbitMQ
    message = json.dumps({"username": username, "score": score})
    publish_game_result(message)
    return {"status": "success"}

if __name__ == "__main__":
    app.run(port=5000, debug=True)
