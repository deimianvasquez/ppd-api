from crypt import methods
from flask import Flask, Blueprint, jsonify, request
from api.models import User


api = Blueprint('api', __name__)


@api.route('/user', methods=['GET'])
@api.route('/user/<int:id>', methods=['GET'])
def get_user(id=None):
  if request.method == 'GET':
    if id is not None:
      user = User.get_user(id)
      if user is not None:
        return user.serialize()
      else:
        return jsonify({'message':"User not found"}), 404

    else:
      users = User.get_users()
      return jsonify(list(map(lambda user: user.serialize(), users))), 200
  return jsonify({'message':'method not allowed'})


@api.route('/signup', methods=['POST'])
def add_user():
  if request.method == 'POST':
    user_data = request.json

    if set(('email', 'fullname', 'password')).issubset(user_data):
      user = User.query.filter_by(email=user_data['email']).one_or_none()
      print(user)
      if user is None:
        new_user = User.create(user_data)
        if new_user is not None:
          return jsonify(new_user.serialize()), 201
        else:
          return jsonify({"message":"Error, try again, if the error persists contact your system administrator"}), 500
      else:
        return jsonify({'message':"the email already register"}), 400

    else:
      return jsonify({'message':"all fields are required email, fullname and password"}), 400
