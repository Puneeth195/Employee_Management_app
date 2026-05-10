from flask import Flask, render_template, request, redirect, session
from db_config import get_connection
import re

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- LOGIN ----------------
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (username, password)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user'] = username
            return redirect('/dashboard')
        else:
            return "Invalid Credentials"

    return render_template('login.html')


# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')

    search = request.args.get('search')

    conn = get_connection()
    cursor = conn.cursor()

    if search:
        cursor.execute(
            "SELECT * FROM employee WHERE name LIKE %s",
            ('%' + search + '%',)
        )
    else:
        cursor.execute("SELECT * FROM employee")

    employees = cursor.fetchall()
    conn.close()

    return render_template('dashboard.html', employees=employees)


# ---------------- ADD ----------------
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        emp_code = request.form['employee_code']
        salary = request.form['salary']
        join_date = request.form['join_date']

        # ✅ EMPTY VALIDATION
        if not all([name, email, phone, emp_code, salary, join_date]):
            return "All fields are required!"

        # ✅ EMAIL VALIDATION
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_pattern, email):
            return "Invalid Email Format!"

        # ✅ PHONE VALIDATION (10 digits)
        if not re.match(r'^[0-9]{10}$', phone):
            return "Phone must be 10 digits!"

        conn = get_connection()
        cursor = conn.cursor()

        # ✅ UNIQUE EMPLOYEE CODE CHECK
        cursor.execute("SELECT * FROM employee WHERE employee_code=%s", (emp_code,))
        if cursor.fetchone():
            conn.close()
            return "Employee Code already exists!"

        # ✅ INSERT (FIXED ORDER)
        cursor.execute("""
            INSERT INTO employee (name, email, phone, employee_code, salary, join_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, email, phone, emp_code, salary, join_date))

        conn.commit()
        conn.close()

        return redirect('/dashboard')

    return render_template('add.html')


# ---------------- DELETE ----------------
@app.route('/delete/<int:id>')
def delete(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM employee WHERE id=%s", (id,))
    conn.commit()
    conn.close()

    return redirect('/dashboard')


# ---------------- EDIT ----------------
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        cursor.execute("""
            UPDATE employee SET 
                name=%s,
                email=%s,
                phone=%s,
                employee_code=%s,
                salary=%s,
                join_date=%s
            WHERE id=%s
        """, (
            request.form['name'],
            request.form['email'],
            request.form['phone'],
            request.form['employee_code'],
            request.form['salary'],
            request.form['join_date'],
            id
        ))

        conn.commit()
        conn.close()
        return redirect('/dashboard')

    # GET request
    cursor.execute("SELECT * FROM employee WHERE id=%s", (id,))
    emp = cursor.fetchone()
    conn.close()

    return render_template('edit.html', emp=emp)


# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)