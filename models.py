from datetime import datetime
from enum import Enum
from extensions import db

class DeviceMakeEnum(str, Enum):
    SAMSUNG = "Samsung"
    APPLE = "Apple"
    HUAWEI = "Huawei"
    XIAOMI = "Xiaomi"
    GOOGLE = "Google"
    MOTOROLA = "Motorola"
    NOKIA = "Nokia"

class DealerEnum(str, Enum):
    ALZA = "Alza"
    DATART = "Datart"
    MALL = "Mall"
    CZC = "CZC"
    TSBOHEMIA = "TS Bohemia"
    O2 = "O2"
    VODAFONE = "Vodafone"
    TMOBILE = "T-Mobile"

class DeviceModelEnum:
    MODELS = {
        DeviceMakeEnum.SAMSUNG: [
            # A Series
            ("A12", "Galaxy A12"),
            ("A13", "Galaxy A13"),
            ("A14", "Galaxy A14"),
            ("A23", "Galaxy A23"),
            ("A24", "Galaxy A24"),
            ("A34", "Galaxy A34"),
            ("A54", "Galaxy A54"),
            # S Series
            ("S21", "Galaxy S21"),
            ("S21P", "Galaxy S21+"),
            ("S21U", "Galaxy S21 Ultra"),
            ("S22", "Galaxy S22"),
            ("S22P", "Galaxy S22+"),
            ("S22U", "Galaxy S22 Ultra"),
            ("S23", "Galaxy S23"),
            ("S23P", "Galaxy S23+"),
            ("S23U", "Galaxy S23 Ultra"),
            # Z Series (Foldables)
            ("ZF4", "Galaxy Z Fold 4"),
            ("ZF5", "Galaxy Z Fold 5"),
            ("ZFL4", "Galaxy Z Flip 4"),
            ("ZFL5", "Galaxy Z Flip 5")
        ],
        DeviceMakeEnum.APPLE: [
            # Latest iPhone Models
            ("IP15PM", "iPhone 15 Pro Max"),  # Latest flagship
            ("IP15PR", "iPhone 15 Pro"),
            ("IP15P", "iPhone 15 Plus"),
            ("IP15", "iPhone 15"),
            # Previous Generation
            ("IP14PM", "iPhone 14 Pro Max"),
            ("IP14PR", "iPhone 14 Pro"),
            ("IP14P", "iPhone 14 Plus"),
            ("IP14", "iPhone 14"),
            ("IP13PM", "iPhone 13 Pro Max"),
            ("IP13PR", "iPhone 13 Pro")
        ],
        DeviceMakeEnum.HUAWEI: [
            ("P40", "P40 Pro"),
            ("P30", "P30 Lite")
        ]
    }

    @staticmethod
    def get_models_for_make(make: DeviceMakeEnum):
        return DeviceModelEnum.MODELS.get(make, [])

class DeviceMake(db.Model):
    """Device manufacturers catalog"""
    __tablename__ = 'device_make'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False, unique=True)
    text = db.Column(db.String(100), nullable=False)
    models = db.relationship('DeviceModel', backref='make', lazy=True)
    phones = db.relationship('Phone', backref='make', lazy=True)

    @staticmethod
    def get_choices():
        return [(make.value, make.value) for make in DeviceMakeEnum]

class DeviceModel(db.Model):
    """Device models catalog"""
    __tablename__ = 'device_model'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False)
    text = db.Column(db.String(100), nullable=False)
    make_id = db.Column(db.Integer, db.ForeignKey('device_make.id'), nullable=False)
    phones = db.relationship('Phone', backref='model', lazy=True)
    __table_args__ = (db.UniqueConstraint('make_id', 'code', name='uq_model_make_code'),)

from enum import Enum

class PhoneStatus(str, Enum):
    INSTOCK = "INSTOCK"
    ISSUED = "ISSUED"
    TERMINATED = "TERMINATED"

class Phone(db.Model):
    """Phones inventory"""
    __tablename__ = 'phones'
    id = db.Column(db.Integer, primary_key=True)
    make_id = db.Column(db.Integer, db.ForeignKey('device_make.id'), nullable=False)
    model_id = db.Column(db.Integer, db.ForeignKey('device_model.id'), nullable=False)
    serial_number = db.Column(db.String(100), unique=True, nullable=False)
    buying_price = db.Column(db.Numeric(10, 2))
    status = db.Column(db.String(20), nullable=False, default=PhoneStatus.INSTOCK.value)
    dealer = db.Column(db.String(50))  # Will store DealerEnum values
    purchased = db.Column(db.Date)
    note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    assignments = db.relationship('PhoneAssignment', backref='phone', lazy=True)
    sim_assignments = db.relationship('PhoneSimAssignment', backref='phone', lazy=True)

class SimCard(db.Model):
    """SIM cards inventory"""
    __tablename__ = 'sim_cards'
    id = db.Column(db.Integer, primary_key=True)
    serial_number = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(20))
    status = db.Column(db.String(20), nullable=False, default='INSTOCK')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    phone_assignments = db.relationship('PhoneSimAssignment', backref='sim_card', lazy=True)

class PhoneSimAssignment(db.Model):
    """Phone-SIM card assignments"""
    __tablename__ = 'phone_sim_assignments'
    id = db.Column(db.Integer, primary_key=True)
    phone_id = db.Column(db.Integer, db.ForeignKey('phones.id'), nullable=False)
    sim_id = db.Column(db.Integer, db.ForeignKey('sim_cards.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_date = db.Column(db.Date, nullable=False)
    returned_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='sim_assignments')

class User(db.Model):
    """Users"""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    position = db.Column(db.String(100))
    country = db.Column(db.String(2), default='CZ')  # ISO country code
    state = db.Column(db.String(20), default='active')  # active, maternity_leave, inactive
    entry_date = db.Column(db.Date)
    exit_date = db.Column(db.Date)
    assignments = db.relationship('PhoneAssignment', backref='user', lazy=True)

class PhoneAssignment(db.Model):
    """Phone assignments"""
    __tablename__ = 'phone_assignments'
    id = db.Column(db.Integer, primary_key=True)
    phone_id = db.Column(db.Integer, db.ForeignKey('phones.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_date = db.Column(db.Date, nullable=False)
    returned_date = db.Column(db.Date)
    note = db.Column(db.Text)
    protocol_number = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
