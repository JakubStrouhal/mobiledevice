from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, DateField, TextAreaField, SelectField
from wtforms.validators import DataRequired, ValidationError
from models import DeviceMake, DeviceModel

class DeviceForm(FlaskForm):
    device_type = SelectField('Typ zařízení', choices=[('mobile_phone', 'Mobilní telefon')])
    make = SelectField('Výrobce', validators=[DataRequired()])
    model = SelectField('Model', validators=[DataRequired()])
    serial_number = StringField('Sériové číslo', validators=[DataRequired()])
    cost = FloatField('Cena')
    currency = SelectField('Měna', choices=[('CZK', 'CZK')])
    date_of_purchase = DateField('Datum nákupu')
    in_operation_from = DateField('V provozu od')
    note = TextAreaField('Poznámka')

    def __init__(self, *args, **kwargs):
        super(DeviceForm, self).__init__(*args, **kwargs)
        self.make.choices = [(m.name, m.name) for m in DeviceMake.query.order_by(DeviceMake.name).all()]
        if self.make.data:
            make = DeviceMake.query.filter_by(name=self.make.data).first()
            if make:
                self.model.choices = [(m.name, m.name) for m in DeviceModel.query.filter_by(make_id=make.id).order_by(DeviceModel.name).all()]

class AssignmentForm(FlaskForm):
    note = TextAreaField('Poznámka')
