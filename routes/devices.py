from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask import current_app
from sqlalchemy import text
from models import (
    Phone, DeviceMake, DeviceModel, PhoneStatus,
    User, PhoneAssignment, PhoneSimAssignment
)
from forms import PhoneForm, EmployeeForm
from extensions import db
from datetime import datetime

devices = Blueprint('devices', __name__)

@devices.route('/')
def list_devices():
    try:
        # Get status filter from query params, default to showing only active
        show_inactive = request.args.get('show_inactive', '0') == '1'
        
        # Query users based on active status filter
        query = User.query
        if not show_inactive:
            query = query.filter(User.state == 'active')
        users = query.all()
        
        current_app.logger.info(f"Retrieved {len(users)} users (show_inactive={show_inactive})")

        # Get devices and counts for each user
        for user in users:
            # Get device count
            user.phone_count = PhoneAssignment.query.filter(
                PhoneAssignment.user_id == user.id,
                PhoneAssignment.returned_date.is_(None)
            ).count()
            
            # Get SIM count
            user.sim_count = PhoneSimAssignment.query.filter(
                PhoneSimAssignment.user_id == user.id,
                PhoneSimAssignment.returned_date.is_(None)
            ).count()

    # Get all devices for the view
    devices = Phone.query.all()

    # Keep existing user data for context panel (using the first user for simplicity)
    user_devices = []
    device_count = 0
    sim_count = 0
    if users:
        user = users[0] # Using the first user for context panel
        user_devices = Phone.query\
            .join(PhoneAssignment)\
            .filter(
                PhoneAssignment.user_id == user.id,
                PhoneAssignment.returned_date.is_(None)
            ).all()
        device_count = len(user_devices)
        sim_count = PhoneSimAssignment.query.filter(
            PhoneSimAssignment.user_id == user.id,
            PhoneSimAssignment.returned_date.is_(None)
        ).count()
    else:
        user = None

    return render_template('devices/list.html',
                         devices=devices,
                         users=users, # Changed from employees
                         user=user,
                         user_devices=user_devices,
                         device_count=device_count,
                         sim_count=sim_count,
                         show_inactive=show_inactive)

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
    """Create a new employee endpoint.

    GET: Display the employee creation form
    POST: Handle form submission and create new employee
    """
    form = EmployeeForm()
    if request.method == 'POST':
        current_app.logger.info("Processing employee creation form submission")
        current_app.logger.debug(f"Form data received: {request.form}")

        if not form.validate():
            current_app.logger.warning("Form validation failed")
            for field, errors in form.errors.items():
                for error in errors:
                    current_app.logger.error(f"Validation error - {field}: {error}")
                    flash(f'{field}: {error}', 'error')
            return render_template('devices/employee_new.html', form=form), 400

        try:
            # Create new employee instance with form data
            employee = User(
                employee_id=form.employee_id.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                position=form.position.data or None,  # Handle optional fields
                country=form.country.data or 'CZ',   # Default to CZ if not provided
                state=form.state.data or 'active',   # Default to active if not provided
                entry_date=form.entry_date.data
            )

            current_app.logger.info(f"Creating new employee: {employee.first_name} {employee.last_name}")
            current_app.logger.debug(f"Employee data: {vars(employee)}")

            # Add and commit to database
            db.session.add(employee)
            db.session.commit()

            current_app.logger.info(f"Successfully created employee with ID: {employee.id}")
            flash('New employee added successfully', 'success')
            return redirect(url_for('devices.list_devices'))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating new employee: {str(e)}")
            # Provide more user-friendly error message
            if 'duplicate key' in str(e):
                flash('An employee with this ID already exists', 'error')
            else:
                flash('Error creating employee. Please try again.', 'error')
            return render_template('devices/employee_new.html', form=form), 400

    return render_template('devices/employee_new.html', form=form)

@devices.route('/employee/<int:id>/toggle-status', methods=['POST'])
def employee_toggle_status(id):
    """Toggle employee's active/inactive status."""
    try:
        user = User.query.get_or_404(id)
        user.state = 'inactive' if user.state == 'active' else 'active'
        db.session.commit()
        flash(f'Employee status updated to {user.state}', 'success')
    except Exception as e:
        current_app.logger.error(f"Error updating employee status: {str(e)}")
        flash('Error updating employee status', 'error')
        db.session.rollback()

    return redirect(url_for('devices.list_devices'))