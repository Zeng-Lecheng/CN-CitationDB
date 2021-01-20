from citationdb import Db


database = Db('./db.json')


if __name__ == '__main__':
    database.write_db()
