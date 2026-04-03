from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "secret123"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# ------------------ MODELS ------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))

class Skills(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    skills_have = db.Column(db.String(100))
    skills_want = db.Column(db.String(100))

# ------------------ ROUTES ------------------

@app.route('/')
def home():
    return render_template("login.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        user = User(name=name, email=email, password=password)
        db.session.add(user)
        db.session.commit()

        return redirect('/')

    return render_template("register.html")


@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    user = User.query.filter_by(email=email, password=password).first()

    if user:
        session['user_id'] = user.id
        return redirect('/dashboard')
    else:
        return "Invalid login!"


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect('/')

    if request.method == 'POST':
        have = request.form['have']
        want = request.form['want']

        skill = Skills(user_id=session['user_id'], skills_have=have, skills_want=want)
        db.session.add(skill)
        db.session.commit()

    return render_template("dashboard.html")


@app.route('/matches')
def matches():
    if 'user_id' not in session:
        return redirect('/')

    current_user = session['user_id']
    user_skills = Skills.query.filter_by(user_id=current_user).first()

    if not user_skills:
        return "Please add skills first!"

    matched_users = Skills.query.filter(
        Skills.skills_have.ilike(f"%{user_skills.skills_want}%"),
        Skills.user_id != current_user
    ).all()

    results = []

    for user in matched_users:
        user_info = User.query.get(user.user_id)

        results.append({
            "name": user_info.name,
            "email": user_info.email,
            "have": user.skills_have,
            "want": user.skills_want
        })

    return render_template("matches.html", matches=results)


@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == 'POST':
        email = request.form['email']
        new_password = request.form['new_password']

        user = User.query.filter_by(email=email).first()

        if user:
            user.password = new_password
            db.session.commit()
            return "Password reset successful!"
        else:
            return "Email not found!"

    return render_template("forgot.html")


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# ------------------ RUN ------------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)