
from flask import Blueprint 
from conn_db import db_conn 
from token_gen import * 
from role import * 
import jwt 
from datetime import datetime
from flask import request,jsonify


user_routes = Blueprint("user_routes", __name__)

conn = db_conn()
cur = conn.cursor()


@user_routes.route('/get_users', methods=['GET'])
@token_required
def get_users():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'token is missing'}), 403
    try:
        token = token.split(" ")[1]
        payload = jwt.decode(
            token, app.config['SECRET_KEY'], algorithms=['HS256'])
        role_id = payload.get('role_id')
        print(role_id[0])
        if role_id[0] == 1:
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


@user_routes.route('/connect', methods=['POST'])
@role_required(1)
def connect_users():
    data = request.json
    cid = data.get('cid')
    follower_id = data.get('follower_id')
    following_id = data.get('following_id')
    cur.execute('''insert into connection(cid,follower_id,following_id) values(%s,%s,%s)''',
                (cid, follower_id, following_id))
    conn.commit()
    return jsonify(data)


@user_routes.route('/create_post', methods=['POST'])
@role_required(1)
def create():
    data = request.json
    pid = data.get('pid')
    content = data.get('content')
    likes = data.get('likes')
    uid = data.get('uid')
    id = data.get('id')
    current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    cur.execute('''insert into post(pid,content,likes,created_at,uid,id) values(%s,%s,%s,%s,%s,%s)''',
                (pid, content, likes, current_time, uid, id))
    conn.commit()
    return jsonify(data)



@user_routes.route('/post_of_user/<string:uname>', methods=['GET'])
@role_required(1)
def posts_of_user(uname):
    # cur.execute(
    #     '''select pid,content,created_at from post where id=%s''', (id,))
    cur.execute(
        '''select post.content,post.created_at from post inner join users on post.uid=users.uid where users.uname=%s''', (uname,))
    data = cur.fetchall()
    conn.commit()
    return jsonify(data)


@user_routes.route('/like_post', methods=['POST'])
@role_required(1)
def like_post():
    data = request.json
    pk = data.get('pk')
    uid = data.get('uid')
    likes = data.get('likes')
    pid = data.get('pid')
    cur.execute(
        '''insert into post(pk,uid,likes,pid) values(%s,%s,%s,%s)''', (pk,uid, likes, pid))
    conn.commit()
    return jsonify({'message':'Like'})


@user_routes.route('/like_count/<int:pid>', methods=['GET'])
@role_required(1)
def count_likes(pid):
    cur.execute(
        '''select count(uid) from post where pid=%s and likes='True' ''', (pid,))
    data = cur.fetchall()
    return jsonify(data)


@user_routes.route('/posts_liked_by_user/<int:uid>', methods=['GET'])
@role_required(1)
def posts_liked_by_user(uid):
    cur.execute('''select pid,content,likes from post where uid=%s''', (uid,))
    data = cur.fetchall()
    return jsonify(data)


@user_routes.route('/liked_by/<int:pid>', methods=['GET'])
@role_required(1)
def people_liked_the_post(pid):
    cur.execute('''select users.uname, post.uid from users inner join post on users.uid=post.uid where post.pid=%s and likes='True' ''', (pid,))
    data = cur.fetchall()
    return jsonify(data)


@user_routes.route('/home/<int:uid>', methods=['GET'])
@role_required(1)
def home(uid):
    cur.execute('''select pid from post where uid=%s and likes='True' ''', (uid,))
    p = cur.fetchone()
    cur.execute(
        '''select likedata.name,likedata.content, likedata.tc from likedata inner join post on likedata.uid = post.uid where post.pid=%s  ''',(p,))
    data = cur.fetchall()
    return jsonify(data)


@user_routes.route('/users',methods=['GET'])
def users():
    page = request.args.get("page",default=1, type=int)
    per_page = request.args.get("per_page",default=5, type=int)
    offset = (page-1) * per_page
    cur.execute("select * from users limit %s offset %s",(per_page, offset))
    data = cur.fetchall()
    conn.commit()
    return jsonify({ "data": data })
    
