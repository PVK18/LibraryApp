import tkinter as tk
from tkinter import messagebox
import sqlite3

DB_PATH = "../db/library.db"

class ReadersForm(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()

        self.current_id = None
        self.readers = []
        self.index = 0

        self.create_widgets()
        self.load_readers()
        self.show_record()

    def create_widgets(self):
        tk.Label(self, text="ФИО:").grid(row=0, column=0, sticky="e")
        self.entry_name = tk.Entry(self, width=40)
        self.entry_name.grid(row=0, column=1, columnspan=3, sticky="w")

        tk.Label(self, text="Адрес:").grid(row=1, column=0, sticky="e")
        self.entry_address = tk.Entry(self, width=40)
        self.entry_address.grid(row=1, column=1, columnspan=3, sticky="w")

        tk.Label(self, text="Телефон:").grid(row=2, column=0, sticky="e")
        self.entry_phone = tk.Entry(self, width=20)
        self.entry_phone.grid(row=2, column=1, sticky="w")

        nav_frame = tk.Frame(self)
        nav_frame.grid(row=3, column=0, columnspan=4, pady=10)
        tk.Button(nav_frame, text="<<", command=self.first_record).pack(side="left")
        tk.Button(nav_frame, text="<", command=self.prev_record).pack(side="left")
        tk.Button(nav_frame, text=">", command=self.next_record).pack(side="left")
        tk.Button(nav_frame, text=">>", command=self.last_record).pack(side="left")

        btn_frame = tk.Frame(self)
        btn_frame.grid(row=4, column=0, columnspan=4, pady=10)
        tk.Button(btn_frame, text="Добавить", command=self.add_record).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Сохранить", command=self.save_record).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Удалить", command=self.delete_record).pack(side="left", padx=5)

        search_frame = tk.Frame(self)
        search_frame.grid(row=5, column=0, columnspan=4, pady=10)
        tk.Label(search_frame, text="Поиск по ФИО:").pack(side="left")
        self.search_name = tk.Entry(search_frame, width=20)
        self.search_name.pack(side="left", padx=5)
        tk.Button(search_frame, text="Найти", command=self.search).pack(side="left")
        tk.Button(search_frame, text="Сбросить фильтр", command=self.load_readers).pack(side="left", padx=10)

    def load_readers(self, where_clause="", params=()):
        query = "SELECT reader_id, full_name, address, phone FROM readers"
        if where_clause:
            query += " WHERE " + where_clause
        query += " ORDER BY full_name"
        self.cursor.execute(query, params)
        self.readers = self.cursor.fetchall()
        self.index = 0
        self.show_record()

    def show_record(self):
        if not self.readers:
            self.clear_entries()
            self.current_id = None
            return
        record = self.readers[self.index]
        self.current_id = record[0]
        self.entry_name.delete(0, tk.END)
        self.entry_name.insert(0, record[1])
        self.entry_address.delete(0, tk.END)
        self.entry_address.insert(0, record[2] or "")
        self.entry_phone.delete(0, tk.END)
        self.entry_phone.insert(0, record[3] or "")

    def clear_entries(self):
        self.entry_name.delete(0, tk.END)
        self.entry_address.delete(0, tk.END)
        self.entry_phone.delete(0, tk.END)

    def first_record(self):
        if self.readers:
            self.index = 0
            self.show_record()

    def last_record(self):
        if self.readers:
            self.index = len(self.readers) - 1
            self.show_record()

    def next_record(self):
        if self.readers and self.index < len(self.readers) - 1:
            self.index += 1
            self.show_record()

    def prev_record(self):
        if self.readers and self.index > 0:
            self.index -= 1
            self.show_record()

    def add_record(self):
        self.clear_entries()
        self.current_id = None

    def save_record(self):
        name = self.entry_name.get().strip()
        address = self.entry_address.get().strip()
        phone = self.entry_phone.get().strip()

        if not name:
            messagebox.showerror("Ошибка", "ФИО не может быть пустым.")
            return

        try:
            if self.current_id is None:
                self.cursor.execute(
                    "INSERT INTO readers (full_name, address, phone) VALUES (?, ?, ?)",
                    (name, address, phone))
            else:
                self.cursor.execute(
                    "UPDATE readers SET full_name=?, address=?, phone=? WHERE reader_id=?",
                    (name, address, phone, self.current_id))
            self.conn.commit()
            self.load_readers()
            messagebox.showinfo("Успех", "Данные сохранены.")
        except sqlite3.IntegrityError as e:
            messagebox.showerror("Ошибка базы данных", str(e))

    def delete_record(self):
        if self.current_id is None:
            messagebox.showwarning("Внимание", "Нет записи для удаления.")
            return

        if messagebox.askyesno("Подтверждение", "Удалить текущую запись?"):
            self.cursor.execute("DELETE FROM readers WHERE reader_id=?", (self.current_id,))
            self.conn.commit()
            self.load_readers()

    def search(self):
        name = self.search_name.get().strip()
        if name:
            where = "full_name LIKE ?"
            param = ('%' + name + '%',)
            self.load_readers(where, param)
        else:
            self.load_readers()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Читатели")
    form = ReadersForm(root)
    form.pack(padx=10, pady=10)
    root.mainloop()
