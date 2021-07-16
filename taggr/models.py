from taggr import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from taggr import login


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.String(128))
    square_api_key = db.Column(db.String(128))
    dymo_printer_name = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


@login.user_loader
def load_user(userid):
    return User.query.get(int(userid))
