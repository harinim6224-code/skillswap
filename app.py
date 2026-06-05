from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "secret123"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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

@app.route('/')
def splash():
    return render_template("splash.html")

@app.route('/loginpage')
def loginpage():
    return render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']

        user = User(
            name=name,
            email=email,
            phone=phone,
            password=password
        )

        db.session.add(user)
        db.session.commit()

        return redirect('/loginpage')

    return render_template("register.html")

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
  

    user = User.query.filter_by(
        email=email,
        password=password
    ).first()

    if user:
        session['user_id'] = user.id
        return redirect('/dashboard')

    return "Invalid Login Credentials"

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect('/loginpage')

    if request.method == 'POST':
        have = request.form['have']
        want = request.form['want']

        skill = Skills(
            user_id=session['user_id'],
            skills_have=have,
            skills_want=want
        )

        db.session.add(skill)
        db.session.commit()

    return render_template("dashboard.html")

@app.route('/matches')
def matches():
    if 'user_id' not in session:
        return redirect('/loginpage')

    current_user = session['user_id']

    my_skill = Skills.query.filter_by(user_id=current_user).all()
    all_users = Skills.query.filter(
    Skills.user_id != current_user
).all()

    if not my_skill:
        return "Please add skills first!"

    all_users = Skills.query.filter(
        Skills.user_id != current_user
    ).all()

    results = []

for my_skill in my_skills:
    all_users = Skills.query.filter(Skills.user_id != current_user).all()

    for other in all_users:
        if (
            my_skill.skills_want.strip().lower() == other.skills_have.strip().lower()
            and
            my_skill.skills_have.strip().lower() == other.skills_want.strip().lower()
        ):
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

@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == 'POST':
        email = request.form['email']
        new_password = request.form['new_password']

        user = User.query.filter_by(email=email).first()

        if user:
            user.password = new_password
            db.session.commit()
            return "Password Reset Successful!"

        return "Email Not Found!"

    return render_template("forgot.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/loginpage')

if __name__ == "__main__":
    with app.app_context():
    
        db.create_all()

    app.run(debug=True)