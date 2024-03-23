from __init__ import app 


app.config['SECRET_KEY'] = "this is secret"

from auth import auth_routes
app.register_blueprint(auth_routes)

from user_route import user_routes
app.register_blueprint(user_routes)

from admin_route import admin_routes
app.register_blueprint(admin_routes)

if __name__ == '__main__':
    app.run(debug=True)



