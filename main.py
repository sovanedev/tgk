from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
#import jwt
import secrets
import random

app = Flask(__name__)

base_dir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(base_dir, 'db.db')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SECRET_KEY'] = secrets.token_hex(16)

db = SQLAlchemy(app)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    mail = db.Column(db.String(50), nullable = True)
    age = db.Column(db.Integer, nullable = True)
    sex = db.Column(db.String(50), nullable = True)
    access = db.Column(db.Integer, nullable=False)
    token = db.Column(db.String(200), nullable=False)

def generate_token(user_id):
    payload = {
        'user_id': user_id,
    }
    token = random.randint(1000000, 132312312312)
    return token

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    login = data.get('login')
    password = data.get('password')

    existing_user = Users.query.filter_by(login=login).first()
    if existing_user:
        return jsonify({"message": "User already exists"}), 400

    new_user = Users(login=login, password=password, access=0)
    new_user.token = generate_token(new_user.id)
    
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully", "token": new_user.token})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    login = data.get('login')
    password = data.get('password')

    user = Users.query.filter_by(login=login, password=password).first()
    if user is None:
        return jsonify({"message": "Invalid username or password"}), 401

    return jsonify({"token": user.token})

@app.route('/db', methods=['POST'])
def get_items():
    data = request.get_json('token')
    token = data.get('token')

    if token is None:
        return jsonify({"message": "Token not provided in the request parameters."}), 401

    user = Users.query.filter_by(token=token).first()

    if user is None:
        return jsonify({"message": "Invalid token."}), 401

    return jsonify({
        "user_id": user.id,
        "name": user.login,
        "access": user.access,
        "mail": user.mail,
        "age": user.age,
        "sex": user.sex,
        "password": user.password,
        "token": user.token
    })

@app.route("/edit", methods=["POST"])
def edit():
    data = request.get_json()
    token = data["Token"]
    user = Users.query.filter_by(token=token).first()

    if not user:
        return jsonify({"message": "Invalid token."}), 404

    if "Age" in data and data["Age"] > 0:
        user.age = data["Age"]
    if "Sex" in data:
        user.sex = data["Sex"]
    if "Name" in data:
        user.login = data["Name"]
    if "Password" in data:
        user.password = data["Password"]
    if "Mail" in data:
        user.mail = data["Mail"]

    db.session.commit()

    return jsonify({"message": "Changes saved successfully."}), 200

@app.route("/listen", methods=["POST"])
def listen():
    data = request.get_json()
    if data["Token"]:
        return jsonify({"listening": request.get_json()})
    else:
        return jsonify({"message": "Вы не авторизованы."})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=1337)
