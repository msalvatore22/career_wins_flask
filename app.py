from flask import Flask
import db
import json
from bson import json_util


app = Flask(__name__)

def parse_json(data):
    return json.loads(json_util.dumps(data))

@app.route('/')
def flask_mongodb_atlas():
    return "flask mongodb atlas!"


#test to insert data to the data base
@app.route("/test")
def test():
    findOne = db.collection.find_one()
    return parse_json(findOne)

if __name__ == '__main__':
    app.run(port=5000)