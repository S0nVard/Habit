from flask import Flask, redirect, render_template, request, session, url_for, redirect, flash
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from wtforms import BooleanField, PasswordField, StringField
from wtforms.validators import InputRequired, Length#, Email
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
Bootstrap(app)
#connecting to database 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
#app.config['SQLAlchemy_TRACK_MODIFICATIONS'] = False
app.secret_key = 'BAD_SECRET_KEY'
db = SQLAlchemy(app)
migrate = Migrate(app,db)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50), unique=True, nullable = False)
    email = db.Column(db.String(50), unique=True, nullable = False)
    password = db.Column(db.String(80), nullable = False)
    #date_added = db.Column(db.DateTime, default=datetime.now())
    
    def __repr__(self):
        return "<Name %r>" % self.username

class Big_goal(db.Model):
    id = db.Column(db.Integer, primary_key = True )
    goal = db.Column(db.String(1000), nullable = False)
    date_added = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return "<Goal %r>" % self.goal
        
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

with app.app_context():
    db.create_all()
    db.session.commit()

@app.route('/homepage', methods=['GET','POST'])
#@login_required
def homepage():
    form=Goal()
    if request.method == "POST":
        #if form.validate_on_submit():
        goal = request.form.get('goal')
        new_goal = Big_goal(goal=goal)
        #print('CREATED user', new_user.username)
        
        db.session.add(new_goal)
        db.session.commit()
        print(f'submitted long-term goal: {goal}')
        return redirect(url_for('habits'))
    
    return render_template("homepage.html", form=form)

@app.route('/signup')
def signup():
    return render_template("signup.html")

@app.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: return(url_for('habits'))
    form = LoginForm()
    if form.validate_on_submit():
        
            username = form.username.data
            password = form.password.data
            remember = True if form.password.data else False

            user = User.query.filter_by(username=username).first()
            print(user)
            # check if the user actually exists
            # take the user-supplied password, hash it, and compare it to the hashed password in the database
            if not user or not check_password_hash(user.password, password):
                flash('Please check your login details and try again.')
                #print('invalid data')
                return redirect(url_for('login'))
                
            return redirect(url_for("habits"))
    
    return render_template("login.html", form=form)



@app.route('/register', methods=['GET', 'POST'])
def register():
    name = None
    form = RegistrationForm() 
    #print('Created FORM')
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
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
def habits():
    goal = Big_goal.query.order_by(Big_goal.date_added.desc()).first()
    print(f"retrieved your goal {goal}")
    return render_template("habits.html", goal=goal.goal)

@app.route('/tree')
def summary():
    goal = Big_goal.query.order_by(Big_goal.date_added.desc()).first()
    print(f"retrieved your goal {goal}")
    return render_template("tree.html", goal=goal.goal)

@app.route('/badges')
def calendar():
    goal = Big_goal.query.order_by(Big_goal.date_added.desc()).first()
    print(f"retrieved your goal {goal}")
    return render_template("badges.html", goal=goal.goal)


@app.route("/logout")
def logout():
    flash('Logged out successfully!', category='success')
    logout_user()
    return render_template('login.html')

if __name__=="__main__":
    app.run(debug=True)
    
    