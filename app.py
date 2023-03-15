from flask import Flask, redirect, render_template, request, session, url_for, redirect, flash
from flask_session import Session
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from wtforms import BooleanField, PasswordField, StringField
from wtforms.validators import InputRequired, Length #, Email
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from sqlalchemy import ForeignKey
import os 

app = Flask(__name__)
Bootstrap(app)
#connecting to database 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://ohmydftzwauuzh:3d1597ec6c466890965bb4328785b687d4c8ca54b54b378a20cf640f5fead099@ec2-34-226-11-94.compute-1.amazonaws.com:5432/db36ekb7prhk3s' 
#app.config['SQLAlchemy_TRACK_MODIFICATIONS'] = False
app.secret_key = 'BAD_SECRET_KEY'


# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)



db = SQLAlchemy(app)
migrate = Migrate(app,db)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    username = db.Column(db.String(50), unique=True, nullable = False)
    email = db.Column(db.String(50), unique=True, nullable = False)
    password = db.Column(db.String(80), nullable = False)
    #date_added = db.Column(db.DateTime, default=datetime.now())
    
    def __repr__(self):
        return "<Name %r>" % self.username

# add a column for username to retrieve the goals for the current user
class Big_goal(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True )
    user_id = db.Column(db.Integer, ForeignKey(User.id))
    goal = db.Column(db.String(1000), nullable = False)
    date_added = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return "<Goal %r>" % self.goal
    
class Habit(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True )
    big_goal_id = db.Column(db.Integer, ForeignKey(Big_goal.id))
    name = db.Column(db.String(200), nullable = False)
    completion = db.Column(db.Integer, default=0)
    
class Action(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    habit_id = db.Column(db.Integer, ForeignKey(Habit.id))
    week = db.Column(db.Integer)
    day = db.Column(db.Integer)
    name = db.Column(db.String(1000), nullable=False)
    completed = db.Column(db.Boolean, unique=False, default=False)

    def __repr__(self):
        return '<Action %r>' % self.id
    
        
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=4, max=80)])
    remember = BooleanField('Remember me')
  
    
class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), #Email(message='Invalid email'), 
                                             Length(max=50)])
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=50)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=4, max=80)])       
    
class Goal(FlaskForm):
    Goal = StringField('goal', validators=[InputRequired(), Length(min=1, max=1000)])            

class Tree(FlaskForm):
    habit = StringField('habit', validators=[InputRequired(), Length(min=1, max=1000)])
    action = StringField('action', validators=[InputRequired(), Length(min=1, max=10000)])

    
with app.app_context():
    db.create_all()
    db.session.commit()

# Create a decorator (helper function for @app.route) that requires the user to log in at specified pages
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("email") is None:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/homepage', methods=['GET','POST'])
def homepage():
    form=Goal()
    if request.method == "POST":
        #if form.validate_on_submit():
        goal = request.form.get('goal')
        new_goal = Big_goal(goal=goal)
        #print('CREATED user', new_user.username)
        
        db.session.add(new_goal)
        db.session.commit()
        session['goal'] = Big_goal.query.order_by(Big_goal.date_added.desc()).first()
        print(f'submitted long-term goal: {goal}')
        return redirect(url_for('habits'))
    
    return render_template("homepage.html", form=form)

@app.route('/', methods=['GET', 'POST'])
def login():
    #session.clear()
    
    if current_user.is_authenticated: return(url_for('habits'))
    form = LoginForm()
    if form.validate_on_submit():
        
            username = form.username.data
            password = form.password.data
            remember = True if form.password.data else False

            user = User.query.filter_by(username=username).first()
            #print(user)
            # check if the user actually exists
            # take the user-supplied password, hash it, and compare it to the hashed password in the database
            if not user or not check_password_hash(user.password, password):
                flash('Please check your login details and try again.')
                #print('invalid data')
                return redirect(url_for('login'))
            #adding sessions
            session['id'] = user.id 
            session["username"] = user.username
            session["email"] = user.email
            session['goal'] = Big_goal.query.order_by(Big_goal.date_added.desc()).first()
            print("FROM SESSION:", session['username'])
            return redirect(url_for("habits"))
        
    return render_template("login.html", form=form)

# route for loggin out the user
@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route('/register', methods=['GET', 'POST'])
def register():
    name = None
    form = RegistrationForm() 
    #print('Created FORM')
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        #print('Queried USER') 
        if user is None:
            #print(form.username.data, form.email.data, form.password.data)
            new_user = User(username=form.username.data, email=form.email.data, password=generate_password_hash(form.password.data, method='sha256'))
            #print('CREATED user', new_user.username)
            
            db.session.add(new_user)
            db.session.commit()
            #print('ADDED user') 
        name = form.username.data
        form.username.data = ' '
        form.email.data = ' '
        flash('User added successfully!')
        #print(name, user)    
        return render_template("homepage.html") 
    return render_template("register.html", form=form)

@app.route('/habits')
@login_required
def habits():
    
    #goal = Big_goal.query.order_by(Big_goal.date_added.desc()).first()
    goal = session['goal']
    habits = Habit.query.filter_by(big_goal_id=goal.id).all()
    for habit in habits: 
        actions = Action.query.filter_by(habit_id=habit.id).all()
        if len(actions) > 0:
            fraction = int(sum([1 if a.completed else 0 for a in actions])/len(actions)*100)
            habit.completion = fraction
            db.session.commit()
        print(habit.name, habit.completion)
        
    print(f"retrieved your goal {goal.goal} - {goal.date_added}")
    return render_template("habits.html", goal=goal.goal, habits=habits)

@app.route('/tree', methods = ['POST', 'GET'])
@login_required
def tree():
    db_week_action = Action.query.order_by(Action.id).all()
    print(db_week_action)
    #goal = Big_goal.query.order_by(Big_goal.date_added.desc()).first()
    goal = session['goal']
    habits = Habit.query.filter_by(big_goal_id=goal.id).all()
    print(f"retrieved your goal {goal}")

    return render_template("tree.html", goal=goal.goal, db_week_action=db_week_action, habits=habits)

@app.route('/add_action/<habit_id>', methods=['POST', 'GET'])
@login_required
def add_action(habit_id):
    if request.method == "POST":
        action_name = request.form.get('name')
        
        new_action = Action(name = action_name,
                            habit_id = habit_id,
                            week=1,
                            day=1,
                            completed=False)

        db.session.add(new_action)
        db.session.commit()
        return redirect(url_for("tree"))
    else:
        return redirect(url_for("tree"))


@app.route('/add_habit', methods=['POST', 'GET'])
@login_required
def add_habit():
    if request.method == "POST":

        habit_name = request.form.get('habit')
        new_habit = Habit(name = habit_name, big_goal_id=session["goal"].id)

        db.session.add(new_habit)
        db.session.commit()
        return redirect(url_for("habits"))
    else:
        return redirect(url_for("habits"))

@app.route('/change_status/<action_id>', methods=['POST', 'GET'])
@login_required
def change_status(action_id):
    action = Action.query.filter_by(id=action_id).first()
    action.completed = not action.completed
    db.session.commit()
    
    return redirect(url_for("tree"))


@app.route('/badges')
@login_required
def badges():
    goal = Big_goal.query.order_by(Big_goal.date_added.desc()).first()
    print(f"retrieved your goal {goal}")
    return render_template("badges.html", goal=goal.goal)

@app.route('/add_badges/<habit_id>', methods=['POST', 'GET'])
@login_required
def add_badges(habit_id):
    goal = session['goal']
    habits = Habit.query.filter_by(id=habit.id).all()
    for habit in habits: 
        if habit.completion == 1:
            habit_complete = Habit.query.order_by(Habit.id).all()
            print(habit_complete)
            print(f"retrieved your goal {goal}")

        return render_template("badge.html", goal=goal.goal, habit_complete=habit_complete, habits=habits)
                

if __name__=="__main__":
    app.run(debug=True)
    
    