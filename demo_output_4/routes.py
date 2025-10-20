from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Project, Task
from forms import TaskForm, ProjectForm

main_bp = Blueprint('main', __name__)


@main_bp.route('/tasks')
@login_required
def tasks():
    """List user tasks"""
    tasks = Task.query.filter_by(assigned_to_id=current_user.id).all()
    return render_template('tasks.html', tasks=tasks)

@main_bp.route('/create_task', methods=['GET', 'POST'])
@login_required
def create_task():
    """Create new task"""
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(
            title=form.title.data,
            description=form.description.data,
            status=form.status.data,
            priority=form.priority.data,
            assigned_to_id=current_user.id
        )
        db.session.add(task)
        db.session.commit()
        flash('Task created successfully!', 'success')
        return redirect(url_for('main.tasks'))
    
    return render_template('create_task.html', form=form)

@main_bp.route('/projects')
@login_required
def projects():
    """List user projects"""
    projects = Project.query.filter_by(owner_id=current_user.id).all()
    return render_template('projects.html', projects=projects)

