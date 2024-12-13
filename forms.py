from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, TextAreaField, SelectField
from wtforms.validators import DataRequired, ValidationError
from models import DeviceMakeEnum, DeviceModelEnum, PhoneStatus, DealerEnum
from wtforms.fields import DateField

class PhoneForm(FlaskForm):
    make = SelectField('Make', validators=[DataRequired()])
    model = SelectField('Model', validators=[DataRequired()])
    serial_number = StringField('Serial Number', validators=[DataRequired()])
    buying_price = DecimalField('Buying Price', places=2)
    status = SelectField('Status', validators=[DataRequired()], choices=[
        (PhoneStatus.INSTOCK.value, 'In Stock'),
        (PhoneStatus.ISSUED.value, 'Issued'),
        (PhoneStatus.TERMINATED.value, 'Terminated')
    ])
    dealer = SelectField('Dealer', validators=[DataRequired()])
    purchased = DateField('Purchase Date', format='%Y-%m-%d')
    note = TextAreaField('Note')

    def __init__(self, *args, **kwargs):
        super(PhoneForm, self).__init__(*args, **kwargs)
        self.make.choices = [(make.value, make.value) for make in DeviceMakeEnum]
        self.dealer.choices = [(dealer.value, dealer.value) for dealer in DealerEnum]
        
        # Set model choices based on selected make or default to first make's models
        if self.make.data:
            try:
                make_enum = DeviceMakeEnum(self.make.data)
                models = DeviceModelEnum.get_models_for_make(make_enum)
                self.model.choices = [(code, text) for code, text in models]
            except ValueError:
                self.model.choices = []
        else:
            first_make = next(iter(DeviceMakeEnum))
            models = DeviceModelEnum.get_models_for_make(first_make)
            self.model.choices = [(code, text) for code, text in models]

class AssignmentForm(FlaskForm):
    note = TextAreaField('Note')
