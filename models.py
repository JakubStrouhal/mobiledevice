from datetime import datetime
from app import db

class DeviceMake(db.Model):
    """Číselník výrobců"""
    __tablename__ = 'device_make'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False, unique=True)
    text = db.Column(db.String(100), nullable=False)
    models = db.relationship('DeviceModel', backref='make', lazy=True)
    phones = db.relationship('Phone', backref='make', lazy=True)

class DeviceModel(db.Model):
    """Číselník modelů"""
    __tablename__ = 'device_model'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False)
    text = db.Column(db.String(100), nullable=False)
    make_id = db.Column(db.Integer, db.ForeignKey('device_make.id'), nullable=False)
    phones = db.relationship('Phone', backref='model', lazy=True)
    __table_args__ = (db.UniqueConstraint('make_id', 'code', name='uq_model_make_code'),)

class Phone(db.Model):
    """Telefony"""
    __tablename__ = 'phones'
    id = db.Column(db.Integer, primary_key=True)
    make_id = db.Column(db.Integer, db.ForeignKey('device_make.id'), nullable=False)
    model_id = db.Column(db.Integer, db.ForeignKey('device_model.id'), nullable=False)
    serial_number = db.Column(db.String(100), unique=True, nullable=False)
    buying_price = db.Column(db.Numeric(10, 2))
    state = db.Column(db.String(20), default='active')  # active, inactive, maintenance
    note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    assignments = db.relationship('PhoneAssignment', backref='phone', lazy=True)

class User(db.Model):
    """Uživatelé"""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    position = db.Column(db.String(100))
    state = db.Column(db.String(20), default='active')
    assignments = db.relationship('PhoneAssignment', backref='user', lazy=True)

class PhoneAssignment(db.Model):
    """Přiřazení telefonů"""
    __tablename__ = 'phone_assignments'
    id = db.Column(db.Integer, primary_key=True)
    phone_id = db.Column(db.Integer, db.ForeignKey('phones.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_date = db.Column(db.Date, nullable=False)
    returned_date = db.Column(db.Date)
    note = db.Column(db.Text)
    protocol_number = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
