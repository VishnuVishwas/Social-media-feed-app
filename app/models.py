#app/models.py

from .extensions import db
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timezone

# Create a followers association table
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    # Relationships for followers
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0


# post model
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(280), nullable=False)  # Limiting post length to 280 characters
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now(timezone.utc))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Relationship to the user who made the post
    author = db.relationship('User', backref='posts')

    def __repr__(self):
        return f"<Post {self.content}>"

