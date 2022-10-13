from crypt import methods
from flask import Flask, Blueprint, jsonify, request
from api.models import User, Unore, News
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import cloudinary.uploader as uploader

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
      return jsonify({'message':'User already exists'}), 400
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


@api.route('/unore', methods=['GET'])
def get_unore():
  unore = Unore.get_unore()
  if unore is not None:
    return jsonify(list(map(lambda item: item.serialize(), unore))), 200
  if unore is None: 
    return jsonify({'message':"Unore not found"}), 404
  return jsonify(unore), 500


@api.route('/unore', methods=['POST'])
@jwt_required()
def create_unore():
  if request.method == 'POST':
    data = request.json
    data.update({'user_id':get_jwt_identity()})
    if data is None:
      return jsonify({'message':'Bad request'}), 400
    if data.get('amount') is None:
      return jsonify({'message':'Bad request'}), 400
    
    unore = Unore.create(data)
    if type(unore) == Unore:
      return unore.serialize(), 201
    if unore is None:
      return jsonify({'message':'Error try again later'}), 500
    
    unore = Unore.create(data)
    if type(unore) == Unore:
      return unore.serialize(), 201
    if unore is None:
      return jsonify({'message':'Error try again later'}), 500
    return jsonify(unore), 500
  return jsonify({'message':'method not allowed'}),405


@api.route('/news', methods=['GET'])
def get_news():
  news = News.get_news()
  if news is not None:
    return jsonify(list(map(lambda item: item.serialize(), news))), 200
  if news is None: 
    return jsonify({'message':"News not found"}), 404
  return jsonify(news), 500


@api.route('/news', methods=['POST'])
@jwt_required()
def create_news():
  if request.method == 'POST':
    data_files = request.files
    data_form = request.form
    data = {
      'title':data_form.get('title'),
      'subtitle':data_form.get('subtitle'),
      'summary':data_form.get('summary'),
      'complete':data_form.get('complete'),
      'user_id':get_jwt_identity(),
      'image':data_files.get('image'),
      'image_secondary':data_files.get('image_secondary'),
      'image_preview':data_files.get('image_preview')
    }
    if data is None:
      return jsonify({'message':'Bad request'}), 400
    if data.get('title') is None:
      return jsonify({'message':'Bad request'}), 400
    if data.get('subtitle') is None:  
      return jsonify({'message':'Bad request'}), 400
    if data.get('summary') is None:
      return jsonify({'message':'Bad request'}), 400
    if data.get('complete') is None:
      return jsonify({'message':'Bad request'}), 400
    if data.get('image') is None:
      return jsonify({'message':'Bad request'}), 400
    if data.get('image_secondary') is None:
      return jsonify({'message':'Bad request'}), 400
    if data.get('image_preview') is None:
      return jsonify({'message':'Bad request'}), 400

    res_image = uploader.upload(data_files["image"])
    res_image_secondary = uploader.upload(data_files["image_secondary"])
    res_image_preview = uploader.upload(data_files["image_preview"])

    data.update({'image':res_image['secure_url']})
    data.update({'image_secondary':res_image_secondary['secure_url']})
    data.update({'image_preview':res_image_preview['secure_url']})
    data.update({'public_id_image':res_image['public_id']})
    data.update({'public_id_secondary':res_image_secondary['public_id']})
    data.update({'public_id_preview':res_image_preview['public_id']})

   
    news = News.create(data)
    if type(news) == News:
      return news.serialize(), 201
    if news is None:
      uploader.destroy(data['public_id_image'])
      uploader.destroy(data['public_id_secondary'])
      uploader.destroy(data['public_id_preview'])
      return jsonify({'message':'Error try again later'}), 500
    return jsonify(news), 500
  return jsonify({'message':'method not allowed'}),405
