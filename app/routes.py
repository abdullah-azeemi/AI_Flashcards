import os
import re
import json
import random
from flask import render_template, url_for, flash, redirect, request
from app import app, db
from dotenv import load_dotenv
from app.forms import RegistrationForm, LoginForm
from app.models import User, Flashcard, CodingProblem, TimeComplexityQuiz, ForumPost, ForumReply
from app.ai_assistant import AI_Assistant
from flask_login import login_user, current_user, logout_user, login_required
import stripe

load_dotenv(dotenv_path="./.env")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

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

# @app.route("/flashcards", methods=['GET', 'POST'])
# def generate_flashcards():
#     if request.method == 'POST':
#          concepts = request.form.getlist('concepts')
#          language = request.form['language']
#          flashcards = ai_assistant.generate_flashcards(concepts, language)
#          return render_template('flashcards.html', flashcards=flashcards)

#     return render_template('generate_flashcards.html')

# @app.route("/flashcards")
# def flashcards():
#     return render_template('flashcards.html', flashcards=[])

@app.route("/generate_flashcards", methods=["GET", "POST"])
@login_required
def generate_flashcards():
    if request.method == "POST":
        concepts = request.form.getlist("concepts")
        language = request.form["language"]
        Flashcard.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        
        flashcards = ai_assistant.generate_flashcards(concepts, language)
        print("Flashcards:", flashcards)

        for concept in concepts:
            for flashcard in flashcards:
                serialized_answer = json.dumps(flashcard, ensure_ascii=False)
                print("Serialized Flashcard:", serialized_answer)

                existing_flashcard = Flashcard.query.filter_by(
                    concept=concept,
                    answer=serialized_answer,
                    user_id=current_user.id
                ).first()
                
                if existing_flashcard:
                    print(f"Flashcard already exists: {existing_flashcard}")
                else:
                    new_flashcard = Flashcard(
                        concept=concept,
                        answer=serialized_answer,
                        user_id=current_user.id,
                        language=language
                    )
                    db.session.add(new_flashcard)

        db.session.commit()
        current_user.increment_correct_answers()  

        flash("Flashcards generated and saved!", "success")
        return redirect(url_for("flashcards"))

    return render_template("generate_flashcards.html")



@app.route("/flashcards")
@login_required
def flashcards():
    user_flashcards = Flashcard.query.filter_by(user_id=current_user.id).order_by(Flashcard.id.desc()).all()
    print("Retrieved Flashcards:", user_flashcards)
    
    for flashcard in user_flashcards:
        try:
            flashcard.answer = json.loads(flashcard.answer)
        except json.JSONDecodeError:
            flashcard.answer = {} 

    return render_template("flashcards.html", flashcards=user_flashcards)



@app.route("/solve_problem")
@login_required
def solve_problem():
    leetcode_problems = [
        "https://leetcode.com/problems/two-sum/",
        "https://leetcode.com/problems/reverse-linked-list/",
        "https://leetcode.com/problems/valid-parentheses/",
        "https://leetcode.com/problems/merge-two-sorted-lists/",
        "https://leetcode.com/problems/binary-tree-inorder-traversal/",
        "https://leetcode.com/problems/maximum-subarray/",
        "https://leetcode.com/problems/container-with-most-water/",
        "https://leetcode.com/problems/longest-common-prefix/",
        "https://leetcode.com/problems/climbing-stairs/",
        "https://leetcode.com/problems/remove-duplicates-from-sorted-array/",
        "https://leetcode.com/problems/search-insert-position/",
        "https://leetcode.com/problems/symmetric-tree/",
        "https://leetcode.com/problems/linked-list-cycle/",
        "https://leetcode.com/problems/minimum-depth-of-binary-tree/",
        "https://leetcode.com/problems/path-sum/",
        "https://leetcode.com/problems/valid-palindrome/",
        "https://leetcode.com/problems/maximum-depth-of-binary-tree/",
        "https://leetcode.com/problems/plus-one/",
        "https://leetcode.com/problems/palindrome-number/",
        "https://leetcode.com/problems/invert-binary-tree/",
        "https://leetcode.com/problems/implement-strstr/",
        "https://leetcode.com/problems/longest-palindromic-substring/",
        "https://leetcode.com/problems/rotate-array/",
        "https://leetcode.com/problems/find-minimum-in-rotated-sorted-array/",
        "https://leetcode.com/problems/subsets/",
        "https://leetcode.com/problems/letter-combinations-of-a-phone-number/",
        "https://leetcode.com/problems/remove-nth-node-from-end-of-list/",
        "https://leetcode.com/problems/generate-parentheses/",
        "https://leetcode.com/problems/kth-largest-element-in-an-array/",
        "https://leetcode.com/problems/group-anagrams/",
    ]
    
    random_problem_link = random.choice(leetcode_problems)
    new_problem = CodingProblem(problem_link=random_problem_link, user_id=current_user.id)
    current_user.increment_problems_solved()
    db.session.add(new_problem)
    db.session.commit()
    return redirect(random_problem_link)

@app.route("/problems")
@login_required
def problems():
    user_problems = CodingProblem.query.filter_by(user_id=current_user.id).all()
    return render_template("problems.html", problems=user_problems)

@app.route("/time_complexity", methods=["GET", "POST"])
@login_required
def time_complexity():
    if request.method == "POST":
        code_snippet = request.form["code_snippet"]
        user_guess = request.form["complexity"]
        correct_complexity = request.form["correct_complexity"]
        correct = (user_guess == correct_complexity)
        print("\n\n\ncode sniper", code_snippet, "user_guess", user_guess, "correct_complexity", correct_complexity, "correct", correct)
        TimeComplexityQuiz.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()

        quiz = TimeComplexityQuiz(
            code_snippet=code_snippet,
            correct_complexity=correct_complexity,
            user_id=current_user.id,
            user_guess=user_guess,
            correct=correct
        )
        db.session.add(quiz)
        db.session.commit()

        if correct:
            print("Correct Guess")
            current_user.increment_time_complexity_quizzes_correct()
            db.session.commit()
            
        flash(f"Your answer has been recorded. The correct complexity was {correct_complexity}.", "success" if correct else "danger")
        return redirect(url_for("time_complexity_results"))
    code_snippet, correct_complexity = ai_assistant.generate_time_complexity_quiz()

    print("code_snippet", code_snippet)
    print("correct_complexity", correct_complexity)
    if not code_snippet:
        flash("Sorry, there was a problem generating the quiz. Please try again later.", "danger")
        return redirect(url_for("dashboard"))

    return render_template("time_complexity.html", code_snippet=code_snippet, correct_complexity=correct_complexity)


@app.route("/time_complexity_results")
@login_required
def time_complexity_results():
    quizzes = TimeComplexityQuiz.query.filter_by(user_id=current_user.id).all()
    return render_template("time_complexity_results.html", quizzes=quizzes)

@app.route("/forum")
@login_required
def forum():
    posts = ForumPost.query.all()
    return render_template("forum.html", posts=posts)

@app.route("/forum/new", methods=["GET", "POST"])
@login_required
def new_post():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        post = ForumPost(title=title, content=content, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        flash("Your post has been created!", "success")
        return redirect(url_for("forum"))
    return render_template("new_post.html")

@app.route("/forum/<int:post_id>", methods=["GET", "POST"])
@login_required
def post(post_id):
    post = ForumPost.query.get_or_404(post_id)
    if request.method == "POST":
        content = request.form["content"]
        reply = ForumReply(content=content, user_id=current_user.id, post_id=post.id)
        db.session.add(reply)
        db.session.commit()
        flash("Your reply has been added!", "success")
        return redirect(url_for("post", post_id=post.id))
    return render_template("post.html", post=post)

@app.route("/checkout", methods=["POST", "GET"])
@login_required
def checkout():
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Premium Membership',
                    },
                    'unit_amount': 1000,  # $10.00
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=url_for('checkout_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('checkout_cancel', _external=True),
        )
        return redirect(session.url, code=303)
    except Exception as e:
        flash("An error occurred: " + str(e), "danger")
        return redirect(url_for('home'))


@app.route("/checkout/success")
@login_required
def checkout_success():
    return render_template("checkout_success.html")

@app.route("/checkout/cancel")
@login_required
def checkout_cancel():
    return render_template("checkout_cancel.html")

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user)


if __name__ == "main":
    print(stripe.api_key)


