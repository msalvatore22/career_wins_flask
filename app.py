import os
from flask import Flask, request, make_response
import database.db as mongo
from flask_pymongo import ObjectId
import json
from bson.json_util import dumps
from flask_cors import CORS
import http_status_codes as codes

app = Flask(__name__)
CORS(app)

# helper method for sending data back from API
def send(data, status_code):
  return make_response(dumps(data), status_code)

@app.route('/api/v1/<collection_name>', methods = ['POST'])
def post_document(collection_name):
  """
    Post one document to a collection
  """
  collection = getattr(mongo.db, collection_name)
  form_data = request.json
  try:
    insert_id = str(collection.insert_one(form_data).inserted_id)
    output = {'message': 'new document created', "_id": insert_id}
    return send(output, codes.HTTP_SUCCESS_CREATED)
  except Exception as e:
    output = {'error': str(e)}
    return send(output, codes.HTTP_BAD_REQUEST)

@app.route('/api/v1/<collection_name>', methods=['GET'])
def get_all_documents(collection_name):
  """
      Documents in a collection.
  """
  collection = getattr(mongo.db, collection_name)
  output = []
  for q in collection.find():
      output.append(q)
  return send(output, codes.HTTP_SUCCESS_GET_OR_UPDATE)

@app.route('/api/v1/<collection_name>/<id>', methods=['GET'])
def get_one_documents(collection_name, id):
  """
    Get one item from a collection.
  """
  collection = getattr(mongo.db, collection_name)
  doc = collection.find_one({'_id': ObjectId(id)})
  if doc:
    return send(doc, codes.HTTP_SUCCESS_GET_OR_UPDATE)
  else:
    return send({'error' : 'item not found'}, codes.HTTP_NOT_FOUND)

@app.route('/api/v1/<collection_name>/<id>', methods=['PUT'])
def update_document(collection_name, id):
  """
    Update one item in collection.
  """
  collection = getattr(mongo.db, collection_name)
  doc = collection.find_one({'_id': ObjectId(id)})
  if doc:
    for key in request.json.keys():
      doc[key] = request.json[key]
    try:
      collection.replace_one({"_id": ObjectId(id)}, doc)
      output = {'message' : 'item updated'}
      return send(output, codes.HTTP_SUCCESS_GET_OR_UPDATE)
    except Exception as e:
      output = {'error' : str(e)}
      return send(output, codes.HTTP_BAD_REQUEST)
  else:
    output = {'error' : 'item not found'}
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
    output = {'error' : 'item not found'}
    return send(output, codes.HTTP_NOT_FOUND)

@app.route('/')
def flask_mongodb_atlas():
  return "flask mongodb atlas!"

if __name__ == '__main__':
    app.run(port=5000)
