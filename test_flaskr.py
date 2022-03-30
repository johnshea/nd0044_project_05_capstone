import unittest
import json
from flaskr import create_app
from models import setup_db, Check, Employee
import os

SERVER_TOKEN = os.environ['SERVER_TOKEN']
MANAGER_TOKEN = os.environ['MANAGER_TOKEN']

database_path = os.environ['DATABASE_URL_TEST']
if database_path.startswith("postgres://"):
  database_path = database_path.replace("postgres://", "postgresql://", 1)

class RestaurantTestCase(unittest.TestCase):
  def setUp(self) -> None:
      self.app = create_app()
      self.client = self.app.test_client
      self.database_path = database_path
      db = setup_db(self.app, self.database_path)

  def tearDown(self) -> None:
      pass

  def test_get_checks_endpoint_by_public(self):
      res = self.client().get('/checks')

      self.assertEqual(res.status_code, 401)

  def test_get_checks_endpoint_by_server(self):
      headers = {
          "Authorization": "Bearer " + SERVER_TOKEN
      }

      res = self.client().get('/checks', headers=headers)
      data = res.get_json()

      total_checks_counts = len(Check.query.all())

      self.assertEqual(res.status_code, 200)
      self.assertEqual(data['total_checks'], total_checks_counts)
      self.assertTrue(data['checks'])

  def test_get_checks_endpoint_by_manager(self):
      headers = {
          "Authorization": "Bearer " + MANAGER_TOKEN
      }

      res = self.client().get('/checks', headers=headers)
      data = res.get_json()

      total_checks_counts = len(Check.query.all())

      self.assertEqual(res.status_code, 200)
      self.assertEqual(data['total_checks'], total_checks_counts)
      self.assertTrue(data['checks'])

  def test_get_employees_endpoint_by_public(self):
      res = self.client().get('/employees')

      self.assertEqual(res.status_code, 401)

  def test_get_employees_endpoint_by_server(self):
      headers = {
          "Authorization": "Bearer " + SERVER_TOKEN
      }

      res = self.client().get('/employees', headers=headers)
      data = res.get_json()

      total_employees_counts = len(Employee.query.all())

      self.assertEqual(res.status_code, 200)
      self.assertEqual(data['total_employees'], total_employees_counts)
      self.assertTrue(data['employees'])


  def test_get_employees_endpoint_by_manager(self):
      headers = {
          "Authorization": "Bearer " + MANAGER_TOKEN
      }

      res = self.client().get('/employees', headers=headers)
      data = res.get_json()

      total_employees_counts = len(Employee.query.all())

      self.assertEqual(res.status_code, 200)
      self.assertEqual(data['total_employees'], total_employees_counts)
      self.assertTrue(data['employees'])

  def test_post_employees_endpoint_by_public(self):
      res = self.client().post('/employees')

      self.assertEqual(res.status_code, 401)

  def test_post_employees_endpoint_by_server(self):
      headers = {
          "Authorization": "Bearer " + SERVER_TOKEN
      }

      res = self.client().post('/employees', headers=headers)
      self.assertEqual(res.status_code, 403)

  def test_post_employees_endpoint_by_manager(self):
      headers = {
          "Authorization": "Bearer " + MANAGER_TOKEN,
          "Content-Type": "application/json"
      }

      body_json = { "name": "New Employee" }
      res = self.client().post('/employees', json=body_json, headers=headers)
      data = res.get_json()

      total_employees_counts = len(Employee.query.all())

      self.assertEqual(res.status_code, 200)
      self.assertEqual(data['success'], True)
      self.assertTrue(data['id'], 5)

  def test_patch_employees_endpoint_by_public(self):
      res = self.client().patch('/employees/2')

      self.assertEqual(res.status_code, 401)

  def test_patch_employees_endpoint_by_server(self):
      headers = {
          "Authorization": "Bearer " + SERVER_TOKEN
      }

      res = self.client().patch('/employees/2', headers=headers)
      self.assertEqual(res.status_code, 403)

  def test_patch_employees_endpoint_by_manager(self):
      headers = {
          "Authorization": "Bearer " + MANAGER_TOKEN,
          "Content-Type": "application/json"
      }

      body_json = { "name": "Updated Employee" }
      res = self.client().patch('/employees/2', json=body_json, headers=headers)
      data = res.get_json()

      updated_employee = Employee.query.get(2)

      self.assertEqual(res.status_code, 200)
      self.assertEqual(data['success'], True)
      self.assertTrue(data['id'], 2)
      self.assertEqual(updated_employee.name, "Updated Employee")

  def test_delete_employees_endpoint_by_public(self):
      res = self.client().delete('/employees/3')

      self.assertEqual(res.status_code, 401)

  def test_delete_employees_endpoint_by_server(self):
      headers = {
          "Authorization": "Bearer " + SERVER_TOKEN
      }

      res = self.client().delete('/employees/3', headers=headers)
      self.assertEqual(res.status_code, 403)

  def test_delete_employees_endpoint_by_manager(self):
      headers = {
          "Authorization": "Bearer " + MANAGER_TOKEN,
          "Content-Type": "application/json"
      }

      body_json = { "name": "Updated Employee" }
      res = self.client().delete('/employees/3', json=body_json, headers=headers)
      data = res.get_json()

      updated_employee = Employee.query.get(3)

      self.assertEqual(res.status_code, 200)
      self.assertEqual(data['success'], True)
      self.assertTrue(data['id'], 3)
      self.assertIsNone(updated_employee)

if __name__ == '__main__':
    unittest.main()
