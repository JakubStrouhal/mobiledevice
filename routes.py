from flask import render_template, request, jsonify, redirect, url_for
from app import app, db
from models import Phone, User, PhoneAssignment, DeviceMake, DeviceModel
from forms import PhoneForm, AssignmentForm
from datetime import datetime

@app.route('/')
def index():
    return redirect(url_for('device_list'))

@app.route('/devices')
def device_list():
    # Get all assignments with related phone and user information
    assignments = db.session.query(PhoneAssignment)\
        .join(Phone)\
        .join(User)\
        .filter(PhoneAssignment.returned_date.is_(None))\
        .all()
    
    # Process assignments into display format
    devices = []
    for assignment in assignments:
        device = {
            'id': assignment.phone.id,
            'employee_id': assignment.user.employee_id,
            'status': assignment.phone.status,
            'user': assignment.user,
            'phone_count': 1,  # This could be aggregated if needed
            'sim_count': 0,    # This would need to be implemented
            'entry_date': assignment.assigned_date,
            'exit_date': assignment.returned_date
        }
        devices.append(device)
    
    return render_template('devices/list.html', devices=devices)

@app.route('/devices/models/<make>')
def device_models(make):
    make_obj = DeviceMake.query.filter_by(code=make).first_or_404()
    models = DeviceModel.query.filter_by(make_id=make_obj.id).all()
    return jsonify([{'id': model.id, 'code': model.code, 'text': model.text} for model in models])

@app.route('/devices/<int:id>')
def device_detail(id):
    phone = Phone.query.get_or_404(id)
    return render_template('devices/detail.html', device=phone)

@app.route('/devices/<int:id>/edit', methods=['GET', 'POST'])
def device_edit(id):
    phone = Phone.query.get_or_404(id)
    form = PhoneForm(obj=phone)
    
    if form.validate_on_submit():
        make = DeviceMake.query.filter_by(code=form.make.data).first()
        model = DeviceModel.query.filter_by(code=form.model.data, make_id=make.id).first()
        
        phone.make_id = make.id
        phone.model_id = model.id
        phone.serial_number = form.serial_number.data
        phone.buying_price = form.buying_price.data
        phone.note = form.note.data
        
        db.session.commit()
        return redirect(url_for('device_detail', id=phone.id))
        
    return render_template('devices/edit.html', form=form, device=phone)

@app.route('/devices/<int:id>/assign', methods=['GET', 'POST'])
def device_assign(id):
    phone = Phone.query.get_or_404(id)
    form = AssignmentForm()
    
    if form.validate_on_submit():
        assignment = PhoneAssignment(
            phone_id=phone.id,
            user_id=request.form.get('user_id'),
            assigned_date=datetime.now().date(),
            note=form.note.data
        )
        db.session.add(assignment)
        phone.status = 'ISSUED'  # Update phone status when assigned
        db.session.commit()
        return redirect(url_for('device_detail', id=phone.id))
        
    users = User.query.filter_by(state='active').all()
    return render_template('devices/assign.html', form=form, device=phone, users=users)

@app.route('/protocols/handover/<int:assignment_id>')
def handover_protocol(assignment_id):
    assignment = PhoneAssignment.query.get_or_404(assignment_id)
    return render_template('protocols/handover.html', assignment=assignment)
