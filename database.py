from flask import Flask, render_template_string
import mysql.connector

app = Flask(__name__)

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
def test_db_connection():
    try:
        connection = get_db_connection()
        connection.close()
        return render_template_string('<h1>Database connection successful!</h1>')
    except mysql.connector.Error as err:
        return render_template_string('<h1>Database connection failed!</h1><p>{{ error }}</p>', error=err)
    



if __name__ == '__main__':
    app.run(debug=True)
