import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="Nitram86287337",
)

myc = mydb.cursor()
myc.execute("USE python_database")

#myc.execute("CREATE TABLE pythontableperson(personID INT(11) NOT NULL PRIMARY KEY AUTO_INCREMENT UNIQUE KEY, name VARCHAR(20) NOT NULL, cpr VARCHAR(12) NOT NULL UNIQUE KEY, address VARCHAR(50) NOT NULL)")

