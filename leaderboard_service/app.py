from flask import Flask, render_template
from common.database import SessionLocal
from account_service.models import User

app = Flask(__name__)

@app.route("/")
def leaderboard():
    db = SessionLocal()
    users = db.query(User).order_by(User.high_score.desc()).all()
    db.close()
    return render_template("leaderboard.html", users=users)

if __name__ == "__main__":
    app.run(port=5002, debug=True)
