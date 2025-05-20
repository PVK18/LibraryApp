import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

DB_PATH = "db/library.db"

class BooksForm(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()

        self.books = []
        self.index = 0
        self.current_key = None  # (library_id, book_id)

        self.libraries = []
        self.themes = []

        self.load_libraries()
        self.load_themes()
        self.create_widgets()
        self.load_books()
        self.show_record()

    def create_widgets(self):
        tk.Label(self, text="Библиотека:").grid(row=0, column=0, sticky="e")
        self.library_cb = ttk.Combobox(self, values=[f"{lib[1]} (ID:{lib[0]})" for lib in self.libraries], state="readonly")
        self.library_cb.grid(row=0, column=1, sticky="w")
        self.library_cb.bind("<<ComboboxSelected>>", self.on_library_change)

        tk.Label(self, text="Код книги:").grid(row=1, column=0, sticky="e")
        self.entry_book_id = tk.Entry(self)
        self.entry_book_id.grid(row=1, column=1, sticky="w")

        tk.Label(self, text="Тематика:").grid(row=2, column=0, sticky="e")
        self.theme_cb = ttk.Combobox(self, values=[t[1] for t in self.themes], state="readonly")
        self.theme_cb.grid(row=2, column=1, sticky="w")

        tk.Label(self, text="Автор:").grid(row=3, column=0, sticky="e")
        self.entry_author = tk.Entry(self, width=40)
        self.entry_author.grid(row=3, column=1, columnspan=3, sticky="w")

        tk.Label(self, text="Название:").grid(row=4, column=0, sticky="e")
        self.entry_title = tk.Entry(self, width=40)
        self.entry_title.grid(row=4, column=1, columnspan=3, sticky="w")

        tk.Label(self, text="Издательство:").grid(row=5, column=0, sticky="e")
        self.entry_publisher = tk.Entry(self, width=30)
        self.entry_publisher.grid(row=5, column=1, sticky="w")

        tk.Label(self, text="Место издания:").grid(row=5, column=2, sticky="e")
        self.entry_publish_place = tk.Entry(self, width=20)
        self.entry_publish_place.grid(row=5, column=3, sticky="w")

        tk.Label(self, text="Год издания:").grid(row=6, column=0, sticky="e")
        self.entry_publish_year = tk.Entry(self)
        self.entry_publish_year.grid(row=6, column=1, sticky="w")

        tk.Label(self, text="Количество:").grid(row=6, column=2, sticky="e")
        self.entry_quantity = tk.Entry(self)
        self.entry_quantity.grid(row=6, column=3, sticky="w")

        nav_frame = tk.Frame(self)
        nav_frame.grid(row=7, column=0, columnspan=4, pady=10)
        tk.Button(nav_frame, text="<<", command=self.first_record).pack(side="left")
        tk.Button(nav_frame, text="<", command=self.prev_record).pack(side="left")
        tk.Button(nav_frame, text=">", command=self.next_record).pack(side="left")
        tk.Button(nav_frame, text=">>", command=self.last_record).pack(side="left")

        btn_frame = tk.Frame(self)
        btn_frame.grid(row=8, column=0, columnspan=4, pady=10)
        tk.Button(btn_frame, text="Добавить", command=self.add_record).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Сохранить", command=self.save_record).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Удалить", command=self.delete_record).pack(side="left", padx=5)

        search_frame = tk.Frame(self)
        search_frame.grid(row=9, column=0, columnspan=4, pady=10)
        tk.Label(search_frame, text="Поиск по названию:").pack(side="left")
        self.search_title = tk.Entry(search_frame, width=20)
        self.search_title.pack(side="left", padx=5)
        tk.Button(search_frame, text="Найти", command=self.search).pack(side="left")
        tk.Button(search_frame, text="Сбросить фильтр", command=self.load_books).pack(side="left", padx=10)

    def load_libraries(self):
        self.cursor.execute("SELECT library_id, name FROM libraries ORDER BY name")
        self.libraries = self.cursor.fetchall()

    def load_themes(self):
        self.cursor.execute("SELECT theme_id, name FROM themes ORDER BY name")
        self.themes = self.cursor.fetchall()

    def load_books(self, where_clause="", params=()):
        query = """
        SELECT library_id, book_id, theme_id, author, title, publisher, publish_place, publish_year, quantity
        FROM books
        """
        if where_clause:
            query += " WHERE " + where_clause
        query += " ORDER BY title"
        self.cursor.execute(query, params)
        self.books = self.cursor.fetchall()
        self.index = 0
        self.show_record()

    def show_record(self):
        if not self.books:
            self.clear_all_entries()
            self.current_key = None
            return
        record = self.books[self.index]
        self.current_key = (record[0], record[1])
        lib_idx = next((i for i, lib in enumerate(self.libraries) if lib[0] == record[0]), 0)
        self.library_cb.current(lib_idx)
        self.entry_book_id.delete(0, tk.END)
        self.entry_book_id.insert(0, str(record[1]))
        theme_idx = next((i for i, t in enumerate(self.themes) if t[0] == record[2]), 0)
        self.theme_cb.current(theme_idx if record[2] is not None else 0)
        self.entry_author.delete(0, tk.END)
        self.entry_author.insert(0, record[3] or "")
        self.entry_title.delete(0, tk.END)
        self.entry_title.insert(0, record[4] or "")
        self.entry_publisher.delete(0, tk.END)
        self.entry_publisher.insert(0, record[5] or "")
        self.entry_publish_place.delete(0, tk.END)
        self.entry_publish_place.insert(0, record[6] or "")
        self.entry_publish_year.delete(0, tk.END)
        self.entry_publish_year.insert(0, str(record[7]) if record[7] else "")
        self.entry_quantity.delete(0, tk.END)
        self.entry_quantity.insert(0, str(record[8]) if record[8] is not None else "0")

    def clear_form(self):
        self.entry_book_id.delete(0, tk.END)
        self.theme_cb.set("")
        self.entry_author.delete(0, tk.END)
        self.entry_title.delete(0, tk.END)
        self.entry_publisher.delete(0, tk.END)
        self.entry_publish_place.delete(0, tk.END)
        self.entry_publish_year.delete(0, tk.END)
        self.entry_quantity.delete(0, tk.END)

    def clear_all_entries(self):
        self.library_cb.set("")
        self.clear_form()

    def add_record(self):
        self.clear_form()
        self.current_key = None
        self.on_library_change(None)

    def get_next_book_id(self, library_id):
        self.cursor.execute("SELECT MAX(book_id) FROM books WHERE library_id=?", (library_id,))
        result = self.cursor.fetchone()
        max_id = result[0] if result and result[0] is not None else 0
        return max_id + 1

    def on_library_change(self, event):
        if self.current_key is None and self.library_cb.get():
            try:
                library_str = self.library_cb.get()
                library_id = int(library_str.split("ID:")[1].rstrip(")"))
                next_id = self.get_next_book_id(library_id)
                self.entry_book_id.delete(0, tk.END)
                self.entry_book_id.insert(0, str(next_id))
            except Exception:
                pass

    def first_record(self):
        if self.books:
            self.index = 0
            self.show_record()

    def last_record(self):
        if self.books:
            self.index = len(self.books) - 1
            self.show_record()

    def next_record(self):
        if self.books and self.index < len(self.books) - 1:
            self.index += 1
            self.show_record()

    def prev_record(self):
        if self.books and self.index > 0:
            self.index -= 1
            self.show_record()

    def save_record(self):
        try:
            library_str = self.library_cb.get()
            if not library_str:
                raise ValueError("Не выбрана библиотека")
            library_id = int(library_str.split("ID:")[1].rstrip(")"))

            book_id = int(self.entry_book_id.get().strip())
            theme_name = self.theme_cb.get()
            theme_id = next((t[0] for t in self.themes if t[1] == theme_name), None)
            author = self.entry_author.get().strip()
            title = self.entry_title.get().strip()
            publisher = self.entry_publisher.get().strip()
            publish_place = self.entry_publish_place.get().strip()
            publish_year_str = self.entry_publish_year.get().strip()
            quantity_str = self.entry_quantity.get().strip()

            if not author or not title:
                raise ValueError("Поля 'Автор' и 'Название' обязательны")

            publish_year = int(publish_year_str) if publish_year_str else None
            quantity = int(quantity_str) if quantity_str else 0
            if quantity < 0:
                raise ValueError("Количество не может быть отрицательным")
            if publish_year is not None and (publish_year <= 1000 or publish_year > 2100):
                raise ValueError("Неверный год издания")

            self.cursor.execute("SELECT COUNT(*) FROM books WHERE library_id=? AND book_id=?", (library_id, book_id))
            exists = self.cursor.fetchone()[0] > 0

            if exists:
                self.cursor.execute("""
                    UPDATE books SET
                        theme_id=?, author=?, title=?, publisher=?, publish_place=?, publish_year=?, quantity=?
                    WHERE library_id=? AND book_id=?
                """, (theme_id, author, title, publisher, publish_place, publish_year, quantity, library_id, book_id))
            else:
                self.cursor.execute("""
                    INSERT INTO books (library_id, book_id, theme_id, author, title, publisher, publish_place, publish_year, quantity)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (library_id, book_id, theme_id, author, title, publisher, publish_place, publish_year, quantity))

            self.conn.commit()
            self.load_books()
            messagebox.showinfo("Успех", "Данные сохранены.")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def delete_record(self):
        if self.current_key is None:
            messagebox.showwarning("Внимание", "Нет записи для удаления.")
            return
        if messagebox.askyesno("Подтверждение", "Удалить текущую запись?"):
            self.cursor.execute("DELETE FROM books WHERE library_id=? AND book_id=?", self.current_key)
            self.conn.commit()
            self.load_books()

    def search(self):
        title = self.search_title.get().strip()
        if title:
            where = "title LIKE ?"
            param = ('%' + title + '%',)
            self.load_books(where, param)
        else:
            self.load_books()

# Блок запуска
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Книги")
    form = BooksForm(root)
    form.pack(padx=10, pady=10)
    root.mainloop()
