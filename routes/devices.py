from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from sqlalchemy import and_, text
from sqlalchemy.sql import text as sqlalchemy_text
from models import (
    Phone, DeviceMake, DeviceModel, PhoneStatus,
    User, PhoneAssignment, PhoneSimAssignment,
    DeviceMakeEnum, DeviceModelEnum
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
        
        # Base query for users with ordered results
        users_query = User.query.order_by(User.last_name, User.first_name)

        # Filter active users unless show_inactive is True
        if not show_inactive:
            users_query = users_query.filter(User.state == 'active')

        # Get users with prefetched assignments
        users = users_query.all()
        
        current_app.logger.info(f"Retrieved {len(users)} users (show_inactive={show_inactive})")

        # Calculate device and SIM counts for each user
        for user in users:
            user.phone_count = PhoneAssignment.query.filter(
                PhoneAssignment.user_id == user.id,
                PhoneAssignment.returned_date.is_(None)
            ).count()
            
            user.sim_count = PhoneSimAssignment.query.filter(
                PhoneSimAssignment.user_id == user.id,
                PhoneSimAssignment.returned_date.is_(None)
            ).count()

        # Get all devices
        devices = Phone.query.all()

        # Initialize context panel data
        context_user = users[0] if users else None
        user_devices = []
        device_count = 0
        sim_count = 0

        if context_user:
            # Get active devices for the context user
            user_devices = Phone.query.join(PhoneAssignment).filter(
                and_(
                    PhoneAssignment.user_id == context_user.id,
                    PhoneAssignment.returned_date.is_(None)
                )
            ).all()
            
            device_count = len(user_devices)
            sim_count = PhoneSimAssignment.query.filter(
                and_(
                    PhoneSimAssignment.user_id == context_user.id,
                    PhoneSimAssignment.returned_date.is_(None)
                )
            ).count()

        return render_template('devices/list.html',
                            devices=devices,
                            employees=users,
                            user=context_user,
                            user_devices=user_devices,
                            device_count=device_count,
                            sim_count=sim_count,
                            show_inactive=show_inactive)

    except Exception as e:
        current_app.logger.error(f"Error in list_devices: {str(e)}")
        flash('Error retrieving device list', 'error')
        return render_template('errors/500.html'), 500

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

@devices.route('/inventory')
def inventory_report():
    """Generate device inventory report."""
    try:
        # Get status summary
        status_summary = db.session.query(
            Phone.status,
            db.func.count(Phone.id)
        ).group_by(Phone.status).all()
        status_summary = dict(status_summary)

        # Get device distribution by make/model
        device_distribution = {}
        phones = Phone.query.all()
        for phone in phones:
            make = phone.make.text
            model = phone.model.text
            
            if make not in device_distribution:
                device_distribution[make] = {}
            
            if model not in device_distribution[make]:
                device_distribution[make][model] = {
                    'total': 0,
                    'instock': 0,
                    'issued': 0
                }
            
            device_distribution[make][model]['total'] += 1
            if phone.status == PhoneStatus.INSTOCK.value:
                device_distribution[make][model]['instock'] += 1
            elif phone.status == PhoneStatus.ISSUED.value:
                device_distribution[make][model]['issued'] += 1

        # Get recent assignments
        recent_assignments = PhoneAssignment.query\
            .order_by(PhoneAssignment.assigned_date.desc())\
            .limit(10)\
            .all()

        return render_template('devices/inventory.html',
                            status_summary=status_summary,
                            device_distribution=device_distribution,
                            recent_assignments=recent_assignments)

    except Exception as e:
        current_app.logger.error(f"Error generating inventory report: {str(e)}")
        flash('Error generating inventory report', 'error')
        return render_template('errors/500.html'), 500

@devices.route('/employee/<int:id>/details')
def employee_details(id):
    """Get employee details for context panel."""
    try:
        user = User.query.get_or_404(id)
        
        # Count active devices and SIM cards
        device_count = PhoneAssignment.query.filter(
            PhoneAssignment.user_id == id,
            PhoneAssignment.returned_date.is_(None)
        ).count()
        
        sim_count = PhoneSimAssignment.query.filter(
            PhoneSimAssignment.user_id == id,
            PhoneSimAssignment.returned_date.is_(None)
        ).count()
        
        return jsonify({
            'first_name': user.first_name,
            'last_name': user.last_name,
            'position': user.position,
            'device_count': device_count,
            'sim_count': sim_count
        })
    except Exception as e:
        current_app.logger.error(f"Error fetching employee details: {str(e)}")
        return jsonify({'error': 'Failed to fetch employee details'}), 500

@devices.route('/employee/<int:id>/toggle-status', methods=['POST'])
def employee_toggle_status(id):
    """Toggle employee's active/inactive status."""
    try:
        user = User.query.get_or_404(id)
        # Toggle between active and inactive states
        user.state = 'inactive' if user.state == 'active' else 'active'
        db.session.commit()
        
        # Get the current show_inactive parameter from the request
        show_inactive = request.args.get('show_inactive', '0')
        
        flash(f'Employee status updated to {user.state}', 'success')
        current_app.logger.info(f"Employee {user.employee_id} status updated to {user.state}")
        
        # Redirect back to the list view with the same filter state
        return redirect(url_for('devices.list_devices', show_inactive=show_inactive))
    except Exception as e:
        current_app.logger.error(f"Error updating employee status: {str(e)}")
        flash('Error updating employee status', 'error')
        db.session.rollback()
        return redirect(url_for('devices.list_devices'))