import os
import pyodbc

connection_string = os.getenv("DATABASE_URL", "Driver={ODBC Driver 18 for SQL Server};Server=tcp:expenses-server-123.database.windows.net,1433;Database=ExpensesDB;Uid=admn1;Pwd=Serwerazure!;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;")

def init_db():
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Expenses' AND xtype='U')
        CREATE TABLE Expenses (
            id INT IDENTITY(1,1) PRIMARY KEY,
            date DATE NOT NULL,
            category NVARCHAR(50) NOT NULL,
            amount DECIMAL(10, 2) NOT NULL
        )
    """)
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Categories' AND xtype='U')
        CREATE TABLE Categories (
            id INT IDENTITY(1,1) PRIMARY KEY,
            name NVARCHAR(50) NOT NULL UNIQUE
        )
    """)
    categories = ['Jedzenie', 'Rachunki', 'Transport', 'Rozrywka', 'Inne']
    for category in categories:
        cursor.execute("SELECT COUNT(*) FROM Categories WHERE name = ?", category)
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO Categories (name) VALUES (?)", category)
    conn.commit()
    conn.close()

def get_db_connection():
    return pyodbc.connect(connection_string)