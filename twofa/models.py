from sqlalchemy import Column, String, Boolean
from .database import Base
from werkzeug.security import generate_password_hash, check_password_hash


class User(Base):
    __tablename__ = 'users'

    username = Column(String(50), unique=True, primary_key=True)
    email = Column(String(120))
    authy_id = Column(String(12))
    pw_hash = Column(String(50))
    is_authenticated = Column(Boolean(), default=False)

    def __init__(self, username=None, email=None, password=None,
                 authy_id=None, is_authenticated=False):
        self.username = username
        self.email = email
        self.authy_id = authy_id
        self.is_authenticated = is_authenticated
        self.set_password(password)

    def __repr__(self):
        return '<User %r>' % (self.username)

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)

    def is_active(self):
        return True

    def get_id(self):
        return self.username

    def is_anonymous(self):
        return False

    @classmethod
    def load_user(cls, user_id):
        return cls.query.get(user_id)
