from urllib.request import urlopen
from flask import Flask, jsonify, abort, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from functools import wraps
import json
import requests
from jose import jwt

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Check(db.Model):
  __tablename__ = 'checks'

  id = db.Column(db.Integer, primary_key=True)
  employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)

  def format(self):
    return {
      'id': self.id,
      'employee_id': self.employee_id
    }

  def __str__(self):
    return f'<str Check id=${self.id}, employee_id=${self.employee_id}>'

  def __repr__(self):
    return f'<repr Check id=${self.id}, employee_id=${self.employee_id}>'


class Employee(db.Model):
  __tablename__ = 'employees'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(), nullable=False)
  checks = db.relationship('Check', backref='employee')

  def __str__(self):
    return f'<Employee id=${self.id}, name=${self.name}>'

  def __repr__(self):
    return f'<Employee id=${self.id}, name=${self.name}>'

  def format(self):
    return {
      'id': self.id,
      'name': self.name
    }


AUTH0_DOMAIN = 'nd0044-project-05-capstone.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'restaurant'

class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

def get_token_auth_header():
    headers = request.headers
    if 'Authorization' not in headers:
        raise AuthError({
            "success": False,
            "error": 401,
            "message": "auth header not found"},
            401
        )
    else:
        auth_header = headers.get('Authorization')
        auth_info = auth_header.split()
        if len(auth_info) < 2:
            raise AuthError({
                "success": False,
                "error": 401,
                "message": "Authorization header length is not 2"},
                401
            )
        if auth_info[0].lower() != 'bearer':
            raise AuthError({
                "success": False,
                "error": 401,
                "message": "Bearer keyword not found Authorization header"},
                401
            )
        token = auth_header.split()[1]
        return token

def verify_decode_jwt(token):
    jsonurl = requests.get(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = jsonurl.json()

    try:
      unverified_header = jwt.get_unverified_header(token)
    except:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)
    
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }

    if rsa_key:
        try:
            # USE THE KEY TO VALIDATE THE JWT
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description':
                    'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 400)

def check_permissions(permission, payload):
    if 'permissions' not in payload:
        raise AuthError({
            "success": False,
            "error": 400,
            "message": "Permissions key not found in JWT"},
            400
        )

    if permission not in payload['permissions']:
        raise AuthError({
            "success": False,
            "error": 403,
            "message": "Permission not found"},
            403
        )

    return True

def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                token = get_token_auth_header()
                payload = verify_decode_jwt(token)
                check_permissions(permission, payload)
            except AuthError as ae:
                abort(ae.status_code)

            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator

@app.route('/', methods=['GET'])
# @requires_auth('')
def index():
  # print("JWT2: ", jwt)
  return "Hello Capstone!"

@app.route('/checks', methods=['GET'])
@requires_auth('read:checks')
def all_checks(permissions):
  print("permissions: ", permissions)
  try:
    all_checks = Check.query.order_by(Check.id).all()

    all_checks_formatted = [check.format() for check in all_checks]

    return jsonify({
      'success': True,
      'checks': all_checks_formatted,
      'total_checks': len(all_checks_formatted)
    })
  except Exception:
      abort(400)  

@app.route('/employees', methods=['GET'])
@requires_auth('read:employees')
def all_employees(permissions):
  try:
    all_employees = Employee.query.order_by(Employee.id).all()

    all_employees_formatted = [employee.format() for employee in all_employees]

    return jsonify({
      'success': True,
      'employees': all_employees_formatted,
      'total_employees': len(all_employees_formatted)
    })
  except Exception:
    abort(400)

@app.route('/employees/<int:employee_id>', methods=['DELETE'])
@requires_auth('delete:employees')
def delete_employee(permissions, employee_id):
  try:
    deleted_employee = Employee.query.get(employee_id)

    if not deleted_employee:
      abort(404)
    
    db.session.delete(deleted_employee)
    db.session.commit()

    return jsonify({
      'success': True,
      'id': employee_id
    })
  except Exception:
    abort(400)

@app.route('/employees', methods=['POST'])
@requires_auth('create:employees')
def post_employees(permissions):
  try:
    data = request.get_json()

    if not data:
      abort(400)

    name = data.get('name', None)

    if not name:
      abort(400)

    new_employee = Employee(name=name)
    db.session.add(new_employee)
    db.session.commit()

    return jsonify({
      'success': True,
      'id': new_employee.id
    })
  except Exception:
    abort(400)

@app.route('/employees/<int:employee_id>', methods=['PATCH'])
@requires_auth('update:employees')
def patch_employee(permissions, employee_id):
  try:
    employee_to_update = Employee.query.get(int(employee_id))

    if not employee_to_update:
      abort(400)

    data = request.get_json()

    name = data.get('name', None)

    if not name:
      abort(400)

    employee_to_update.name = name
    db.session.add(employee_to_update)
    db.session.commit()

    return jsonify({
      'success': True,
      'id': employee_id
    })
  except Exception as e:
    abort(400)

@app.errorhandler(403)
def auth_error_403(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "Forbidden"
    }), 403


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Unprocessable"
    }), 422


@app.errorhandler(404)
def auth_error_404(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Not Found"
    }), 404


@app.errorhandler(401)
def auth_error_401(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Unauthorized"
    }), 401

