import sqlite3
import os

basepath = os.path.split(os.path.realpath(__file__))[0]

convertDict = {"J":1,"M":2,"E":3,"D":4,"A":5}

def convertInt(grade,affiliation):
    if grade != 1:
        affiliationInt = convertDict[affiliation]
    else:
        affiliationInt = int(affiliation)

    return affiliationInt

conn = sqlite3.connect(os.path.join(basepath,"HealthCheck-userList.db"))
c = conn.cursor()

c.execute("select * from userList")
userList = c.fetchall()

afterUserList = []
for user in userList:
    user = list(user)
    user.insert(3,convertInt(user[1],user[2]))
    afterUserList.append(tuple(user))

c.execute("DROP TABLE IF EXISTS userList")
c.execute("create table userList(userID int,userGrade int,userAffiliation txt,affiliationInt int,userName txt,healthStatus int)")

c.executemany("insert into userList(userID,userGrade,userAffiliation,affiliationInt,userName,healthStatus) values (?,?,?,?,?,?)",afterUserList)

conn.commit()
conn.close()
