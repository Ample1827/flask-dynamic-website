# Main Flask application file
from flask import Flask, render_template
import mysql.connector

app = Flask(__name__)

@app.route("/")
def index():
    # Connect to the MySQL database
    db = mysql.connector.connect(
        host="localhost",
        user="root",          # Update if your MySQL username is different
        password="",          # Update if your MySQL password is set
        database="mywebsite_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT name, email FROM users")
    users = cursor.fetchall()
    cursor.close()
    db.close()

    # Render the template with the data
    return render_template("index.html", title="My Dynamic Website", users=users)

if __name__ == "__main__":
    app.run(debug=True)
