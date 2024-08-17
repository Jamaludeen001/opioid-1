from flask import Flask, request, render_template, redirect, url_for
import pandas as pd
import mysql.connector
import os
import numpy as np

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your actual secret key

# Database connection function
def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1213",
        database="db1"  # Change to your database name
    )
    return connection

@app.route('/')
def upload_page():
    return render_template('upload_csv.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        return redirect(request.url)
    
    if file and file.filename.endswith('.csv'):
        df = pd.read_csv(file)
        create_table_from_csv(df)
        insert_into_db(df)
        return 'CSV file has been processed, table created, and data inserted into the database.'
    
    return 'Invalid file format. Please upload a CSV file.'

def create_table_from_csv(df):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # Determine table name
    table_name = 'patients'
    
    # Create table if it does not exist
    cols=df.columns
    df=df.drop(cols[:3],axis=1)
    columns = df.columns
    column_definitions = []
    # Define SQL column types based on data types in CSV
    for col in columns:
        dtype = str(df[col].dtype)
        if dtype == 'object':
            column_definitions.append(f"{col} VARCHAR(255)")
        elif dtype == 'int64':
            column_definitions.append(f"{col} INT")
        elif dtype == 'float64':
            column_definitions.append(f"{col} FLOAT")
        elif dtype == 'bool':
            column_definitions.append(f"{col} BOOLEAN")
        elif dtype =="datetime64[ns]":
            column_definitions.append(f"{col} DATETIME")
        else:
            column_definitions.append(f"{col} TEXT")  # Fallback for other types

    column_definitions_str = ', '.join(column_definitions)
    create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_definitions_str})"
    cursor.execute(create_table_sql)
    
    connection.commit()
    cursor.close()
    connection.close()

def insert_into_db(df):
    connection = get_db_connection()
    cursor = connection.cursor()

    # Assuming the table name is 'patients'
    table_name = 'patients'
    cols=df.columns
    df=df.drop(cols[:3],axis=1)
    
    for index, row in df.iterrows():
        columns = ', '.join(df.columns)
        values = ', '.join(['%s'] * len(row))
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
        cursor.execute(sql, tuple(row))
    
    connection.commit()
    cursor.close()
    connection.close()

if __name__ == '__main__':
    app.run(debug=True)
