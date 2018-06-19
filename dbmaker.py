import os
import sys
import glob
import sqlite3

labelpath = './label_M_g.db'

def create_dbfile():
    conn = sqlite3.connect(labelpath)
    c = conn.cursor()
    create_table = '''create table images(filename, label)'''
    c.execute(create_table)
    conn.commit()
    conn.close()


def insert_all_images(path, label):
    targets = glob.glob(os.path.join(path, '*.jpg'))
    num_of_images = len(targets)
    print("{}枚の画像があります．．．".format(num_of_images))

    conn = sqlite3.connect(labelpath)
    c = conn.cursor()

    for image in targets:
        filename = os.path.basename(image)
        label = int(label)
        sql = 'insert into images (filename, label) values (?,?)'
        image = (filename, label)
        c.execute(sql, image)
    
    conn.commit()
    conn.close()


def main(arg1, arg2):
    arg = sys.argv
    path = arg1
    label = arg2
    create_dbfile()
    #insert_all_images(path, label)


if __name__ == '__main__':
    arg = sys.argv
    main(arg[1], arg[2])