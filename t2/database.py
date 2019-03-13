import sqlite3
from sqlite3 import Error


class Database:
    def __init__(self):
        self.page_number = 1
        self.page_size = 10
        self.conn = self.create_connection("database.db")

    def create_connection(self, db_file):
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except Error as e:
            print(e)
        return None

    def set_page(self, page_number):
        self.page_number = page_number

    def get_results(self, cur):
        results = []
        for iter in range(0, self.page_number):
            prev_results = results.copy()
            results = cur.fetchmany(self.page_size)
            if not results:
                self.set_page(1)
                return prev_results
        self.set_page(1)
        return results

    def select_all_products(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM products")
        rows = self.get_results(cur)
        return rows

    def select_all_movies(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM movies")
        rows = self.get_results(cur)
        return rows

    def select_product_id(self, id):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM products WHERE id = ?", (id,))
        rows = self.get_results(cur)
        return rows

    def select_movie_id(self, id):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM movies WHERE id = ?", (id,))
        rows = self.get_results(cur)
        return rows

    def select_products_date(self, date):
        cur = self.conn.cursor()
        cur.execute(
            r"SELECT * FROM products WHERE expiration_date < ?", (date,))
        rows = self.get_results(cur)
        return rows

    def select_product_name(self, product):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT * FROM products WHERE UPPER(product_name) like UPPER(?)", (product,))
        rows = self.get_results(cur)
        return rows

    def select_movie_name(self, product):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT * FROM movies WHERE UPPER(movie_title) like UPPER(?)", (product,))
        rows = self.get_results(cur)
        return rows

    def select_product_name_date(self, product, date):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT * FROM products WHERE UPPER(product_name) like UPPER(?) AND expiration_date < ?", (product, date))
        rows = self.get_results(cur)
        return rows

    def insert_product(self, name, date):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO products(product_name, expiration_date) VALUES(?,?)", (name, date))
        self.conn.commit()
        return cur.lastrowid

    def insert_movie(self, name, genre):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO movies(movie_title, movie_genre) VALUES(?,?)", (name, genre))
        self.conn.commit()
        return cur.lastrowid

    def insert_product_id(self, id, name, date):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO products(id, product_name, expiration_date) VALUES(?,?,?)", (id, name, date))
        self.conn.commit()

    def insert_movie_id(self, id, name, genre):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO movies(id, movie_title, movie_genre) VALUES(?,?,?)", (id, name, genre))
        self.conn.commit()

    def delete_product_id(self, id):
        cur = self.conn.cursor()
        cur.execute('DELETE FROM products WHERE id=?', (id,))
        self.conn.commit()

    def delete_movie_id(self, id):
        cur = self.conn.cursor()
        cur.execute('DELETE FROM movies WHERE id=?', (id,))
        self.conn.commit()

    def delete_product_name(self, name):
        cur = self.conn.cursor()
        cur.execute('DELETE FROM products WHERE product_name like ?', (name,))
        self.conn.commit()

    def update_product(self, id, name, date):
        sql = "UPDATE products SET product_name = ?, expiration_date = ? WHERE id = ?"
        cur = self.conn.cursor()
        ceva = cur.execute(sql, (name, date, id))
        self.conn.commit()

    def update_movie(self, id, name, genre):
        sql = "UPDATE movies SET movie_title = ?, genre = ? WHERE id = ?"
        cur = self.conn.cursor()
        cur.execute(sql, (name, genre, id))
        self.conn.commit()
