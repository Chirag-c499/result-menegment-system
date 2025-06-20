from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from models import *
from utils import hash_password, check_password, login_required, get_current_user
import os
from uuid import uuid4
from datetime import date

app = Flask(__name__)
app.secret_key = "super-secret"
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
@login_required
def home():
    user = get_current_user()
    subjects = Subject.select()
    results = Result.select().where(Result.student == user)
    all_users = User.select().where(User.user_type == "student") if user.user_type == "admin" else []
    return render_template("dashboard.html", user=user, subjects=subjects, results=results, all_users=all_users)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        roll_no = request.form['roll_no']
        password = hash_password(request.form['password'])
        user_type = request.form.get('user_type', 'student')
        image = request.files['image']
        filename = ""

        if image:
            ext = os.path.splitext(image.filename)[1]
            filename = f"{uuid4().hex}{ext}"
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        try:
            User.create(
                name=name,
                email=email,
                roll_no=roll_no,
                password=password,
                image=filename,
                user_type=user_type
            )
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('login')) 
        except:
            flash("Email or Roll number already exists.", "danger")

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = User.get(User.email == email)
            if check_password(password, user.password):
                session['user_id'] = user.id
                flash("Logged in successfully!", "success")
                return redirect(url_for('admin_dashboard' if user.user_type == 'admin' else 'home'))
            else:
                flash("Incorrect password.", "danger")
        except:
            flash("User not found.", "danger")
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for('login'))

@app.route("/add_subject", methods=["GET", "POST"])
@login_required
def add_subject():
    user = get_current_user()
    if user.user_type != "admin":
        flash("Access Denied", "danger")
        return redirect(url_for("home"))

    if request.method == "POST":
        sub_code = request.form.get("sub_code").strip()
        sub_name = request.form.get("sub_name").strip()

        if sub_code and sub_name:
            if Subject.select().where(Subject.sub_code == sub_code).exists():
                flash("Subject code already exists.", "danger")
            else:
                Subject.create(sub_code=sub_code, sub_name=sub_name)
                flash("Subject added successfully.", "success")
            return redirect(url_for("add_subject"))

        flash("All fields are required.", "danger")

    subjects = Subject.select()
    return render_template("add_subject.html", user=user, subjects=subjects)

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    user = get_current_user()
    if user.user_type != 'admin':
        flash("Access denied", "danger")
        return redirect(url_for('home'))

    users = User.select().where(User.user_type == 'student')
    subjects = Subject.select()
    results = Result.select()

    return render_template("admin_dashboard.html", user=user, users=users, subjects=subjects, results=results)

@app.route('/update_profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    user = get_current_user()
    if request.method == 'POST':
        user.name = request.form['name']
        user.roll_no = request.form['roll_no']
        image = request.files.get('image')
        if image:
            ext = os.path.splitext(image.filename)[1]
            filename = f"{uuid4().hex}{ext}"
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            user.image = filename
        user.save()
        flash("Profile updated successfully.", "success")
        return redirect(url_for('home'))
    return render_template('update_profile.html', user=user)

@app.route('/delete_profile')
@login_required
def delete_profile():
    user = get_current_user()
    user.delete_instance(recursive=True)
    session.clear()
    flash("Profile deleted.", "warning")
    return redirect(url_for('signup'))

@app.route("/declare_result", methods=["GET", "POST"])
@login_required
def declare_result():
    user = get_current_user()
    if user.user_type != "admin":
        flash("Access denied", "danger")
        return redirect(url_for("home"))

    users = User.select().where(User.user_type == "student")
    subjects = Subject.select()

    if request.method == "POST":
        student_id = request.form.get("student_id")
        result = Result.create(student=student_id, declaration_date=date.today())  # required field!

        for subject in subjects:
            marks = request.form.get(f"marks_{subject.id}")
            total = request.form.get(f"total_{subject.id}")
            if marks and total:
                ResultItem.create(
                    result=result,
                    subject=subject,
                    marks_obtained=marks,
                    total_marks=total
                )

        flash("Result declared successfully!", "success")
        return redirect(url_for("admin_dashboard"))  # 👈 This ensures redirection to admin dashboard

    return render_template("declare_result.html", user=user, all_users=users, subjects=subjects)



if __name__ == '__main__':
    app.run(debug=True)
