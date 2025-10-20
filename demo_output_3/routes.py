from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Post, Comment
from forms import PostForm, CommentForm

main_bp = Blueprint('main', __name__)


@main_bp.route('/posts')
def posts():
    """List all blog posts"""
    posts = Post.query.filter_by(published=True).order_by(Post.created_at.desc()).all()
    return render_template('posts.html', posts=posts)

@main_bp.route('/posts/<int:id>')
def post_detail(id):
    """Blog post detail"""
    post = Post.query.get_or_404(id)
    comments = Comment.query.filter_by(post_id=id).all()
    form = CommentForm()
    return render_template('post_detail.html', post=post, comments=comments, form=form)

@main_bp.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    """Create new blog post"""
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            content=form.content.data,
            summary=form.summary.data,
            author_id=current_user.id
        )
        db.session.add(post)
        db.session.commit()
        flash('Post created successfully!', 'success')
        return redirect(url_for('main.posts'))
    
    return render_template('create_post.html', form=form)

