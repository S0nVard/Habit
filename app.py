#from ensurepip import bootstrap
from flask import Flask, redirect, render_template, request, session, url_for, redirect
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField
from wtforms.validators import InputRequired, Length#, Email



app = Flask(__name__)
Bootstrap(app)
#connecting to database 
app.config['SQLAlchemy_TRACK_MODIFICATIONS'] = False
app.secret_key = 'BAD_SECRET_KEY'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(15), unique=True, nullable = False)
    email = db.Column(db.String(50), unique=True, nullable = False)
    password = db.Column(db.String(80), nullable = False)


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=4, max=80)])
    remember = BooleanField('Remember me')
    
    
class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), #Email(message='Invalid email'), 
                                             Length(max=50)])
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=4, max=80)])                   

with app.app_context():
    db.create_all()
    db.session.commit()

@app.route('/')
def homepage():
    return render_template("homepage.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():

        return '<h1>'+ form.username.data + ' ' + form.password.data +'</h1>'
    
    return render_template("login.html", form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()        
    if form.validate_on_submit():
        return '<h1>' + form.username.data + " " + form.email.data + " "+ form.password.data + '</h1>'  
    
    return render_template("register.html", form=form)

@app.route('/account')
def account():
    return render_template("account.html")

@app.route('/summary')
def summary():
    return render_template("summary.html")

@app.route('/calendar')
def calendar():
    return render_template("calendar.html")

@app.route('/habits')
def habits():
    return render_template("habits.html")


if __name__=="__main__":
    app.run(debug=True)
    
    