import sqlite3
from datetime import datetime
import threading

class Database:
    def __init__(self, db_name='castings.db'):
        self.db_name = db_name
        self.thread_local = threading.local()
        self.create_table()

    def get_connection(self):
        if not hasattr(self.thread_local, "connection"):
            self.thread_local.connection = sqlite3.connect(self.db_name)
        return self.thread_local.connection

    def create_table(self):
        conn = self.get_connection()
        conn.execute('''
        CREATE TABLE IF NOT EXISTS castings (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Наименование_отливки TEXT,
            Исполнитель1 TEXT,
            Исполнитель2 TEXT,
            Контролер1 TEXT,
            Контролер2 TEXT,
            Контроль_подано INTEGER,
            Контроль_дата_приемки DATE,
            Контроль_принято INTEGER,
            Второй_сорт_раковины INTEGER,
            Второй_сорт_зарез INTEGER,
            Второй_сорт_прочее INTEGER,
            Доработка_лапы INTEGER,
            Доработка_питатель INTEGER,
            Доработка_корона INTEGER,
            Окончательный_брак_Недолив INTEGER,
            Окончательный_брак_Вырыв INTEGER,
            Окончательный_брак_Зарез INTEGER,
            Окончательный_брак_Коробление INTEGER,
            Окончательный_брак_Наплыв_металла INTEGER,
            Окончательный_брак_Нарушение_геометрии INTEGER,
            Окончательный_брак_Нарушение_маркировки INTEGER,
            Окончательный_брак_Непроклей INTEGER,
            Окончательный_брак_Неслитина INTEGER,
            Окончательный_брак_Несоответствие_внешнего_вида INTEGER,
            Окончательный_брак_Несоответствие_размеров INTEGER,
            Окончательный_брак_Пеномодель INTEGER,
            Окончательный_брак_Пористость INTEGER,
            Окончательный_брак_Пригар_песка INTEGER,
            Окончательный_брак_Рыхлота INTEGER,
            Окончательный_брак_Раковины INTEGER,
            Окончательный_брак_Скол INTEGER,
            Окончательный_брак_Слом INTEGER,
            Окончательный_брак_Спай INTEGER,
            Окончательный_брак_Трещины INTEGER,
            Окончательный_брак_Прочее INTEGER,
            Примечание TEXT
        )
        ''')
        conn.commit()

    def insert_record(self, data):
        conn = self.get_connection()
        query = '''INSERT INTO castings (
            Наименование_отливки, Исполнитель1, Исполнитель2,
            Контролер1, Контролер2,
            Контроль_подано, Контроль_дата_приемки, Контроль_принято,
            Второй_сорт_раковины, Второй_сорт_зарез, Второй_сорт_прочее,
            Доработка_лапы, Доработка_питатель, Доработка_корона,
            Окончательный_брак_Недолив, Окончательный_брак_Вырыв,
            Окончательный_брак_Зарез, Окончательный_брак_Коробление,
            Окончательный_брак_Наплыв_металла, Окончательный_брак_Нарушение_геометрии,
            Окончательный_брак_Нарушение_маркировки, Окончательный_брак_Непроклей,
            Окончательный_брак_Неслитина, Окончательный_брак_Несоответствие_внешнего_вида,
            Окончательный_брак_Несоответствие_размеров, Окончательный_брак_Пеномодель,
            Окончательный_брак_Пористость, Окончательный_брак_Пригар_песка,
            Окончательный_брак_Рыхлота, Окончательный_брак_Раковины,
            Окончательный_брак_Скол, Окончательный_брак_Слом,
            Окончательный_брак_Спай, Окончательный_брак_Трещины,
            Окончательный_брак_Прочее, Примечание
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        
        conn.execute(query, data)
        conn.commit() 