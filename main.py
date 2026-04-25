python
import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os
from datetime import datetime

# ========== КЛАСС ПРИЛОЖЕНИЯ ==========
class QuoteGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Quote Generator")
        self.root.geometry("700x600")
        self.root.resizable(True, True)

        # Загрузка данных
        self.quotes = []          # Список цитат: {"text": ..., "author": ..., "topic": ...}
        self.history = []         # Список индексов сгенерированных цитат
        self.data_file = "quotes.json"
        self.load_data()

        # UI элементы
        self.create_widgets()
        self.update_quote_display()

    # ========== ЗАГРУЗКА / СОХРАНЕНИЕ ДАННЫХ ==========
    def load_data(self):
        """Загружает цитаты и историю из JSON файла"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.quotes = data.get("quotes", [])
                    self.history = data.get("history", [])
            except:
                messagebox.showerror("Ошибка", "Не удалось загрузить данные. Используются стандартные цитаты.")
                self.set_default_quotes()
        else:
            self.set_default_quotes()

    def set_default_quotes(self):
        """Предопределённые цитаты (текст, автор, тема)"""
        self.quotes = [
            {"text": "Жизнь — это то, что с тобой происходит, пока ты строишь планы.", "author": "Джон Леннон", "topic": "Жизнь"},
            {"text": "Будь изменением, которое ты хочешь видеть в мире.", "author": "Махатма Ганди", "topic": "Мотивация"},
            {"text": "Тот, кто может, делает. Тот, кто не может, критикует.", "author": "Дейл Карнеги", "topic": "Успех"},
            {"text": "В двух словах: будьте лучшей версией себя.", "author": "Стив Джобс", "topic": "Самосовершенствование"},
            {"text": "Не бойся ошибок — бойся бездействия.", "author": "Роберт Кийосаки", "topic": "Финансы"},
            {"text": "Читайте — это лучшее учение.", "author": "А.С. Пушкин", "topic": "Образование"},
            {"text": "Всё гениальное просто.", "author": "Альберт Эйнштейн", "topic": "Наука"},
        ]
        self.history = []

    def save_data(self):
        """Сохраняет цитаты и историю в JSON"""
        data = {
            "quotes": self.quotes,
            "history": self.history
        }
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # ========== UI СОЗДАНИЕ ==========
    def create_widgets(self):
        # Основной фрейм
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Область отображения цитаты ---
        self.quote_frame = tk.LabelFrame(main_frame, text="Текущая цитата", font=("Arial", 12, "bold"))
        self.quote_frame.pack(fill=tk.X, pady=5)

        self.lbl_quote_text = tk.Label(self.quote_frame, text="", wraplength=650, font=("Georgia", 12), justify="left")
        self.lbl_quote_text.pack(pady=10, padx=10)

        self.lbl_quote_author = tk.Label(self.quote_frame, text="", font=("Arial", 10, "italic"), fg="gray")
        self.lbl_quote_author.pack(pady=(0,10))

        # --- Кнопка генерации ---
        self.btn_generate = tk.Button(main_frame, text="🎲 Сгенерировать цитату", command=self.generate_random_quote,
                                      font=("Arial", 11), bg="#4CAF50", fg="white", padx=10, pady=5)
        self.btn_generate.pack(pady=10)

        # --- Фильтры ---
        filter_frame = tk.LabelFrame(main_frame, text="Фильтрация", font=("Arial", 10, "bold"))
        filter_frame.pack(fill=tk.X, pady=5)

        # По автору
        tk.Label(filter_frame, text="Автор:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.author_var = tk.StringVar()
        self.author_combo = ttk.Combobox(filter_frame, textvariable=self.author_var, width=30)
        self.author_combo.grid(row=0, column=1, padx=5, pady=5)
        self.update_author_list()
        self.author_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        # По теме
        tk.Label(filter_frame, text="Тема:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.topic_var = tk.StringVar()
        self.topic_combo = ttk.Combobox(filter_frame, textvariable=self.topic_var, width=20)
        self.topic_combo.grid(row=0, column=3, padx=5, pady=5)
        self.update_topic_list()
        self.topic_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        # Кнопка сброса фильтров
        self.btn_reset_filters = tk.Button(filter_frame, text="Сбросить фильтры", command=self.reset_filters,
                                           bg="#f0f0f0")
        self.btn_reset_filters.grid(row=0, column=4, padx=10, pady=5)

        # --- История ---
        history_frame = tk.LabelFrame(main_frame, text="История цитат", font=("Arial", 10, "bold"))
        history_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Список истории с прокруткой
        self.listbox_history = tk.Listbox(history_frame, height=10)
        scrollbar = tk.Scrollbar(history_frame, orient="vertical", command=self.listbox_history.yview)
        self.listbox_history.configure(yscrollcommand=scrollbar.set)
        self.listbox_history.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # --- Добавление новой цитаты ---
        add_frame = tk.LabelFrame(main_frame, text="Добавить новую цитату", font=("Arial", 10, "bold"))
        add_frame.pack(fill=tk.X, pady=5)

        tk.Label(add_frame, text="Текст:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_text = tk.Entry(add_frame, width=50)
        self.entry_text.grid(row=0, column=1, padx=5, pady=5, columnspan=2)

        tk.Label(add_frame, text="Автор:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_author = tk.Entry(add_frame, width=25)
        self.entry_author.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(add_frame, text="Тема:").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.entry_topic = tk.Entry(add_frame, width=20)
        self.entry_topic.grid(row=1, column=3, padx=5, pady=5)

        self.btn_add = tk.Button(add_frame, text="➕ Добавить", command=self.add_quote, bg="#2196F3", fg="white")
        self.btn_add.grid(row=1, column=4, padx=10, pady=5)

        # Обновление истории в UI
        self.update_history_display()

    def update_author_list(self):
        """Обновляет список авторов в фильтре"""
        authors = sorted(set(q["author"] for q in self.quotes))
        self.author_combo["values"] = [""] + authors

    def update_topic_list(self):
        """Обновляет список тем в фильтре"""
        topics = sorted(set(q["topic"] for q in self.quotes))
        self.topic_combo["values"] = [""] + topics

    def apply_filters(self):
        """Применяет фильтры и генерирует случайную цитату из отфильтрованных"""
        filtered = self.quotes[:]
        author = self.author_var.get().strip()
        topic = self.topic_var.get().strip()

        if author:
            filtered = [q for q in filtered if q["author"] == author]
        if topic:
            filtered = [q for q in filtered if q["topic"] == topic]

        if filtered:
            quote = random.choice(filtered)
            self.display_quote(quote)
        else:
            self.lbl_quote_text.config(text="Нет цитат с такими фильтрами.")
            self.lbl_quote_author.config(text="")

    def reset_filters(self):
        """Сбрасывает фильтры"""
        self.author_var.set("")
        self.topic_var.set("")
        self.apply_filters()

    def generate_random_quote(self):
        """Выбирает случайную цитату из всех и добавляет в историю"""
        if not self.quotes:
            messagebox.showwarning("Нет цитат", "Добавьте хотя бы одну цитату!")
            return

        quote = random.choice(self.quotes)
        self.display_quote(quote)

        # Добавление в историю (сохраняем индекс)
        idx = self.quotes.index(quote)
        self.history.append(idx)
        self.save_data()
        self.update_history_display()

    def display_quote(self, quote):
        """Отображает цитату на экране"""
        self.lbl_quote_text.config(text=f"❝ {quote['text']} ❞")
        self.lbl_quote_author.config(text=f"— {quote['author']} (Тема: {quote['topic']})")

    def update_quote_display(self):
        """Обновляет отображение, если есть история"""
        if self.history and self.history[-1] < len(self.quotes):
            self.display_quote(self.quotes[self.history[-1]])
        else:
            self.lbl_quote_text.config(text="Нажмите 'Сгенерировать цитату'")
            self.lbl_quote_author.config(text="")

    def update_history_display(self):
        """Обновляет список истории"""
        self.listbox_history.delete(0, tk.END)
        for idx in self.history[-20:]:  # Показываем последние 20
            if idx < len(self.quotes):
                q = self.quotes[idx]
                self.listbox_history.insert(tk.END, f"{q['author']}: {q['text'][:60]}...")

    def add_quote(self):
        """Добавляет новую цитату с проверкой ввода"""
        text = self.entry_text.get().strip()
        author = self.entry_author.get().strip()
        topic = self.entry_topic.get().strip()

        # Проверка на пустые строки
        if not text:
            messagebox.showerror("Ошибка", "Текст цитаты не может быть пустым!")
            return
        if not author:
            messagebox.showerror("Ошибка", "Автор не может быть пустым!")
            return
        if not topic:
            messagebox.showerror("Ошибка", "Тема не может быть пустой!")
            return

        # Добавление
        new_quote = {"text": text, "author": author, "topic": topic}
        self.quotes.append(new_quote)
        self.save_data()

        # Очистка полей
        self.entry_text.delete(0, tk.END)
        self.entry_author.delete(0, tk.END)
        self.entry_topic.delete(0, tk.END)

        # Обновление фильтров и списков
        self.update_author_list()
        self.update_topic_list()
        self.update_history_display()

        messagebox.showinfo("Успех", "Цитата добавлена!")


# ========== ЗАПУСК ==========
if __name__ == "__main__":
    root = tk.Tk()
    app = QuoteGenerator(root)
    root.mainloop()
