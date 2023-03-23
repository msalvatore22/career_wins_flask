
import os
import datetime
import bcrypt
from flask import Flask, request, make_response, Response, jsonify
from flask_cors import CORS
import http_status_codes as codes

from dotenv import load_dotenv 
load_dotenv()

import database.db as mongo
from database.model import Win, User
from flask_pymongo import ObjectId
from bson.json_util import dumps

from flask_jwt_extended import (
  create_access_token, 
  get_jwt_identity,
  jwt_required,
  current_user,
  JWTManager
  )

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

def user_lookup():
  current_user = get_jwt_identity()
  user_lookup = mongo.db["users"].find_one({'email': current_user})
  return user_lookup

# Register a new user
@app.route("/api/v1/users", methods=["POST"])
def register():
  form_data = request.get_json()
  if "id" in form_data:
    form_data.pop("id")

  form_data["password"] = bcrypt.hashpw(form_data["password"].encode('utf-8'), bcrypt.gensalt(rounds=15)) 
  new_user = User(**form_data)
  doc = mongo.db["users"].find_one({"email": new_user.email})

  if not doc:
    mongo.db["users"].insert_one(new_user.__dict__)
    return jsonify({'msg': 'User created successfully'}), 201
  else:
    return jsonify({'msg': 'User already exists with that email'}), 409

# Login a user
@app.route("/api/v1/login", methods=['POST'])
def login():
  login_details = request.get_json()
  user_lookup = mongo.db["users"].find_one({'email': login_details["email"]})

  if user_lookup: 
    if bcrypt.checkpw(login_details["password"].encode('utf-8'), user_lookup["password"]):
      access_token = create_access_token(identity=user_lookup["email"])
      return jsonify(access_token=access_token), 200
  return jsonify({'msg': 'The email or password is incorrect'}), 401

# Get user
@app.route("/api/v1/user", methods=["GET"])
@jwt_required()
def get_user():
  user = user_lookup()
  if user:
    del user['_id'], user['password']
    return jsonify({'user' : user }), 200
  else:
    return jsonify({'msg': 'Profile not found'}), 404

# Add win to user document
@app.route('/api/v1/wins', methods = ['POST'])
@jwt_required()
def post_win():
  """
    Insert a new win into user collection
  """
  user = user_lookup()
  
  form_data = request.json
  if "id" in form_data:
    form_data.pop("id")

  win = Win(**form_data)
  
  try:
    mongo.db["users"].update_one({'email': user["email"]}, {'$push': { "wins": win.__dict__ }})
    output = {'message': "inserted new win"}
    return send(output, codes.HTTP_SUCCESS_CREATED)
  except Exception as e:
    output = {'error': str(e)}
    return send(output, codes.HTTP_BAD_REQUEST)

# Delete win from user document
@app.route('/api/v1/wins/<id>', methods = ['DELETE'])
@jwt_required()
def delete_win(id):
  """
    Delete win from user collection
  """
  user = user_lookup()

  try:
    mongo.db["users"].update_one({'email': user["email"]}, {'$pull': { "wins": {"id": id} }})
    output = {'message': f"Deleted win id {id}"}
    print(output)
    return send(output, codes.HTTP_SUCCESS_DELETED)
  except Exception as e:
    output = {'error': str(e)}
    return send(output, codes.HTTP_BAD_REQUEST)

# Get a win from user document by win id
@app.route('/api/v1/wins/<id>', methods=['GET'])
@jwt_required()
def get_one_document(id):
  """
    Get one win from user collection
  """
  user = user_lookup()

  user_wins = user["wins"]
  win = next(win for win in user_wins if win["id"] == id)
  if win:
    return send(win, codes.HTTP_SUCCESS_GET_OR_UPDATE)
  else:
    return send({'error' : 'document not found'}, codes.HTTP_NOT_FOUND)

# Update a win from user document by win id
@app.route('/api/v1/wins/<id>', methods=['PUT'])
@jwt_required()
def update_document(id):
  """
    Update one item in collection.
  """
  user = user_lookup() 
  form_data = request.get_json()
  if user:
    try:
      mongo.db["users"].find_one_and_update({'email': user["email"], "wins.id": id}, {'$set': {
        "wins.$.title": form_data["title"],
        "wins.$.description": form_data["description"],
        "wins.$.impact": form_data["impact"],
        "wins.$.winDate": form_data["winDate"],
        "wins.$.favorite": form_data["favorite"],
        "wins.$.updatedAt": datetime.datetime.utcnow()
      }})
      output = {'message': 'win updated', "id": id}
      return send(output, codes.HTTP_SUCCESS_GET_OR_UPDATE)
    except Exception as e:
      output = {'error' : str(e)}
      return send(output, codes.HTTP_BAD_REQUEST)
  else:
    output = {'error' : 'user not found'}
    return send(output, codes.HTTP_NOT_FOUND)

@app.route('/')
def flask_mongodb_atlas():
  return "flask mongodb atlas!"

if __name__ == '__main__':
    app.run(port=5000)
