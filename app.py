from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "secret123"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------------- MODELS ---------------- #

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(10))
    password = db.Column(db.String(100))


class Skills(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    skills_have = db.Column(db.String(100))
    skills_want = db.Column(db.String(100))


# ---------------- ROUTES ---------------- #

@app.route('/')
def splash():
    return render_template("splash.html")


@app.route('/loginpage')
def loginpage():
    return render_template("login.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = User(
            name=request.form['name'],
            email=request.form['email'],
            phone=request.form['phone'],
            password=request.form['password']
        )

        db.session.add(user)
        db.session.commit()

        return redirect('/loginpage')

    return render_template("register.html")


@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    user = User.query.filter_by(email=email, password=password).first()

    if user:
        session['user_id'] = user.id
        return redirect('/dashboard')

    return "Invalid Login Credentials"


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect('/loginpage')

    if request.method == 'POST':
        skill = Skills(
            user_id=session['user_id'],
            skills_have=request.form['have'],
            skills_want=request.form['want']
        )

        db.session.add(skill)
        db.session.commit()

    return render_template("dashboard.html")


# ---------------- MATCHING LOGIC FIXED ---------------- #

@app.route('/matches')
def matches():
    if 'user_id' not in session:
        return redirect('/loginpage')

    current_user = session['user_id']

    # Get all skills of current user
    my_skills = Skills.query.filter_by(user_id=current_user).all()

    # Get all other users' skills
    all_users = Skills.query.filter(Skills.user_id != current_user).all()

    results = []

    # Convert my skills into a set of tuples for fast matching
    my_pairs = set()

    for s in my_skills:
        have = s.skills_have.strip().lower()
        want = s.skills_want.strip().lower()
        my_pairs.add((have, want))

    # Compare with other users
    for other in all_users:
        other_have = other.skills_have.strip().lower()
        other_want = other.skills_want.strip().lower()

        # EXACT REVERSE MATCH (BEST LOGIC)
        if (other_want, other_have) in my_pairs:

            user_info = User.query.get(other.user_id)

            if user_info:
                results.append({
                    "name": user_info.name,
                    "email": user_info.email,
                    "phone": user_info.phone,
                    "have": other.skills_have,
                    "want": other.skills_want
                })

    return render_template("matches.html", matches=results)

# ---------------- FORGOT PASSWORD ---------------- #

@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()

        if user:
            user.password = request.form['new_password']
            db.session.commit()
            return "Password Reset Successful!"

        return "Email Not Found!"

    return render_template("forgot.html")


# ---------------- LOGOUT ---------------- #

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/loginpage')


# ---------------- RUN APP ---------------- #

if __name__ == "__main__":
    with app.app_context():
        db.create_all()   # ❗ NO drop_all (IMPORTANT FIX)

    app.run(debug=True)