from flask import render_template, url_for, flash, redirect, request
from app import app, db
from app.forms import RegistrationForm, LoginForm
from app.models import User, Flashcard, CodingProblem
from app.ai_assistant import AI_Assistant
from flask_login import login_user, current_user, logout_user, login_required

ai_assistant = AI_Assistant()

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', title='Home')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/flashcards", methods=['GET', 'POST'])
def generate_flashcards():
    if request.method == 'POST':
         concepts = request.form.getlist('concepts')
         language = request.form['language']
         flashcards = ai_assistant.generate_flashcards(concepts, language)
         return render_template('flashcards.html', flashcards=flashcards)

    return render_template('generate_flashcards.html')

@app.route("/flashcards")
def flashcards():
    return render_template('flashcards.html', flashcards=[])

