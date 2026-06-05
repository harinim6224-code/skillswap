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
    user = User.query.filter_by(
        email=request.form['email'],
        password=request.form['password']
    ).first()

    if user:
        session['user_id'] = user.id
        return redirect('/dashboard')

    return "Invalid Login"


# ---------------- DASHBOARD (FIXED SAFE VERSION) ---------------- #

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect('/loginpage')

    if request.method == 'POST':
        have = request.form.get('have', '').strip().lower()
        want = request.form.get('want', '').strip().lower()

        if have and want:
            skill = Skills(
                user_id=session['user_id'],
                skills_have=have,
                skills_want=want
            )

            db.session.add(skill)
            db.session.commit()

            print("SKILL SAVED ✔")

        else:
            print("EMPTY INPUT ❌")

    return render_template("dashboard.html")


# ---------------- MATCHING (FIXED LOGIC) ---------------- #

@app.route('/matches')
def matches():
    if 'user_id' not in session:
        return redirect('/loginpage')

    current_user = session['user_id']

    def norm(text):
        return text.strip().lower()

    my_skills = Skills.query.filter_by(user_id=current_user).all()
    all_users = Skills.query.filter(Skills.user_id != current_user).all()

    if not my_skills:
        return "Please add skills first!"

    results = []

    my_pairs = set(
        (norm(s.skills_have), norm(s.skills_want))
        for s in my_skills
    )

    for other in all_users:
        other_pair = (norm(other.skills_have), norm(other.skills_want))

        if (other_pair[1], other_pair[0]) in my_pairs:
            user = User.query.get(other.user_id)

            if user:
                results.append({
                    "name": user.name,
                    "email": user.email,
                    "phone": user.phone,
                    "have": other.skills_have,
                    "want": other.skills_want
                })

    return render_template("matches.html", matches=results)


# ---------------- DEBUG CHECK ---------------- #

@app.route('/check')
def check():
    data = Skills.query.all()

    return {
        "total_skills": len(data),
        "data": [
            {
                "user_id": s.user_id,
                "have": s.skills_have,
                "want": s.skills_want
            } for s in data
        ]
    }


# ---------------- RUN APP ---------------- #

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)