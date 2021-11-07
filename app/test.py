import sqlite3

title = 'stuff'
db = sqlite3.connect("story.db")
c = db.cursor()
k = "SELECT name FROM sqlite_master WHERE type='table';"
listOfTables = c.execute(k).fetchall()
if (title in listOfTables):
    print("nope")
    db.commit()
    db.close()
else:
    text = 'beeeeboooop'
    #c.execute("CREATE TABLE " + title + "(entrynum INTEGER,entrytext TEXT,user TEXT);")
    #c.execute('INSERT INTO ' + title + ' (entrynum, entrytext, user) VALUES(?,?,?)', (0, text, 'gavin'))
    print('success')

c.execute("DROP TABLE CowBoyBebop;")

db.commit()
db.close()