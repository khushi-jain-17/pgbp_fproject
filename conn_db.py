import psycopg2 
from marshmallow import Schema, fields, validate, ValidationError 
import re

class EmailValidator:
    @staticmethod
    def validate_email(email):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValidationError('Invalid email address')

class PasswordValidator:
    @staticmethod
    def validate_password(password):
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long')

        if not re.search(r'[A-Z]', password):
            raise ValidationError('Password must contain at least one uppercase letter')

        if not re.search(r'[a-z]', password):
            raise ValidationError('Password must contain at least one lowercase letter')

        if not re.search(r'[0-9]', password):
            raise ValidationError('Password must contain at least one digit')

        if not re.search(r'[\W]', password):
            raise ValidationError('Password must contain at least one special character')


class UserSchema(Schema):
    uid = fields.Integer(dump_only = True)
    uname = fields.String(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True, validate=EmailValidator.validate_email)
    password = fields.String(required=True, validate=PasswordValidator.validate_password)
    role_id = fields.Integer(required=True)


class RoleSchema(Schema):
    rid = fields.Integer(dump_only=True)
    rname = fields.String(required=True, validate=validate.Length(min=1, max=50))

def db_conn():
    conn = psycopg2.connect(
        database='pgbp',
        host='localhost',
        user='postgres',
        password='1719',
        port='5432'
    )
    return conn 
