# app/routes.py
# create routes here

from flask import Blueprint, jsonify, request, session
from .models import User, Post, followers
from .extensions import db
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, unset_jwt_cookies
from .decorators import login_required
from flask_cors import cross_origin

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return jsonify(message = "Welcome to the Social Media Feed API!")

# user registration 
@main.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    email = request.json.get('email')
    password = request.json.get('password')

    # check for missing data
    if not username :
        return jsonify({"message": f"Missing {username}"}), 400
    if not email :
        return jsonify({"message": f"Missing {email}"}), 400
    if not password :
        return jsonify({"message": f"Missing {password}"}), 400

    # check if user details exist
    if User.query.filter_by(email=email).first():
        return jsonify({"message": f"Email {email} already exist"})
    
    # if new valid user
    new_user = User(username=username, email=email)
    new_user.set_password(password=password)

    # commit to db
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": f"New user {username} registered successfully"}), 201

# Login user
@main.route('/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')

    user = User.query.filter_by(email=email).first()
    
    # store user ID in session
    session['user_id'] = user.id

    # validate the user
    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid credentials"}), 401

    # create jwt access token
    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token), 200

# protected route
@main.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    return jsonify(message="Protected route successfully accessed"), 200


# logout route
@main.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    response = jsonify({"message": "Logged out successfully"})
    unset_jwt_cookies(response)
    return response, 200

# Follow a user route
@main.route('/follow/<username>', methods=['POST'])
def follow(username):

    # get the user id of logged in user from session
    current_user_id = session.get('user_id')
    if not current_user_id:
        return({"message": "Please Login"})

    current_user = User.query.get(current_user_id)
    user_to_follow = User.query.filter_by(username=username).first()

    if not user_to_follow:
        return jsonify({"message": "User not found"}), 404

    if current_user.is_following(user_to_follow):
        return jsonify({"message": f"You're already following {username}"}), 400

    current_user.follow(user_to_follow)
    db.session.commit()

    return jsonify({"message": f"You're now following {username}"}), 200

# unfollow a user
@main.route('/unfollow/<username>', methods=['POST'])
def unfollow(username):

    # get the logged in user from the session
    current_user_id = session.get('user_id')

    if not current_user_id:
        return jsonify({"message": "You must be logged in to unfollow users"}), 403

    current_user = User.query.get(current_user_id)
    user_to_unfollow = User.query.filter_by(username=username).first()

    if not user_to_unfollow:
        return jsonify({"message": "User not found"}), 404
    
    if not current_user.is_following(user_to_unfollow):
        return jsonify({"message": f"You're not following {username}"}), 404

    current_user.unfollow(user_to_unfollow)
    db.session.commit()

    return jsonify({"message": f"You have unfollowed {username}"}), 200

# see all the followers
@main.route('/followers', methods=['GET'])
def view_followers():
    # get logged in user details
    current_user_id = session.get('user_id')
    if not current_user_id:
        return jsonify({"message": "You must login first"}), 403
    
    current_user = User.query.get(current_user_id)

    #Fetch all the users
    followers = current_user.followers.all()
    follower_list = [{"id": follower.id, "username": follower.username} for follower in followers] 

    return jsonify({"followers": follower_list}), 200

# see all the unfollowers
@main.route('/following', methods=['GET'])
def view_following():
    # Get the logged-in user from session
    current_user_id = session.get('user_id')
    if not current_user_id:
        return jsonify({"message": "You must be logged in to view followed users"}), 403

    current_user = User.query.get(current_user_id)

    # Fetch all followed users
    followed_users = current_user.followed.all()
    following_list = [{"id": followed.id, "username": followed.username} for followed in followed_users]

    return jsonify({"following": following_list}), 200

# post 
from .models import Post

@main.route('/post', methods=['POST'])
@login_required
def create_post():
    current_user_id = session.get('user_id')
    
    if not current_user_id:
        return jsonify({"message": "You must be logged in to post"}), 403

    data = request.json
    content = data.get('content')

    if not content or len(content) > 280:
        return jsonify({"message": "Post content must be between 1 and 280 characters"}), 400

    # Create a new post
    post = Post(content=content, author_id=current_user_id)
    db.session.add(post)
    db.session.commit()

    return jsonify({"message": "Post created successfully"}), 201

# fetch posts for the user
@main.route('/my_posts', methods=['GET'])
@login_required
def get_my_posts():
    current_user_id = session.get('user_id')

    if not current_user_id:
        return jsonify({"message": "You must be logged in to view your posts"}), 403

    # Query the Post model instead of accessing user.posts
    posts = Post.query.filter_by(author_id=current_user_id).order_by(Post.timestamp.desc()).all()

    posts_data = [{"id": post.id, "content": post.content, "timestamp": post.timestamp} for post in posts]

    return jsonify(posts_data), 200

# viewing follower posts
@main.route('/feed', methods=['GET'])
@login_required
def get_feed():
    current_user_id = session.get('user_id')

    if not current_user_id:
        return jsonify({"message": "You must be logged in to view the feed"}), 403

    # Get the logged-in user
    current_user = User.query.get(current_user_id)

    # Get all the posts from the users the current user is following
    followed_posts = Post.query.join(followers, (followers.c.followed_id == Post.author_id)) \
                               .filter(followers.c.follower_id == current_user_id) \
                               .order_by(Post.timestamp.desc()).all()

    # Include the current user's own posts in the feed
    user_posts = Post.query.filter_by(author_id=current_user_id).order_by(Post.timestamp.desc()).all()

    # Combine and sort both the followed users' posts and the user's own posts
    all_posts = followed_posts + user_posts
    all_posts.sort(key=lambda x: x.timestamp, reverse=True)  # Sort by timestamp

    # Convert posts to JSON
    posts_data = [{"author": post.author.username, "content": post.content, "timestamp": post.timestamp} for post in all_posts]

    return jsonify(posts_data), 200

