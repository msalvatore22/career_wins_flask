from .db import db

class Movie(db.Document):
  title = db.StringField(required=True)
  description = db.StringField()
  
    