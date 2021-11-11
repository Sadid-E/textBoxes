# PM: Sadid - textBoxes 

from flask import Flask             #facilitate flask webserving
from flask import render_template   #facilitate jinja templating
from flask import request           #facilitate form submission
from flask import session           #cookies
from flask import redirect
import os #for secret_key
import sqlite3


app = Flask(__name__)    #create Flask object
app.secret_key = os.urandom(32)

DB_FILE="story.db"
db = sqlite3.connect(DB_FILE) #open if file exists, otherwise create
c = db.cursor()               #facilitate db ops -- you will use cursor to trigger db events
c.execute("CREATE TABLE IF NOT EXISTS accounts(username TEXT, password TEXT, storiescontributed TEXT, storiescreated TEXT);")
db.commit()
db.close()

@app.route("/", methods=['GET', 'POST'])
def disp_loginpage():
	if session.get("name"):
		return loggedIn() #remembers when you're logged in
	return render_template('base.html')

@app.route("/auth", methods=['GET', 'POST'])
def authenticate():
	m = request.method #either get or post
	if session.get("name"):
		return render_template('response.html', username = session["name"], method = m)
	user = request.form['username']
	pwd = request.form['password']
	if(user == ''): #empty username
		return render_template('login.html', error="No username inputted. Try again.")
	if(pwd == ''): #empty password
		return render_template('login.html', error="No password inputted. Try again.")
	db = sqlite3.connect(DB_FILE)
	c = db.cursor()
	c.execute("SELECT * from accounts WHERE username=:u AND password=:p;", {"u":user, "p":pwd})
	if not c.fetchone():
		return render_template('login.html', error="Username or password incorrect. Try again.")
	else:
		session["name"] = request.form['username'] #inputs cookies
		session["password"] = request.form['password'] #inputs cookies
		return render_template('response.html', username = session["name"], method = m)
	db.commit()
	db.close()

@app.route("/create", methods=['GET', 'POST'])
def create():
	user = request.form['username']
	pwd = request.form['password']
	db = sqlite3.connect(DB_FILE)
	c = db.cursor()
	c.execute("SELECT * from accounts WHERE username=:u", {"u":user})
	if(user == ''): #empty username
		return render_template('register.html', error="No username inputted. Try again.")
	if(pwd == ''): #empty password
		return render_template('register.html', error="No password inputted. Try again.")
	if pwd != request.form['c_password']:
		return render_template('register.html', error="Passwords do not match. Try again.")
	if c.fetchone():
		return render_template('register.html', error="Username already exists. Try again.")
	else:
		c.execute('INSERT INTO accounts (username, password, storiescontributed, storiescreated) VALUES(?,?,?,?)',(request.form['username'],request.form['password'],"/","/"))
		db.commit()
		db.close()
		m = request.method
		session["name"] = request.form['username']
		session["password"] = request.form['password']
		return render_template('response.html', username = session["name"], method = m)

@app.route("/recentStories", methods=['GET', 'POST'])
def viewRecent():
	return render_template('recentStories.html', username = session["name"], method = "GET", error="")

@app.route("/login" , methods = ['GET', 'POST'])
def disp_login():
	m = request.method #either get or post
	if session.get("name"):
		return redirect("/auth")
	return render_template('login.html', error = '')

@app.route("/register" , methods = ['GET', 'POST'])
def disp_register():
	m = request.method #either get or post
	if session.get("name"):
		return redirect("/auth")
	return render_template('register.html', error='')

@app.route("/out", methods=['GET', 'POST'])
def out(): #logging out
	if len(session) > 0: #gets rid of cookie
		session.pop("name")
		session.pop("password")
	return redirect("/") #goes back to login page

@app.route("/in", methods=['GET', 'POST'])
def loggedIn():
	return render_template('response.html', username = session["name"], method = "GET", error="")

@app.route("/findStories", methods=['GET', 'POST'])
def newstorylist():
	db = sqlite3.connect("story.db")
	c = db.cursor()
	c.execute("SELECT storiescontributed FROM accounts WHERE username='"+session['name']+"';")
	new = c.fetchone()[0]
	contributed = new.split("/")[1:-1]
	c.execute("SELECT name FROM sqlite_master WHERE type='table';")
	total=c.fetchall();
	unused=[]
	for i in total:
		if (i[0] not in contributed and i[0] != "accounts"):
			unused.append(i[0])
	titles=[]
	lastentry=[]
	poster=[]

	for i in unused:
		c.execute("SELECT entrytext FROM '"+i+"' WHERE entrynum=0")
		store=c.fetchone()[0];
		titles.append(store)

		c.execute("SELECT entrytext FROM '" + i + "' WHERE entrynum=-1")
		store = c.fetchone()[0];
		lastentry.append(store)

		c.execute("SELECT user FROM '" + i + "' WHERE entrynum=-1")
		store = c.fetchone()[0];
		poster.append(store)
	db.commit()
	db.close()
	num = len(poster)
	return render_template('recentStories.html',titles=titles,lastentry=lastentry,poster=poster,num=num, buttons=unused)

@app.route("/editstory", methods=['GET', 'POST'])
def entrypage():
	db = sqlite3.connect("story.db")
	c = db.cursor()
	i=request.form["toedit"]
	print(i)
	c.execute("SELECT entrytext FROM '" + i + "' WHERE entrynum=-1")
	lastentry = c.fetchone()[0];

	c.execute("SELECT entrytext FROM '" + i + "' WHERE entrynum=0")
	title = c.fetchone()[0];

	c.execute("SELECT user FROM '" + i + "' WHERE entrynum=-1")
	lastuser = c.fetchone()[0];

	c.execute("SELECT user FROM '" + i + "' WHERE entrynum=0")
	origin = c.fetchone()[0];
	db.commit()
	db.close()
	#don't forget to address this later
	session['target']=i
	return render_template("editstory.html", title=title, origin=origin, lastentry=lastentry, poster=lastuser, error="", entry="New Entry" )

@app.route("/updatestory", methods=['GET', 'POST'])
def updatestory():
	k=request.form['newentry']
	i = session['target']
	session.pop('target')
	wordcount=len(k.split(" "))
	q="Your entry is "+str(wordcount)+" words long. Please reduce it to less than 200."
	if (wordcount>200):
		return render_template("editstory.html", title=title, origin=origin, lastentry=lastentry, poster=lastuser, error=q, entry=k )
	else:
		db = sqlite3.connect("story.db")
		c = db.cursor()
		c.execute("SELECT entrynum from "+i)
		nums=c.fetchall()
		top=1;
		for en in nums:
			if(en[0]>top):
				top=en[0]
		top=top+1
		c.execute('INSERT INTO ' + i + ' (entrynum, entrytext, user) VALUES(?,?,?)',
				  (top, k, session["name"]))
		c.execute("UPDATE "+i+" SET entrytext='" + k + "',user= '" + session['name'] + "' WHERE entrynum=-1")

		c.execute("SELECT storiescontributed FROM accounts WHERE username='" + session['name'] + "'")
		new = c.fetchone()[0] + i + "/"
		c.execute("UPDATE accounts SET storiescontributed='" + new + "' WHERE username='" + session['name'] + "'")

		db.commit()
		db.close()
		return render_template('response.html', username = session["name"], method = "GET", error="")
@app.route("/makestory", methods=['GET', 'POST'])
def editpage():
	return render_template('createstory.html',error="", entry="First Entry")

@app.route("/poststory", methods=['GET', 'POST'])
def poststory():
	title=request.form["storytitle"]
	entry=request.form['firstentry']
	if (title=="" or title.isspace()): 
		return render_template('createstory.html',error="Please enter a title.",entry=entry)
	if not title.replace(" ","").isalnum(): # checks if title only includes alphanumeric characters
		return render_template('createstory.html',error="Please make sure the title only includes alphanumeric characters.",entry=entry)
	db = sqlite3.connect("story.db")
	c = db.cursor()
	k=c.execute("SELECT * FROM sqlite_master WHERE type='table' AND name=:n;", {"n":title.replace(" ","").lower()}) # checks for duplicate titles

	if c.fetchall():
		db.commit()
		db.close()
		return render_template('createstory.html',error="Title already in use. Please pick another one")
	else:
		text=request.form["firstentry"]
		c.execute("CREATE TABLE "+title.replace(" ","").lower()+"(entrynum INTEGER,entrytext TEXT,user TEXT);")
		c.execute('INSERT INTO '+title.replace(" ","").lower()+' (entrynum, entrytext, user) VALUES(?,?,?)',(0,title,session["name"]))
		c.execute('INSERT INTO ' + title.replace(" ","").lower() + ' (entrynum, entrytext, user) VALUES(?,?,?)', (1, text, session["name"]))
		c.execute('INSERT INTO ' + title.replace(" ", "").lower() + ' (entrynum, entrytext, user) VALUES(?,?,?)',(-1, text, session["name"]))
		c.execute("SELECT storiescontributed FROM accounts WHERE username='" + session['name'] + "'")
		new= c.fetchone()[0]+title.replace(" ","").lower()+"/"
		c.execute("UPDATE accounts SET storiescontributed='"+new+"' WHERE username='" + session['name'] + "'")

		c.execute("SELECT storiescreated FROM accounts WHERE username='" + session['name'] + "'")
		new = c.fetchone()[0] + title.replace(" ", "").lower() + "/"
		c.execute("UPDATE accounts SET storiescreated='" + new + "' WHERE username='" + session['name'] + "'")

		db.commit()
		db.close()
		return redirect("/in")


if __name__ == "__main__": #false if this file imported as module
	#enable debugging, auto-restarting of server when this file is modified
	app.debug = True
	app.run()
