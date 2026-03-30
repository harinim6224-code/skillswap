from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret123"

# DB Connection
def get_db():
    return sqlite3.connect("database.db")

# Create Tables
def create_tables():
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS skills (
        user_id INTEGER,
        skills_have TEXT,
        skills_want TEXT
    )''')

    conn.commit()
    conn.close()

create_tables()

# Home -> Login
@app.route('/')
def home():
    return render_template("login.html")

# Register
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        conn = get_db()
        cur = conn.cursor()

        try:
            cur.execute("INSERT INTO users(name,email,password) VALUES (?,?,?)",
                        (name,email,password))
            conn.commit()
        except:
            return "Email already exists"

        return redirect('/')
    
    return render_template("register.html")

# Login
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    conn = get_db()
    cur = conn.cursor()

    user = cur.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()

    if user and check_password_hash(user[3], password):
        session['user_id'] = user[0]
        return redirect('/dashboard')
    else:
        return "Invalid credentials"

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')
    return render_template("dashboard.html")

# Add Skills
@app.route('/add_skill', methods=['GET','POST'])
def add_skill():
    if request.method == 'POST':
        have = request.form['have']
        want = request.form['want']

        conn = get_db()
        cur = conn.cursor()

        cur.execute("INSERT INTO skills VALUES (?,?,?)",
                    (session['user_id'], have, want))
        conn.commit()

        return redirect('/dashboard')

    return render_template("add_skill.html")

# Match Logic
@app.route('/matches')
def matches():
    conn = get_db()
    cur = conn.cursor()

    current = cur.execute("SELECT * FROM skills WHERE user_id=?",
                          (session['user_id'],)).fetchone()

    matches = cur.execute("""
        SELECT users.name, skills.skills_have, skills.skills_want
        FROM skills
        JOIN users ON users.id = skills.user_id
        WHERE skills.skills_have = ?
        AND skills.skills_want = ?
        AND skills.user_id != ?
    """, (current[2], current[1], session['user_id'])).fetchall()

    return render_template("matches.html", matches=matches)

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)