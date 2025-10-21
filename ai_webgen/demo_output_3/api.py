from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import db, Post, Comment

api_bp = Blueprint('api', __name__)


@api_bp.route('/posts', methods=['GET'])
def get_posts():
    """Get all published posts"""
    posts = Post.query.filter_by(published=True).order_by(Post.created_at.desc()).all()
    return jsonify([{
        'id': p.id,
        'title': p.title,
        'content': p.content,
        'summary': p.summary,
        'author': p.author.username,
        'created_at': p.created_at.isoformat()
    } for p in posts])

@api_bp.route('/posts/<int:id>', methods=['GET'])
def get_post(id):
    """Get single post with comments"""
    post = Post.query.get_or_404(id)
    comments = Comment.query.filter_by(post_id=id).all()
    
    return jsonify({
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'summary': post.summary,
        'author': post.author.username,
        'created_at': post.created_at.isoformat(),
        'comments': [{
            'id': c.id,
            'content': c.content,
            'author': c.author.username,
            'created_at': c.created_at.isoformat()
        } for c in comments]
    })

@api_bp.route('/posts/<int:post_id>/comments', methods=['POST'])
@login_required
def add_comment(post_id):
    """Add comment to post"""
    data = request.get_json()
    content = data.get('content')
    
    if not content:
        return jsonify({'error': 'Content is required'}), 400
    
    comment = Comment(
        content=content,
        author_id=current_user.id,
        post_id=post_id
    )
    
    db.session.add(comment)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'comment': {
            'id': comment.id,
            'content': comment.content,
            'author': comment.author.username,
            'created_at': comment.created_at.isoformat()
        }
    })


@api_bp.errorhandler(404)
def api_not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@api_bp.errorhandler(400)
def api_bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

@api_bp.errorhandler(500)
def api_internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500
