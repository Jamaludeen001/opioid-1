from flask import Flask, request, render_template, redirect, url_for
import mysql.connector

app = Flask(__name__)
app.secret_key = 'my_secret_key'

# Database connection function
def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1213",
        database="db1"
    )
    return connection

@app.route('/')
def home():
    return render_template('change_column_type.html')

@app.route('/change_column_type', methods=['POST'])
def change_column_type():
    table_name = request.form['table_name']
    column_name = request.form['column_name']
    new_datatype = request.form['new_datatype']
    
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        alter_table_query = f"ALTER TABLE {table_name} MODIFY COLUMN {column_name} {new_datatype}"
        cursor.execute(alter_table_query)
        connection.commit()
        message = f"Successfully changed the datatype of {column_name} to {new_datatype} in table {table_name}."
    except mysql.connector.Error as err:
        message = f"Error: {err}"
    
    cursor.close()
    connection.close()
    
    return render_template('change_column_type.html', message=message)

if __name__ == '__main__':
    app.run(debug=True)
