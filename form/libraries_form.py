import tkinter as tk
from tkinter import messagebox
import sqlite3

DB_PATH = "../db/library.db"

class LibrariesForm(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()

        self.current_id = None
        self.libraries = []
        self.index = 0

        self.create_widgets()
        self.load_libraries()
        self.show_record()

    def create_widgets(self):
        tk.Label(self, text="Наименование:").grid(row=0, column=0, sticky="e")
        self.entry_name = tk.Entry(self, width=40)
        self.entry_name.grid(row=0, column=1, columnspan=3, sticky="w")

        tk.Label(self, text="Адрес:").grid(row=1, column=0, sticky="e")
        self.entry_address = tk.Entry(self, width=40)
        self.entry_address.grid(row=1, column=1, columnspan=3, sticky="w")

        nav_frame = tk.Frame(self)
        nav_frame.grid(row=2, column=0, columnspan=4, pady=10)
        tk.Button(nav_frame, text="<<", command=self.first_record).pack(side="left")
        tk.Button(nav_frame, text="<", command=self.prev_record).pack(side="left")
        tk.Button(nav_frame, text=">", command=self.next_record).pack(side="left")
        tk.Button(nav_frame, text=">>", command=self.last_record).pack(side="left")

        btn_frame = tk.Frame(self)
        btn_frame.grid(row=3, column=0, columnspan=4, pady=10)
        tk.Button(btn_frame, text="Добавить", command=self.add_record).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Сохранить", command=self.save_record).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Удалить", command=self.delete_record).pack(side="left", padx=5)

        search_frame = tk.Frame(self)
        search_frame.grid(row=4, column=0, columnspan=4, pady=10)
        tk.Label(search_frame, text="Поиск по наименованию:").pack(side="left")
        self.search_name = tk.Entry(search_frame, width=20)
        self.search_name.pack(side="left", padx=5)
        tk.Button(search_frame, text="Найти", command=self.search).pack(side="left")
        tk.Button(search_frame, text="Сбросить фильтр", command=self.load_libraries).pack(side="left", padx=10)

    def load_libraries(self, where_clause="", params=()):
        query = "SELECT library_id, name, address FROM libraries"
        if where_clause:
            query += " WHERE " + where_clause
        query += " ORDER BY name"
        self.cursor.execute(query, params)
        self.libraries = self.cursor.fetchall()
        self.index = 0
        self.show_record()

    def show_record(self):
        if not self.libraries:
            self.clear_entries()
            self.current_id = None
            return
        record = self.libraries[self.index]
        self.current_id = record[0]
        self.entry_name.delete(0, tk.END)
        self.entry_name.insert(0, record[1])
        self.entry_address.delete(0, tk.END)
        self.entry_address.insert(0, record[2] or "")

    def clear_entries(self):
        self.entry_name.delete(0, tk.END)
        self.entry_address.delete(0, tk.END)

    def first_record(self):
        if self.libraries:
            self.index = 0
            self.show_record()

    def last_record(self):
        if self.libraries:
            self.index = len(self.libraries) - 1
            self.show_record()

    def next_record(self):
        if self.libraries and self.index < len(self.libraries) - 1:
            self.index += 1
            self.show_record()

    def prev_record(self):
        if self.libraries and self.index > 0:
            self.index -= 1
            self.show_record()

    def add_record(self):
        self.clear_entries()
        self.current_id = None

    def save_record(self):
        name = self.entry_name.get().strip()
        address = self.entry_address.get().strip()

        if not name:
            messagebox.showerror("Ошибка", "Наименование не может быть пустым.")
            return

        try:
            if self.current_id is None:
                self.cursor.execute(
                    "INSERT INTO libraries (name, address) VALUES (?, ?)",
                    (name, address))
            else:
                self.cursor.execute(
                    "UPDATE libraries SET name=?, address=? WHERE library_id=?",
                    (name, address, self.current_id))
            self.conn.commit()
            self.load_libraries()
            messagebox.showinfo("Успех", "Данные сохранены.")
        except sqlite3.IntegrityError as e:
            messagebox.showerror("Ошибка базы данных", str(e))

    def delete_record(self):
        if self.current_id is None:
            messagebox.showwarning("Внимание", "Нет записи для удаления.")
            return

        if messagebox.askyesno("Подтверждение", "Удалить текущую запись?"):
            self.cursor.execute("DELETE FROM libraries WHERE library_id=?", (self.current_id,))
            self.conn.commit()
            self.load_libraries()

    def search(self):
        name = self.search_name.get().strip()
        if name:
            where = "name LIKE ?"
            param = ('%' + name + '%',)
            self.load_libraries(where, param)
        else:
            self.load_libraries()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Библиотеки")
    form = LibrariesForm(root)
    form.pack(padx=10, pady=10)
    root.mainloop()
