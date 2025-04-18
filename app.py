from flask import Flask, render_template, request, redirect, url_for, send_file
from datetime import datetime, timedelta
import pyodbc
import io
import csv
from database import init_db, get_db_connection

app = Flask(__name__)

init_db()

@app.route('/')
def home():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Expenses ORDER BY date DESC")
    expenses = cursor.fetchall()
    cursor.execute("SELECT name FROM Categories")
    categories = [row.name for row in cursor.fetchall()]
    conn.close()
    return render_template('index.html', expenses=expenses, categories=categories)

@app.route('/add', methods=['POST'])
def add_expense():
    date = request.form['date']
    category = request.form['category']
    amount = float(request.form['amount'])
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Expenses (date, category, amount) VALUES (?, ?, ?)", (date, category, amount))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_expense(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        date = request.form['date']
        category = request.form['category']
        amount = float(request.form['amount'])
        cursor.execute("UPDATE Expenses SET date = ?, category = ?, amount = ? WHERE id = ?", (date, category, amount, id))
        conn.commit()
        conn.close()
        return redirect(url_for('home'))
    cursor.execute("SELECT * FROM Expenses WHERE id = ?", (id,))
    expense = cursor.fetchone()
    cursor.execute("SELECT name FROM Categories")
    categories = [row.name for row in cursor.fetchall()]
    conn.close()
    return render_template('edit_expense.html', expense=expense, categories=categories)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_expense(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Expenses WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

@app.route('/summary/<period>')
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
        WHERE date BETWEEN ? AND ? 
        GROUP BY category
    """, (start_date, end_date))
    summary_data = cursor.fetchall()
    conn.close()
    return render_template('summary.html', summary=summary_data, period=title)

@app.route('/export')
def export():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT date, category, amount FROM Expenses ORDER BY date DESC")
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