from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, DateField, TextAreaField, SelectField
from wtforms.validators import DataRequired, ValidationError
from models import DeviceMake, DeviceModel, PhoneStatus, DeviceMakeEnum, DeviceModelEnum

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
        self.make.choices = [(make.value, make.value) for make in DeviceMakeEnum]
        
        if self.make.data:
            models = DeviceModelEnum.get_models_for_make(self.make.data)
            self.model.choices = models

class AssignmentForm(FlaskForm):
    note = TextAreaField('Poznámka')
