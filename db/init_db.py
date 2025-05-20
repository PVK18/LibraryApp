import sqlite3

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # <- подняться на уровень выше
DB_DIR = os.path.join(BASE_DIR, "db")
DB_FILE = os.path.join(DB_DIR, "library.db")

def ensure_db_folder():
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)

def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        print("Соединение с SQLite установлено")
        return conn
    except sqlite3.Error as e:
        print("Ошибка подключения:", e)
        return None

def create_schema(conn):
    cursor = conn.cursor()

    # Таблица Библиотеки
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS libraries (
        library_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        address TEXT NOT NULL
    );
    """)

    # Таблица Тематики
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS themes (
        theme_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    );
    """)

    # Таблица Издательства
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS publishers (
        publisher_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        address TEXT
    );
    """)

    # Таблица Книги
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        library_id INTEGER,
        book_id INTEGER,
        theme_id INTEGER,
        author TEXT NOT NULL,
        title TEXT NOT NULL,
        publisher TEXT,
        publish_place TEXT,
        publish_year INTEGER CHECK(publish_year > 1000 AND publish_year <= strftime('%Y', 'now')),
        quantity INTEGER DEFAULT 1 CHECK(quantity >= 0),
        PRIMARY KEY (library_id, book_id),
        FOREIGN KEY (library_id) REFERENCES libraries(library_id) ON DELETE CASCADE,
        FOREIGN KEY (theme_id) REFERENCES themes(theme_id)
    );
    """)

    # Таблица Читатели
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS readers (
        reader_id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        address TEXT,
        phone TEXT UNIQUE
    );
    """)

    # Таблица Абонементы
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subscriptions (
        library_id INTEGER,
        book_id INTEGER,
        reader_id INTEGER,
        issue_date TEXT NOT NULL,
        return_date TEXT,
        advance REAL DEFAULT 0 CHECK(advance >= 0),
        PRIMARY KEY (library_id, book_id, reader_id, issue_date),
        FOREIGN KEY (library_id, book_id) REFERENCES books(library_id, book_id) ON DELETE CASCADE,
        FOREIGN KEY (reader_id) REFERENCES readers(reader_id)
    );
    """)

    conn.commit()

def create_indexes(conn):
    cursor = conn.cursor()

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_books_author ON books(author);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_books_title ON books(title);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_subscriptions_reader ON subscriptions(reader_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_subscriptions_return ON subscriptions(return_date);")

    conn.commit()

def create_triggers(conn):
    cursor = conn.cursor()

    # Уменьшение количества книг после выдачи
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS reduce_quantity_after_issue
    AFTER INSERT ON subscriptions
    BEGIN
        UPDATE books
        SET quantity = quantity - 1
        WHERE library_id = NEW.library_id AND book_id = NEW.book_id;
    END;
    """)

    # Увеличение количества книг при возврате
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS increase_quantity_after_return
    AFTER UPDATE OF return_date ON subscriptions
    WHEN NEW.return_date IS NOT NULL AND OLD.return_date IS NULL
    BEGIN
        UPDATE books
        SET quantity = quantity + 1
        WHERE library_id = NEW.library_id AND book_id = NEW.book_id;
    END;
    """)

    conn.commit()

def create_views(conn):
    cursor = conn.cursor()

    # Просмотр доступных книг
    cursor.execute("""
    CREATE VIEW IF NOT EXISTS available_books AS
    SELECT *
    FROM books
    WHERE quantity > 0;
    """)

    # Просмотр количества выданных книг по библиотекам
    cursor.execute("""
    CREATE VIEW IF NOT EXISTS issued_books_count AS
    SELECT s.library_id, l.name AS library_name, COUNT(*) AS issued_count
    FROM subscriptions s
    JOIN libraries l ON s.library_id = l.library_id
    GROUP BY s.library_id
    HAVING issued_count > 5;
    """)

    # Просмотр книг с тематиками
    cursor.execute("""
    CREATE VIEW IF NOT EXISTS book_theme_info AS
    SELECT b.book_id, b.title, b.author, t.name AS theme_name
    FROM books b
    JOIN themes t ON b.theme_id = t.theme_id;
    """)

    conn.commit()

def main():
    ensure_db_folder()
    conn = create_connection(DB_FILE)
    if conn:
        create_schema(conn)
        create_indexes(conn)
        create_triggers(conn)
        create_views(conn)
        conn.close()
        print("База данных успешно создана и настроена.")

if __name__ == '__main__':
    main()
