import jwt 
from flask_bcrypt import  generate_password_hash
from flask_bcrypt import check_password_hash
from datetime import datetime
from datetime import datetime, timedelta
from flask import request,jsonify, Blueprint 
from flask_bcrypt import bcrypt 
from conn_db import *
from token_gen import * 
from __init__ import app 
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)
auth_routes = Blueprint("auth_routes", __name__)

conn = db_conn()
cur = conn.cursor()

@auth_routes.route('/signup', methods=['POST'])
def signup():
    try:
        data = UserSchema().load(request.json)
        id = data.get("id")
        uname = data.get("uname")
        email = data.get("email")
        password = data.get("password")
        role_id = data.get("role_id")
    except ValidationError as e:
        return jsonify({'error':e.messages}), 400    
    cur.execute('''select * FROM users where id=%s''', (id,))
    existing_user = cur.fetchone()
    if existing_user:
        return jsonify({'message': 'User already exists'}), 400
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    cur.execute('''INSERT INTO users(id,uname,email,password,role_id) VALUES(%s,%s,%s,%s,%s)''',
                (id, uname, email, hashed_password, role_id))
    conn.commit()
    return "Registerd Successfully"

@auth_routes.route('/login', methods=['POST'])
def login():
    data = request.json
    id = data.get("id")
    password = data.get("password")
    cur.execute('''SELECT role_id FROM users where id=%s''', (id,))
    rid = cur.fetchone()
    cur.execute('''SELECT password FROM users where id=%s''', (id,))
    user = cur.fetchone()
    if user:
        hashed_password = user[0]
        if check_password_hash(hashed_password, password):
            token = jwt.encode({
                'id': id,
                'role_id': rid,
                'exp': datetime.utcnow() + timedelta(seconds=9900)
            }, app.config['SECRET_KEY'], algorithm='HS256')
            conn.commit()
            return jsonify({'token': token}), 201
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    else:
        return jsonify({'error': 'User not found'}), 404


blacklist = set()

@auth_routes.route('/logout', methods=['POST'])
@token_required
def logout():
    token = request.headers.get('Authorization')
    if token:
        token = token.split()[1]
        blacklist.add(token)
        return jsonify({'message': 'logged out'}), 200
    else:
        return jsonify({'error': 'token is missing'}), 403