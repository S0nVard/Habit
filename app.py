from flask import Flask, redirect, render_template, request, url_for, session
app = Flask(__name__)

app.config['SECRET_KEY'] = 't4grewf78iuhrefiukhre7374irwhj73428yriw374eiu' 

@app.route('/')
def login():
    return render_template("login.html")

@app.route('/success')
def success():
    return render_template("homepage.html")

@app.route('/register')
def register():
    return render_template("register.html")

@app.route('/account')
def account():
    return render_template("account.html")

if __name__=="__main__":
    app.run(debug=True)
    
    