from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from common.broker import publish_game_result
import json

app = Flask(__name__)

app.secret_key = "your_secret_key"


@app.route("/")
def home():
    return render_template("home.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        if username:
            session["username"] = username
            return redirect(url_for("game"))
        else:
            error_message = "Введите имя пользователя"
            return render_template("login.html", error=error_message)
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("home"))


@app.route("/game")
def game():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("game.html", username=session["username"])


@app.route("/submit_score", methods=["POST"])
def submit_score():
    if "username" not in session:
        return jsonify({"error": "Пользователь не авторизован"}), 401

    data = request.get_json()
    score = data.get("score")
    username = session["username"]

    if score is None:
        return jsonify({"error": "Отсутствует значение счета"}), 400

    message = json.dumps({"username": username, "score": score})
    publish_game_result(message)

    return jsonify({"status": "success"})


@app.route("/scoreboard")
def scoreboard():
    return render_template("scoreboard.html")


if __name__ == "__main__":
    app.run(port=5000, debug=True)
