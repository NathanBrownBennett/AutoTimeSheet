from flask import Blueprint, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models import db, Task

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/load_tasks', methods=['GET'])
@login_required
def tasks():
    Tasks = Task.query.filter_by(user_id=current_user.id).all()
    return Tasks

@tasks_bp.route('/create_task', methods=['POST'])
@login_required
def create_task():
    task_description = request.form.get('task_description')
    task = Task(description=task_description, user_id=current_user.id, status='to-do')
    db.session.add(task)
    db.session.commit()
    flash('Task created successfully.', 'success')
    return redirect(url_for('main.index'))

@tasks_bp.route('/delete_task/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if current_user.id == task.user_id or current_user.is_admin:
        db.session.delete(task)
        db.session.commit()
        flash('Task deleted successfully.', 'success')
    else:
        flash('You do not have permission to delete this task.', 'danger')
    return redirect(url_for('main.index'))

@tasks_bp.route('/update_task/<int:task_id>', methods=['POST'])
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    if request.form.get('status'):
        task.status = request.form.get('status')
    db.session.commit()
    flash('Task updated successfully.', 'success')
    return redirect(url_for('main.index'))

@tasks_bp.route('/get_tasks', methods=['GET'])
@login_required
def get_tasks():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return jsonify([task.to_dict() for task in tasks])

@tasks_bp.route('/move_task/<int:task_id>', methods=['POST'])
@login_required
def move_task(task_id):
    task = Task.query.get_or_404(task_id)
    new_status = request.form.get('status')
    if new_status in ['to-do', 'in-progress', 'completed']:
        task.status = new_status
        db.session.commit()
        flash('Task moved successfully.', 'success')
    else:
        flash('Invalid status.', 'danger')
    return redirect(url_for('main.index'))
