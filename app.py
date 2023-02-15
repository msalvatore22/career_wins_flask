from flask import Flask, request
import database.db as db
import json
from bson import json_util


app = Flask(__name__)

def parse_json(data):
    return json.loads(json_util.dumps(data))

@app.route('/')
def flask_mongodb_atlas():
    return "flask mongodb atlas!"

@app.route('/api/v1/wins', methods = ['GET'])
def get_wins():
  return parse_json(db.wins.find())


# @app.route('/api/v1/wins', methods = ['POST'])
# def get_wins():
#   raw_win = request.get_json()
  
#   return 

if __name__ == '__main__':
    app.run(port=5000)
