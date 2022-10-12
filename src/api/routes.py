from crypt import methods
from flask import Flask, Blueprint, jsonify, request
from api.models import User
from flask_jwt_extended import create_access_token

api = Blueprint('api', __name__)


@api.route('/user', methods=['GET'])
@api.route('/user/<int:id>', methods=['GET'])
def get_users(id=None):
  if request.method == 'GET':
    if id is not None:
      user = User.get_user(id)
      if type(user) == User:
        return user.serialize()
      if user is None:
        return jsonify({'message':"User not found"}), 404
      return jsonify(user), 500
    
    if id is None:
      users = User.get_all_users()
      if users:
        return jsonify(list(map(lambda user: user.serialize(), users))), 200
      else:
        return jsonify(users),500
  return jsonify({'message':'method not allowed'}),405

@api.route('/user', methods=['POST'])
def create_user():
  if request.method == 'POST':
    data = request.json
    if data is None:
      return jsonify({'message':'Bad request'}), 400
    if data.get('email') is None:
      return jsonify({'message':'Bad request'}), 400
    if data.get('fullname') is None:
      return jsonify({'message':'Bad request'}), 400

    user = User.create(data)
    if type(user) == User:
      return user.serialize(), 201
    if user is None:
      return jsonify({'message':'User already exists'}), 409
    return jsonify(user), 500
  return jsonify({'message':'method not allowed'}),405


@api.route('/login', methods=['POST'])
def login():
  if request.method == 'POST':
    data = request.json
    if data is None:
      return jsonify({'message':'Bad request'}), 400
    if data.get('email') is None:
      return jsonify({'message':'Bad request'}), 400
    if data.get('password') is None:
      return jsonify({'message':'Bad request'}), 400

    user = User.login(data["email"], data["password"])
    if type(user) == User:
      access_token = create_access_token(identity=user.id)
      return jsonify(access_token=access_token), 200
    if user is None:
      return jsonify({'message':'User not found'}), 404
    return jsonify(user), 500
  return jsonify({'message':'method not allowed'}),405


