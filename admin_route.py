 
from flask import Blueprint
from conn_db import db_conn 
from token_gen import * 
from role import * 
import jwt 
from flask import request,jsonify


admin_routes = Blueprint("admin_routes", __name__)

conn = db_conn()
cur = conn.cursor()


@admin_routes.route('/get_admin', methods=['GET'])
@token_required
def get_admin():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'token is missing'}), 403
    try:
        token = token.split(" ")[1]
        payload = jwt.decode(
            token, app.config['SECRET_KEY'], algorithms=['HS256'])
        role_id = payload.get('role_id')
        print(role_id[0])
        if role_id[0] == 2:
            cur.execute('''select * from users where role_id=%s''',
                        (role_id[0],))
            data = cur.fetchall()
            conn.commit()
            return jsonify(data)
        else:
            return jsonify({'error': 'insufficient permission'})
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'token has expired'}), 403
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid Token'}), 403


@admin_routes.route('/get_posts', methods=['GET'])
@role_required(2)
def get_posts():
    cur.execute('''select pid,content,created_at from post''')
    data = cur.fetchall()
    return jsonify(data)


@admin_routes.route('/get_post/<int:id>', methods=['GET'])
@role_required(2)
def get_post(id):
    cur.execute('''select pid,content,created_at from post where id=%s''', (id,))
    data = cur.fetchall()
    conn.commit()
    return jsonify(data)


@admin_routes.route('/update_post/<int:id>', methods=['PUT'])
@role_required(2)
def update_post(id):
    pid = request.json['pid']
    content = request.json['content']
    cur.execute(
        '''UPDATE post SET pid=%s, content=%s WHERE id=%s''', (
            pid, content, id,)
    )
    conn.commit()
    return jsonify({'message': 'item updated successfully'})


@admin_routes.route('/delete_post/<int:id>', methods=['DELETE'])
@role_required(2)
def delete_post(id):
    cur.execute('''delete from post where id=%s''', (id,))
    conn.commit()
    return jsonify({'message': 'Post deleted successfully'})


@admin_routes.route('/create/likedata', methods=['POST'])
@role_required(2)
def create_likedata():
    data = request.json
    lid = data.get('lid')
    post_id = data.get('post_id')
    name = data.get('name')
    content = data.get('content')
    cur.execute(
        '''select count(uid) from post where pid=%s and likes='True' ''',(post_id,))
    total = cur.fetchone()
    cur.execute('''insert into likedata(lid,post_id,name,content,tc) values(%s,%s,%s,%s,%s)''',
                (lid, post_id, name, content, total))
    conn.commit()
    return jsonify(data)