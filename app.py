from flask import Flask, jsonify, abort, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

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


@app.route('/', methods=['GET'])
def index():
  return "Hello Capstone!"

@app.route('/checks', methods=['GET'])
# @requires_auth('get:checks')
def all_checks():
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
# @requires_auth('get:employees')
def all_employees():
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
# @requires_auth('delete:employees')
# def delete_employee(permission, employee_id):
def delete_employee(employee_id):
  try:
    deleted_employee = Employee.query.get(employee_id)

    if not deleted_employee:
      abort(404)
    
    db.session.delete(deleted_employee)
    db.session.commit()

    return jsonify({
      'success': True,
      'employee_id': employee_id
    })
  except Exception:
    abort(400)

@app.route('/employees', methods=['POST'])
# @requires_auth('create:employees')
def post_employees():
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
# @requires_auth('patch:employees')
def patch_employee(employee_id):
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
      'employee_id': employee_id
    })
  except Exception as e:
    abort(400)
