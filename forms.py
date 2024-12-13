from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, DateField, TextAreaField, SelectField
from wtforms.validators import DataRequired, ValidationError
from models import DeviceMake, DeviceModel, PhoneStatus

class PhoneForm(FlaskForm):
    make = SelectField('Výrobce', validators=[DataRequired()])
    model = SelectField('Model', validators=[DataRequired()])
    serial_number = StringField('Sériové číslo', validators=[DataRequired()])
    buying_price = FloatField('Kupní cena')
    status = SelectField('Stav', choices=[
        (PhoneStatus.INSTOCK.value, 'Skladem'),
        (PhoneStatus.ISSUED.value, 'Vydáno'),
        (PhoneStatus.TERMINATED.value, 'Ukončeno')
    ])
    note = TextAreaField('Poznámka')

    def __init__(self, *args, **kwargs):
        super(PhoneForm, self).__init__(*args, **kwargs)
        self.make.choices = [(m.code, m.text) for m in DeviceMake.query.order_by(DeviceMake.text).all()]
        if self.make.data:
            make = DeviceMake.query.filter_by(code=self.make.data).first()
            if make:
                self.model.choices = [(m.code, m.text) for m in DeviceModel.query.filter_by(make_id=make.id).order_by(DeviceModel.text).all()]

class AssignmentForm(FlaskForm):
    note = TextAreaField('Poznámka')
