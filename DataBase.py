import sqlite3
from time import time

class DataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def get_menu(self):
        try:
            self.__cur.execute('SELECT * FROM menu')
            res = self.__cur.fetchall()
            if res:
                return res
        except IOError:
            print('Data reading error!')
        return []

    def add_post(self, title, text, url):
        try:
            self.__cur.execute('SELECT COUNT(*) as "count" FROM posts WHERE url = ?', (url,))
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print('An article with this URL already exists!')
                return False

            tm = time()
            self.__cur.execute('INSERT INTO posts (title, text, url, time) VALUES (?, ?, ?, ?)',
                               (title, text, url, tm))
            self.__db.commit()
            print('Article added successfully:', title)
        except sqlite3.Error as e:
            print('Error adding an article to the database!', e)
            return False
        return True

    def get_posts(self):
        try:
            self.__cur.execute('SELECT * FROM posts')
            res = self.__cur.fetchall()
            if res:
                return res
        except sqlite3.Error as e:
            print('Error getting articles from the database!', e)
        return []




