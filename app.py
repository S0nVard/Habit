from flask import Flask, redirect, render_template, request, url_for, session

app = Flask(__name__)

@app.route('/')
def homepage():
    return render_template("homepage.html")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/register')
def signup():
    return render_template("register.html")


if __name__=="__main__":
    app.run(debug=True)
    
    