# PM: Sadid - textBoxes 


from flask import Flask             #facilitate flask webserving
from flask import render_template   #facilitate jinja templating
from flask import request           #facilitate form submission
from flask import session           #cookies
import os #for secret_key

#the conventional way:
#from flask import Flask, render_template, request

app = Flask(__name__)    #create Flask object
app.secret_key = os.urandom(32)

@app.route("/", methods=['GET', 'POST'])
def disp_loginpage():
    #print(session)
    if session.get("name"):
        return loggedIn() #remembers when you're logged in
    
    return render_template('base.html')


@app.route("/auth", methods=['GET', 'POST'])
def authenticate():
    if(request.form['username'] == ''): #empty username
        return Error("No username inputted. Login again. ")
    if(request.form['password'] == ''): #empty password
        return Error("No password inputted. Login again.")
    if (request.form['username'] != "user") or (request.form['password'] != "password"):
        #if request.form['username'] != "Snaps": #incorrect Username
            #return Error("Incorrect Username! Login again. ")
        return Error("Incorrect Password! Login again." )
  
    m = request.method #either get or post
    session["name"] = request.form['username'] #inputs cookies
    session["password"] = request.form['password'] #inputs cookies
    #print(request.form['username'])
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
