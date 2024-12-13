from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask import current_app
from models import (
    Phone, DeviceMake, DeviceModel, PhoneStatus,
    User, PhoneAssignment, PhoneSimAssignment
)
from forms import PhoneForm
from app import db
from datetime import datetime

devices = Blueprint('devices', __name__)

@devices.route('/')
def list_devices():
    # Create a demo user if none exists
    user = User.query.first()
    if not user:
        user = User(
            employee_id='110657',
            first_name='Renata',
            last_name='Lišková',
            position='Office Manager',
            email='renata.liskova@example.com',
            country='CZ'
        )
        db.session.add(user)
        db.session.commit()
    
    # Get all devices with their assignments
    devices = Phone.query.all()
    
    # Get devices assigned to the demo user
    user_devices = Phone.query\
        .join(PhoneAssignment)\
        .filter(
            PhoneAssignment.user_id == user.id,
            PhoneAssignment.returned_date.is_(None)
        ).all()
    
    # Count assigned devices and SIM cards
    device_count = len(user_devices)
    sim_count = PhoneSimAssignment.query.filter(
        PhoneSimAssignment.user_id == user.id,
        PhoneSimAssignment.returned_date.is_(None)
    ).count()
    
    return render_template('devices/list.html',
                         devices=devices,
                         user=user,
                         user_devices=user_devices,
                         device_count=device_count,
                         sim_count=sim_count)

@devices.route('/<int:id>')
def device_detail(id):
    device = Phone.query.get_or_404(id)
    return render_template('devices/detail.html', device=device)

@devices.route('/<int:id>/edit', methods=['GET', 'POST'])
def device_edit(id):
    device = Phone.query.get_or_404(id)
    form = PhoneForm(obj=device)
    
    if form.validate_on_submit():
        form.populate_obj(device)
        db.session.commit()
        flash('Device updated successfully', 'success')
        return redirect(url_for('devices.device_detail', id=device.id))
        
    return render_template('devices/edit.html', form=form, device=device)

@devices.route('/<int:id>/return', methods=['POST'])
def device_return(id):
    device = Phone.query.get_or_404(id)
    device.status = PhoneStatus.INSTOCK.value
    db.session.commit()
    flash('Device returned successfully', 'success')
    return redirect(url_for('devices.device_detail', id=device.id))

@devices.route('/<int:id>/sign-off', methods=['POST'])
def device_sign_off(id):
    device = Phone.query.get_or_404(id)
    device.status = PhoneStatus.TERMINATED.value
    db.session.commit()
    flash('Device signed off successfully', 'success')
    return redirect(url_for('devices.device_detail', id=device.id))

@devices.route('/new', methods=['GET', 'POST'])
def device_new():
    form = PhoneForm()
    if form.validate_on_submit():
        try:
            device = Phone()
            form.populate_obj(device)
            
            # Get or create make
            make = DeviceMake.query.filter_by(code=form.make.data).first()
            if not make:
                make = DeviceMake(code=form.make.data, text=form.make.data)
                db.session.add(make)
                db.session.flush()
            
            # Get or create model
            model = DeviceModel.query.filter_by(code=form.model.data, make_id=make.id).first()
            if not model:
                model = DeviceModel(
                    code=form.model.data,
                    text=dict(DeviceModelEnum.get_models_for_make(DeviceMakeEnum(form.make.data))).get(form.model.data, form.model.data),
                    make_id=make.id
                )
                db.session.add(model)
                db.session.flush()
            
            device.make_id = make.id
            device.model_id = model.id
            device.status = PhoneStatus.INSTOCK.value
            
            db.session.add(device)
            db.session.commit()
            flash('New device added successfully', 'success')
            return redirect(url_for('devices.device_detail', id=device.id))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating new device: {str(e)}")
            flash('Error creating new device', 'error')
            
    return render_template('devices/edit.html', form=form)

@devices.route('/models/<make>')
def get_models(make):
    try:
        make_enum = DeviceMakeEnum(make)
        models = DeviceModelEnum.get_models_for_make(make_enum)
        return jsonify([(code, text) for code, text in models])
    except ValueError:
        return jsonify([]), 404


@devices.route('/employee/new', methods=['GET', 'POST'])
def employee_new():
    form = EmployeeForm()
    if form.validate_on_submit():
        try:
            employee = User(
                employee_id=form.employee_id.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                position=form.position.data,
                country=form.country.data,
                state=form.state.data,
                entry_date=form.entry_date.data
            )
            db.session.add(employee)
            db.session.commit()
            flash('New employee added successfully', 'success')
            return redirect(url_for('devices.list_devices'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating new employee: {str(e)}")
            flash('Error creating new employee', 'error')
    return render_template('devices/employee_new.html', form=form)