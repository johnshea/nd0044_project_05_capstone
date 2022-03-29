from flask_sqlalchemy import SQLAlchemy

database_name = 'capstone'
database_path = 'postgresql://{}:{}@{}/{}'.format(
  'postgres', 'postgres', 'localhost:5432', database_name
)

db = SQLAlchemy()

def setup_db(app, database_path=database_path):
  app.config['SQLALCHEMY_DATABASE_URI'] = database_path
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
  db.app = app
  db.init_app(app)
  db.create_all()
  return db


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
