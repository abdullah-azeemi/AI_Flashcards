from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    flashcards = db.relationship('Flashcard', backref='author', lazy=True)
    correct_answers = db.Column(db.Integer, default=0)
    problems_solved = db.Column(db.Integer, default=0)
    time_complexity_quizzes_correct = db.Column(db.Integer, default=0)

class Flashcard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    concept = db.Column(db.String(100), nullable=False)
    answer = db.Column(db.String(100), nullable=False)
    correct = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    language = db.Column(db.String(50), nullable=False)  

class CodingProblem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    problem_link = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    solved = db.Column(db.Boolean, default=False)

class TimeComplexityQuiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code_snippet = db.Column(db.Text, nullable=False)
    correct_complexity = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_guess = db.Column(db.String(50), nullable=True)
    correct = db.Column(db.Boolean, nullable=True)

class ForumPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    replies = db.relationship('ForumReply', backref='post', lazy=True)

class ForumReply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('forum_post.id'), nullable=False)


