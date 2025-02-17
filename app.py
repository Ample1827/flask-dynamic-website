# Main Flask application file
import logging
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector

from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email

class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    message = TextAreaField("Message", validators=[DataRequired()])
    submit = SubmitField("Submit")

class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Add/Update User")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a secure key
csrf = CSRFProtect(app)

logging.basicConfig(
    filename='app.log', 
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

@app.errorhandler(404)
def page_not_found(e):
    app.logger.warning(f"404 error: {request.url}")
    return render_template('404.html', title="Page Not Found"), 404

@app.errorhandler(500)
def internal_error(e):
    app.logger.error(f"500 error: {e}")
    return render_template('500.html', title="Server Error"), 500

@app.route("/")
def index():
    users = []
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",  
            password="",  
            database="mywebsite_db"
        )
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT id, name, email FROM users")
        users = cursor.fetchall()
    except mysql.connector.Error as err:
        app.logger.error(f"MySQL Error: {err}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'db' in locals():
            db.close()

    return render_template("index.html", title="My Dynamic Website", users=users)

@app.route("/about")
def about():
    return render_template("about.html", title="About Us")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        message = form.message.data
        return render_template("contact_success.html", name=name)
    return render_template("contact.html", form=form)

@app.route("/add_user", methods=["GET", "POST"])
def add_user():
    form = UserForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        try:
            db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="mywebsite_db"
            )
            cursor = db.cursor()
            cursor.execute("INSERT INTO users (name, email) VALUES (%s, %s)", (name, email))
            db.commit()
            flash("User added successfully!", "success")
        except mysql.connector.Error as err:
            app.logger.error(f"MySQL Error: {err}")
            flash("Database error. Try again later.", "danger")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'db' in locals():
                db.close()
        return redirect(url_for('index'))
    return render_template("manage_users.html", form=form)

@app.route("/edit_user/<int:user_id>", methods=["GET", "POST"])
def edit_user(user_id):
    form = UserForm()
    user = None  # Ensure user is defined

    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="mywebsite_db"
        )
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()

        if not user:
            flash("User not found", "danger")
            return redirect(url_for('index'))

        # Pre-fill form fields if it's a GET request
        if request.method == "GET":
            form.name.data = user["name"]
            form.email.data = user["email"]

        # Handle form submission
        if form.validate_on_submit():
            cursor.execute("UPDATE users SET name=%s, email=%s WHERE id=%s",
                           (form.name.data, form.email.data, user_id))
            db.commit()
            flash("User updated successfully!", "success")
            return redirect(url_for("index"))

    except mysql.connector.Error as err:
        app.logger.error(f"MySQL Error: {err}")
        flash("Database error. Try again later.", "danger")

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'db' in locals():
            db.close()

    # Ensure form is always passed to the template
    return render_template("edit_user.html", form=form, user=user)

if __name__ == "__main__":
    app.run(debug=True)  # Remember to set debug=False in production
