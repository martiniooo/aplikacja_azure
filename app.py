from flask import Flask, render_template, request, redirect, url_for, send_file, session, flash
from datetime import datetime, timedelta
import pyodbc
import io
import csv
from database import init_db, get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'super_secret_key_123' 

init_db()

def login_required(f):
    def wrap(*args, **kwargs):
        if 'user_id' not in session:
            flash('Proszę się zalogować, aby uzyskać dostęp.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

@app.route('/')
@login_required
def home():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Expenses WHERE user_id = ? ORDER BY date DESC", (session['user_id'],))
    expenses = cursor.fetchall()
    cursor.execute("SELECT name FROM Categories")
    categories = [row.name for row in cursor.fetchall()]
    conn.close()
    return render_template('index.html', expenses=expenses, categories=categories, username=session['username'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        if user and password == user.password:
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Zalogowano pomyślnie!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Nieprawidłowa nazwa użytkownika lub hasło.', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO Users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            flash('Rejestracja zakończona sukcesem! Proszę się zalogować.', 'success')
            return redirect(url_for('login'))
        except pyodbc.IntegrityError:
            flash('Nazwa użytkownika już istnieje.', 'error')
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('Wylogowano pomyślnie.', 'success')
    return redirect(url_for('login'))

@app.route('/add', methods=['POST'])
@login_required
def add_expense():
    date = request.form['date']
    category = request.form['category']
    amount = float(request.form['amount'])
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Expenses (date, category, amount, user_id) VALUES (?, ?, ?, ?)", (date, category, amount, user_id))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_expense(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        date = request.form['date']
        category = request.form['category']
        amount = float(request.form['amount'])
        cursor.execute("UPDATE Expenses SET date = ?, category = ?, amount = ? WHERE id = ? AND user_id = ?", (date, category, amount, id, session['user_id']))
        conn.commit()
        conn.close()
        return redirect(url_for('home'))
    cursor.execute("SELECT * FROM Expenses WHERE id = ? AND user_id = ?", (id, session['user_id']))
    expense = cursor.fetchone()
    if expense is None:
        conn.close()
        return redirect(url_for('home'))
    cursor.execute("SELECT name FROM Categories")
    categories = [row.name for row in cursor.fetchall()]
    conn.close()
    return render_template('edit_expense.html', expense=expense, categories=categories, username=session['username'])

@app.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_expense(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Expenses WHERE id = ? AND user_id = ?", (id, session['user_id']))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

@app.route('/summary/<period>')
@login_required
def summary(period):
    conn = get_db_connection()
    cursor = conn.cursor()
    today = datetime.today()
    if period == 'weekly':
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
        title = 'tygodniowe'
    else:  
        start_date = today.replace(day=1)
        end_date = (today.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        title = 'miesięczne'
    
    cursor.execute("""
        SELECT category, SUM(amount) as total 
        FROM Expenses 
        WHERE date BETWEEN ? AND ? AND user_id = ?
        GROUP BY category
    """, (start_date, end_date, session['user_id']))
    summary_data = cursor.fetchall()
    conn.close()
    return render_template('summary.html', summary=summary_data, period=title, username=session['username'])

@app.route('/export')
@login_required
def export():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT date, category, amount FROM Expenses WHERE user_id = ? ORDER BY date DESC", (session['user_id'],))
    expenses = cursor.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Category', 'Amount'])
    for expense in expenses:
        writer.writerow([expense.date, expense.category, expense.amount])
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='expenses_export.csv'
    )

if __name__ == '__main__':
    app.run(debug=True)