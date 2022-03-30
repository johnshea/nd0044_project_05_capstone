from urllib.request import urlopen
from flask import Flask, jsonify, abort, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import json
from models import setup_db, Check, Employee
from auth import AuthError, requires_auth


def create_app(test_config=None):
    app = Flask(__name__)
    db = setup_db(app)

    @app.route('/', methods=['GET'])
    def index():
        return "Hello Capstone!"

    @app.route('/checks', methods=['GET'])
    @requires_auth('read:checks')
    def all_checks(permissions):
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

            all_employees_formatted = \
                [employee.format() for employee in all_employees]

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
        except Exception as e:
            if e.code == 404:
                abort(404)
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
                abort(404)

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
            if e.code == 404:
                abort(404)
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

    return app
