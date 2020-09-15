from werkzeug.security import generate_password_hash, check_password_hash
from shanthanu import db
from flask_login import UserMixin
from shanthanu import login
from datetime import datetime


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return self.username

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    body = db.Column(db.Text)
    category = db.Column(db.String(100))
    description = db.Column(db.String(255))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    tags = db.Column(db.String(100))

    def __repr__(self):
        return self.title
