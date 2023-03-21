
import os
import hashlib
import datetime
from flask import Flask, request, make_response, Response, jsonify
from flask_cors import CORS
import http_status_codes as codes

from dotenv import load_dotenv 
load_dotenv()

import database.db as mongo
from database.model import Win, User
from flask_pymongo import ObjectId
from bson.json_util import dumps

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import current_user
from flask_jwt_extended import JWTManager

class JSONResponse(Response):
  default_mimetype = 'application/json'

class ApiFlask(Flask):
  response_class = JSONResponse

app = ApiFlask(__name__)

CORS(app)

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)
jwt = JWTManager(app)

# helper method for sending data back from API
def send(data, status_code):
  return make_response(dumps(data), status_code)

@app.route("/api/v1/users", methods=["POST"])
def register():
  new_user = request.get_json()
  new_user["password"] = hashlib.sha256(new_user["password"].encode("utf-8")).hexdigest()
  doc = mongo.db["users"].find_one({"email": new_user["email"]})
  if not doc:
    mongo.db["users"].insert_one(new_user)
    return jsonify({'msg': 'User created successfully'}), 201
  else:
    return jsonify({'msg': 'User already exists with that email'}), 409

@app.route("/api/v1/login", methods=['POST'])
def login():
  login_details = request.get_json()
  user_lookup = mongo.db["users"].find_one({'email': login_details["email"]})

  if user_lookup:
    encrypted_password = hashlib.sha256(login_details["password"].encode("utf-8")).hexdigest()
    if encrypted_password == user_lookup["password"]:
      access_token = create_access_token(identity=user_lookup["email"])
      return jsonify(access_token=access_token), 200
  return jsonify({'msg': 'The email or password is incorrect'}), 401

@app.route("/api/v1/user", methods=["GET"])
@jwt_required()
def get_user():
  current_user = get_jwt_identity()
  user_lookup = mongo.db["users"].find_one({'email': current_user})

  if user_lookup:
    del user_lookup['_id'], user_lookup['password']
    return jsonify({'profile' : user_lookup }), 200
  else:
    return jsonify({'msg': 'Profile not found'}), 404

@app.route('/api/v1/wins', methods = ['POST'])
def post_win():
  """
    Create a win using dataclass model
  """
  collection = mongo.db["wins"]
  form_data = request.json
  if "id" in form_data:
    form_data.pop("id")

  win = Win(**form_data)
  
  try:
    insert_id = str(collection.insert_one(win.__dict__).inserted_id)
    output = {'message': 'new document created', "_id": insert_id}
    return send(output, codes.HTTP_SUCCESS_CREATED)
  except Exception as e:
    output = {'error': str(e)}
    return send(output, codes.HTTP_BAD_REQUEST)

# @app.route('/api/v1/<collection_name>', methods = ['POST'])
# def post_document(collection_name):
#   """
#     Post one document to a collection
#   """
#   collection = getattr(mongo.db, collection_name)
#   form_data = request.json
#   try:
#     insert_id = str(collection.insert_one(form_data).inserted_id)
#     output = {'message': 'new document created', "_id": insert_id}
#     return send(output, codes.HTTP_SUCCESS_CREATED)
#   except Exception as e:
#     output = {'error': str(e)}
#     return send(output, codes.HTTP_BAD_REQUEST)

@app.route('/api/v1/<collection_name>', methods=['GET'])
def get_all_documents(collection_name):
  """
      Documents in a collection.
  """
  collection = getattr(mongo.db, collection_name)
  output = []
  for doc in collection.find():
      output.append(doc)
  return send(output, codes.HTTP_SUCCESS_GET_OR_UPDATE)

@app.route('/api/v1/<collection_name>/<id>', methods=['GET'])
def get_one_document(collection_name, id):
  """
    Get one item from a collection.
  """
  collection = getattr(mongo.db, collection_name)
  doc = collection.find_one({'_id': ObjectId(id)})
  if doc:
    return send(doc, codes.HTTP_SUCCESS_GET_OR_UPDATE)
  else:
    return send({'error' : 'document not found'}, codes.HTTP_NOT_FOUND)

@app.route('/api/v1/<collection_name>/<id>', methods=['PUT'])
def update_document(collection_name, id):
  """
    Update one item in collection.
  """
  collection = getattr(mongo.db, collection_name)
  doc = collection.find_one({'_id': ObjectId(id)})
  form_data = request.get_json()
  if doc:
    try:
      collection.update_one({"_id": ObjectId(id)}, {"$set": form_data})
      output = {'message': 'document updated', "_id": id}
      return send(output, codes.HTTP_SUCCESS_GET_OR_UPDATE)
    except Exception as e:
      output = {'error' : str(e)}
      return send(output, codes.HTTP_BAD_REQUEST)
  else:
    output = {'error' : 'document not found'}
    return send(output, codes.HTTP_NOT_FOUND)

@app.route('/api/v1/<collection_name>/<id>', methods=['DELETE'])
def delete_item(collection_name, id):
  """
    Delete one item from collection.
  """
  collection = getattr(mongo.db, collection_name)
  doc = collection.find_one({'_id': ObjectId(id)})
  if doc:
    try:
      collection.delete_one({"_id": doc["_id"]})
      return send("", codes.HTTP_SUCCESS_DELETED)
    except Exception as e:
      output = {'error' : str(e)}
      return send(output, codes.HTTP_BAD_REQUEST)
  else:
    output = {'error' : 'document not found'}
    return send(output, codes.HTTP_NOT_FOUND)

@app.route('/')
def flask_mongodb_atlas():
  return "flask mongodb atlas!"

if __name__ == '__main__':
    app.run(port=5000)
