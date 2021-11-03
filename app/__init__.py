# PM: Sadid - textBoxes 


from flask import Flask             #facilitate flask webserving
from flask import render_template   #facilitate jinja templating
from flask import request           #facilitate form submission
from flask import session           #cookies
import os #for secret_key
import sqlite3

#the conventional way:
#from flask import Flask, render_template, request

app = Flask(__name__)    #create Flask object
app.secret_key = os.urandom(32)

DB_FILE="story.db"

db = sqlite3.connect(DB_FILE) #open if file exists, otherwise create
c = db.cursor()               #facilitate db ops -- you will use cursor to trigger db events

c.execute("CREATE TABLE IF NOT EXISTS accounts(username TEXT, password TEXT);")

db.commit()
db.close()

@app.route("/", methods=['GET', 'POST'])
def disp_loginpage():
    #print(session)
    if session.get("name"):
        return loggedIn() #remembers when you're logged in
    
    return render_template('base.html')


@app.route("/auth", methods=['GET', 'POST'])
def authenticate():
    user = request.form['username']
    pwd = request.form['password']
    if(user == ''): #empty username
        return render_template('login.html', error="No username inputted. Login again.")
    if(pwd == ''): #empty password
        return render_template('login.html', error="No password inputted. Login again.")
    db = sqlite3.connect(DB_FILE) 
    c = db.cursor()
    c.execute("SELECT * from accounts WHERE username=:u AND password=:p;", {"u":user, "p":pwd})
    if not c.fetchone():
        return render_template('login.html', error="Username or password incorrect. Login again.")
    else:
        m = request.method #either get or post
        session["name"] = request.form['username'] #inputs cookies
        session["password"] = request.form['password'] #inputs cookies
        return render_template('response.html', username = session["name"], method = m)
    db.commit()
    db.close()

@app.route("/create", methods=['GET', 'POST'])
def create():
    db = sqlite3.connect(DB_FILE) 
    c = db.cursor()
    c.execute('INSERT INTO accounts (username, password) VALUES(?,?)',(request.form['username'],request.form['password']))
    db.commit()
    db.close()
    m = request.method 
    session["name"] = request.form['username'] 
    session["password"] = request.form['password'] 
    return render_template('response.html', username = session["name"], method = m)

@app.route("/login" , methods = ['GET', 'POST'])
def disp_login():
    return render_template('login.html', error = '')

@app.route("/register" , methods = ['GET', 'POST'])
def disp_register():
    return render_template('register.html')

@app.route("/out")
def out(): #logging out
    #print(len(session))
    if len(session) > 0: #gets rid of cookie
        session.pop("name")
        session.pop("password")
    #print(len(session))
    return render_template('base.html', error = '') #goes back to login page

@app.route("/empty")
def Error(message): #inputted message for optimiziation
    return render_template('base.html', error = message) #message depends on the error checked in authenticate

@app.route("/in")
def loggedIn():
    return render_template('response.html', username = session["name"], method = "GET")

if __name__ == "__main__": #false if this file imported as module
    #enable debugging, auto-restarting of server when this file is modified
    app.debug = True
    app.run()
