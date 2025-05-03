from model.base import Base
from flask_sqlalchemy import SQLAlchemy

print("Creating DB")
db = SQLAlchemy(model_class=Base)