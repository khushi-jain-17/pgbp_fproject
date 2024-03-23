import jwt 
# from flask_bcrypt import generate_password_hash
# from flask_bcrypt import check_password_hash
# from datetime import datetime
# from datetime import datetime, timedelta
from flask import request,jsonify
from functools import wraps 
from __init__ import app 


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'token is missing'}), 403
        try:
            token = token.split(" ")[1]
            payload = jwt.decode(
                token, app.config['SECRET_KEY'], algorithms=['HS256'])
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'token has expired'}), 403
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid Token'}), 403
    return decorated