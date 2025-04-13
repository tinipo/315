# account_service/app.py
from flask import Flask, render_template, request, redirect, url_for, session
from common.database import engine, SessionLocal
from models import Base, User, GameResult
from common.broker import consume_game_results
import threading
import json

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Создаём таблицы, если их ещё нет
Base.metadata.create_all(bind=engine)

# Callback для обработки результатов игры, полученных через RabbitMQ
def game_result_callback(ch, method, properties, body):
    data = json.loads(body)
    username = data.get("username")
    score = data.get("score")
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    if user:
        # Записываем новый результат игры
        game_result = GameResult(score=score, owner=user)
        db.add(game_result)
        db.commit()
        # Обновляем high score
        if score > user.high_score:
            user.high_score = score
        # Вычисляем среднее значение
        games = db.query(GameResult).filter(GameResult.user_id == user.id).all()
        if games:
            user.average_score = sum(g.score for g in games) / len(games)
        db.commit()
    db.close()
    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_consumer():
    consume_game_results(game_result_callback)

# Запускаем RabbitMQ консьюмера в отдельном потоке
consumer_thread = threading.Thread(target=start_consumer, daemon=True)
consumer_thread.start()

@app.route("/")
def home():
    if "username" in session:
        return redirect(url_for("profile"))
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = SessionLocal()
        if db.query(User).filter(User.username == username).first():
            db.close()
            return "Пользователь с таким именем уже существует!"
        new_user = User(username=username, password=password)
        db.add(new_user)
        db.commit()
        db.close()
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = SessionLocal()
        user = db.query(User).filter(User.username == username, User.password == password).first()
        db.close()
        if user:
            session["username"] = username
            return redirect(url_for("profile"))
        return "Неверные данные для входа!"
    return render_template("login.html")

@app.route("/profile")
def profile():
    if "username" not in session:
        return redirect(url_for("login"))
    username = session["username"]
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    db.close()
    return render_template("profile.html", user=user)

if __name__ == "__main__":
    app.run(port=5001, debug=True)
