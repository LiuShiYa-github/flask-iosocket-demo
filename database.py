from flask import Flask
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'l%3ya7fn3moipdpcltj(tdfcv5^@lj=t5d&72levvls+y*@_4^'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@10.0.0.10:3306/demo'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db.init_app(app)


class Host(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(128), nullable=False)
    port = db.Column(db.String(128), nullable=False)
    username = db.Column(db.String(128), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    add_date = db.Column(db.DateTime, nullable=False, default=datetime.now)


with app.app_context():
    db.create_all()
