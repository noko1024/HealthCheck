import sqlite3
import os

basepath = os.path.split(os.path.realpath(__file__))[0]

convertDict = {"J":1,"M":2,"E":3,"D":4,"A":5}

conn = sqlite3.connect(os.path.join(basepath,"HealthCheck-userList.db"))
c = conn.cursor()

c.execute("select * from userList")
userList = c.fetchall()

afterUserList = []
for user in userList:
    user = list(user)
    user[1] += 1
    if user[1] == 6:
        continue
    afterUserList.append(tuple(user))

c.execute("DROP TABLE IF EXISTS userList")
c.execute("create table userList(userID int,userGrade int,userAffiliation txt,affiliationInt int,userName txt,healthStatus int)")

c.executemany("insert into userList(userID,userGrade,userAffiliation,affiliationInt,userName,healthStatus) values (?,?,?,?,?,?)",afterUserList)

conn.commit()
conn.close()
