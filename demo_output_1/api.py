from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import db, Project, Task

api_bp = Blueprint('api', __name__)


@api_bp.route('/tasks', methods=['GET'])
@login_required
def get_tasks():
    """Get user's tasks"""
    status = request.args.get('status')
    query = Task.query.filter_by(assigned_to_id=current_user.id)
    
    if status:
        query = query.filter_by(status=status)
    
    tasks = query.all()
    
    return jsonify([{
        'id': t.id,
        'title': t.title,
        'description': t.description,
        'status': t.status,
        'priority': t.priority,
        'created_at': t.created_at.isoformat(),
        'due_date': t.due_date.isoformat() if t.due_date else None
    } for t in tasks])

@api_bp.route('/tasks', methods=['POST'])
@login_required
def create_task():
    """Create new task"""
    data = request.get_json()
    
    task = Task(
        title=data.get('title'),
        description=data.get('description'),
        status=data.get('status', 'pending'),
        priority=data.get('priority', 'medium'),
        assigned_to_id=current_user.id
    )
    
    db.session.add(task)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'task': {
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'status': task.status,
            'priority': task.priority
        }
    }), 201

@api_bp.route('/tasks/<int:id>', methods=['PUT'])
@login_required
def update_task(id):
    """Update task"""
    task = Task.query.filter_by(id=id, assigned_to_id=current_user.id).first_or_404()
    data = request.get_json()
    
    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.status = data.get('status', task.status)
    task.priority = data.get('priority', task.priority)
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Task updated'})


@api_bp.errorhandler(404)
def api_not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@api_bp.errorhandler(400)
def api_bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

@api_bp.errorhandler(500)
def api_internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500
