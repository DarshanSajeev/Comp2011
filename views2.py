import logging
from flask import Flask, render_template, redirect, request, url_for, flash, session, jsonify
from datetime import datetime
from app import app, db
from app.models import User, Post, Follow, Like
from werkzeug.security import generate_password_hash, check_password_hash

def calculate_age(birthdate):
    today = datetime.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['username'] = username  # Store username in session
            flash('Login successful!', 'success')   
            return redirect(url_for('home'))
        else:
            flash('Login failed. Check your username and/or password.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        age = datetime.strptime(request.form['age'], '%Y-%m-%d')  # Ensure this is parsed as a datetime object
        email = request.form['email']
        if not username or not password or not age or not email:
            flash('All fields are required.', 'danger')
            return redirect(url_for('register'))
        
        # Check if the username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different username.', 'danger')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password, age=age, email=email)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)  # Remove username from session
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/home')
def home():
    if 'username' not in session:
        flash('You need to be logged in to view this page.', 'danger')
        return redirect(url_for('login'))

    current_user = User.query.filter_by(username=session['username']).first()
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('home.html', posts=posts, current_user=current_user)

@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    if 'username' not in session:
        flash('You need to be logged in to create a post.', 'danger')
        return redirect(url_for('login'))

    current_user = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        if not title or not content:
            flash('Title and content are required.', 'danger')
            return redirect(url_for('create_post'))
        new_post = Post(title=title, content=content, date_posted=datetime.utcnow(), username=current_user.username)
        db.session.add(new_post)
        db.session.commit()
        flash('Post created successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', current_user=current_user)

@app.route('/profile')
def profile():
    if 'username' not in session:
        flash('You need to be logged in to view this page.', 'danger')
        return redirect(url_for('login'))

    current_user = User.query.filter_by(username=session['username']).first()
    follower_count = current_user.followers.count() if current_user else 0
    return render_template('profile.html', user=current_user, follower_count=follower_count)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if 'username' not in session:
        flash('You need to be logged in to search for users.', 'danger')
        return redirect(url_for('login'))
    
    current_user = User.query.filter_by(username=session['username']).first()
    
    if request.method == 'POST':
        search_query = request.form['search_query']
        results = User.query.filter(User.username.contains(search_query)).all()
        return render_template('search_results.html', results=results, query=search_query, current_user=current_user)
    
    return render_template('search.html', current_user=current_user)


@app.route('/follow/<username>', methods=['POST'])
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User not found.', 'danger')
        return redirect(url_for('search'))

    current_user = User.query.filter_by(username=session['username']).first()
    if current_user is None:
        flash('You need to be logged in to follow users.', 'danger')
        return redirect(url_for('login'))

    if current_user.username == user.username:
        flash('You cannot follow yourself.', 'danger')
        return redirect(url_for('search'))

    if current_user.is_following(user):
        flash(f'You are already following {user.username}.', 'info')
        return redirect(url_for('search'))

    follow = Follow(follower_id=current_user.username, followed_id=user.username)
    db.session.add(follow)
    db.session.commit()
    flash(f'You are now following {user.username}!', 'success')
    return redirect(url_for('search'))

@app.route('/unfollow/<username>', methods=['POST'])
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User not found.', 'danger')
        return redirect(url_for('search'))

    current_user = User.query.filter_by(username=session['username']).first()
    if current_user is None:
        flash('You need to be logged in to unfollow users.', 'danger')
        return redirect(url_for('login'))

    follow = Follow.query.filter_by(follower_id=current_user.username, followed_id=user.username).first()
    if follow:
        db.session.delete(follow)
        db.session.commit()
        flash(f'You have unfollowed {user.username}', 'success')
        return redirect(url_for('search'))
    return jsonify({'status': 'error', 'message': 'You are not following this user'}), 400

@app.route('/test')
def test():
    return render_template('test_ajax.html')

@app.route('/like', methods=['POST'])
def like_post():
    if 'username' not in session:
        return jsonify(status='error', message='You must be logged in to like posts'), 403

    data = request.get_json()
    post_id = data['post_id']
    post = Post.query.get(post_id)

    if post:
        # Check if the current user is the post creator
        current_user = session['username']
        if post.username == current_user:
            return jsonify(status='error', message='You cannot like your own post'), 403

        # Check if the user has already liked the post
        existing_like = Like.query.filter_by(user_id=current_user, post_id=post_id).first()
        if not existing_like:
            # Create a new Like entry
            new_like = Like(user_id=current_user, post_id=post_id)
            db.session.add(new_like)
            post.likes += 1
            db.session.commit()
            return jsonify(status='success', likes=post.likes)
        else:
            return jsonify(status='error', message='Post already liked', likes=post.likes), 400
    return jsonify(status='error', message='Post not found'), 404
