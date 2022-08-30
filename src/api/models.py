from datetime import datetime
from enum import Enum
import os
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from base64 import b64encode


db = SQLAlchemy()


class UserRol(Enum):
	ADMINISTRATOR='administrator',
	GENERAL ='general'


class UserStatus(Enum):
	ACTIVE = "active",
	DISABLED = "disabled",
	DELETE = "delete"


class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(80), unique=True, nullable=False)
  fullname = db.Column(db.String(80), nullable=False)
  password = db.Column(db.String(250), nullable=False, default="")
  salt = db.Column(db.String(120), nullable=False)
  created_at = db.Column(db.DateTime(timezone=False), nullable=False)
  rol = db.Column(db.Enum(UserRol), nullable=False, default="GENERAL")
  status = db.Column(db.Enum(UserStatus), nullable=False, default="ACTIVE")
  # unore = db.relationship('Unore', backref='user', uselist=True)
  # news = db.relationship('News', backref='user', uselist=True)


  def serialize(self):
    return {
      'id':self.id,
      'fullname':self.fullname,
      'email':self.email,
      'created_at': self.created_at,
      'salt':self.salt,
			'password':self.password,
      'status':self.status.value,
			'rol':self.rol.value
    }

  def set_password(self, password):
    self.password = generate_password_hash(f'{password}{self.salt}')
  

  def get_user(id):
    try:
      user = User.query.get(id)
      print(user.status)
      if user is not None:
        return user
      else:
        return None
    except Exception as error:
      return {'error':500}


  def get_users():
    try:
      users = User.query.all()
      return users
    except Exception as error:
      return {'error':error.args}


  @classmethod
  def create(cls, data):
    try:
      data = cls(**data)
      data.set_password(data.password)
      data.created_at = datetime.now()
      data.salt = b64encode(os.urandom(32)).decode("utf-8")
      db.session.add(data)
      db.session.commit()
      return data

    except Exception as error:
      db.session.rollback()
      return None
    
  