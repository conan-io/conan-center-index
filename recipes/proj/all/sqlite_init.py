import sqlite3
import sys

con = sqlite3.connect(sys.argv[1])
with open(sys.argv[2], 'rb') as sql_init:
    con.executescript(sql_init.read().decode("UTF-8"))
con.close()
