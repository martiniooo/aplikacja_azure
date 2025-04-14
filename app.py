from flask import Flask, render_template, request, redirect, url_for, send_file
from datetime import datetime, timedelta
import pyodbc
import io
import csv
from database import init_db, get_db_connection

app = Flask(__name__)

# Inicjalizacja bazy danych
init_db()

@app.route('/')
def home():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Expenses ORDER BY date DESC")
    expenses = cursor.fetchall()
    cursor.execute("SELECT * FROM Categories")
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

@app.route('/summary/<period>')
def summary(period):
    conn = get_db_connection()
    cursor = conn.cursor()
    today = datetime.today()
    if period == 'weekly':
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
    else:  # monthly
        start_date = today.replace(day=1)
        end_date = (today.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    
    cursor.execute("""
        SELECT category, SUM(amount) as total 
        FROM Expenses 
        WHERE date BETWEEN ? AND ? 
        GROUP BY category
    """, (start_date, end_date))
    summary_data = cursor.fetchall()
    conn.close()
    return render_template('summary.html', summary=summary_data, period=period)

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