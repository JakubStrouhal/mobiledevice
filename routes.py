from flask import render_template, request, jsonify, redirect, url_for
from app import app, db
from models import Device, User, DeviceAssignment, DeviceMake, DeviceModel
from forms import DeviceForm, AssignmentForm
from datetime import datetime

@app.route('/')
def index():
    return redirect(url_for('device_list'))

@app.route('/devices')
def device_list():
    devices = Device.query.all()
    return render_template('devices/list.html', devices=devices)

@app.route('/devices/models/<make>')
def device_models(make):
    make_obj = DeviceMake.query.filter_by(name=make).first_or_404()
    models = DeviceModel.query.filter_by(make_id=make_obj.id).all()
    return jsonify([{'id': model.id, 'name': model.name} for model in models])

@app.route('/devices/<int:id>')
def device_detail(id):
    device = Device.query.get_or_404(id)
    return render_template('devices/detail.html', device=device)

@app.route('/devices/<int:id>/edit', methods=['GET', 'POST'])
def device_edit(id):
    device = Device.query.get_or_404(id)
    form = DeviceForm(obj=device)
    
    if form.validate_on_submit():
        make = DeviceMake.query.filter_by(name=form.make.data).first()
        model = DeviceModel.query.filter_by(name=form.model.data, make_id=make.id).first()
        
        device.make_id = make.id
        device.model_id = model.id
        device.device_type = form.device_type.data
        device.serial_number = form.serial_number.data
        device.cost = form.cost.data
        device.currency = form.currency.data
        device.date_of_purchase = form.date_of_purchase.data
        device.in_operation_from = form.in_operation_from.data
        device.note = form.note.data
        
        db.session.commit()
        return redirect(url_for('device_detail', id=device.id))
        
    return render_template('devices/edit.html', form=form, device=device)

@app.route('/devices/<int:id>/assign', methods=['GET', 'POST'])
def device_assign(id):
    device = Device.query.get_or_404(id)
    form = AssignmentForm()
    
    if form.validate_on_submit():
        assignment = DeviceAssignment(
            device_id=device.id,
            user_id=request.form.get('user_id'),
            released_date=datetime.now().date(),
            note=form.note.data
        )
        db.session.add(assignment)
        db.session.commit()
        return redirect(url_for('device_detail', id=device.id))
        
    users = User.query.filter_by(status='active').all()
    return render_template('devices/assign.html', form=form, device=device, users=users)

@app.route('/protocols/handover/<int:assignment_id>')
def handover_protocol(assignment_id):
    assignment = DeviceAssignment.query.get_or_404(assignment_id)
    return render_template('protocols/handover.html', assignment=assignment)
