from webapp import db, login_manager, app
from flask_login import UserMixin
import os
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    reg_no = db.Column(db.String(10), unique=True, nullable=False)
    dept = db.Column(db.String(10), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    #profile_pic = db.Column(db.String(20), nullable=False, default="default.jpg")
    #dob = db.Column(db.Date, nullable=False)
    mobile = db.Column(db.String(10), nullable=False)

    #comma seperated event ids
    events = db.Column(db.String(100))

    def get_reset_token(self, expiry_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expiry_sec)
        return s.dumps( {'user_id': self.id} ).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.name}', '{self.email}', '{self.reg_no}', '{self.mobile}', [{self.events}])"


class Events(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.String(5), nullable=False)
    reg_no = db.Column(db.String(5*10+4), nullable=False)
    time = db.Column(db.String(20), nullable=False) # "YYYY-MM-DD HH:MM:SS" (19 characters long)
    def __repr__(self):
        return f"Events('{self.event_id}', '[{self.reg_no}]', '{self.time}')"


with app.app_context():
    if "database.db" not in os.listdir():
        db.create_all()
