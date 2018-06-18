import csv
import sqlite3

csvpath = './label1.csv'
conn = sqlite3.connect('./label.db')
c = conn.cursor()

create_table = '''create table images(filename, label)'''
c.execute(create_table)



with open(csvpath, 'r', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        sql = 'insert into images (filename, label) values (?,?)'
        image = (row[0], row[1])
        c.execute(sql, image)
    conn.commit()

conn.close()
