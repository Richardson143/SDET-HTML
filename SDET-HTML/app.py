from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
from routes.auth import auth_bp
from routes.main import main_bp
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)

Session(app)

if __name__ == "__main__":
    app.run(debug=True)