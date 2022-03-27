from io import BytesIO
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog as fd
import tkinterDnD
from PIL import Image, ImageTk
import requests
import validators
import pytesseract as tess
tess.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def expand2square(pil_img, background_color):
    """Функция для расширения картинки до квадрата, заполняя недостающие края цветом background_color"""
    width, height = pil_img.size
    if width == height:
        return pil_img
    elif width > height:
        result = Image.new(pil_img.mode, (width, width), background_color)
        result.paste(pil_img, (0, (width - height) // 2))
        return result
    else:
        result = Image.new(pil_img.mode, (height, height), background_color)
        result.paste(pil_img, ((height - width) // 2, 0))
        return result


class App(object):
    """
    Окно приложения
    """

    def __init__(self, root):
        self.main = root
        self.main.title("Text recognition")
        self.main.rowconfigure(0, minsize=480, weight=1)
        self.main.columnconfigure(0, minsize=480, weight=1)
        self.main.columnconfigure(1, minsize=400, weight=1)
        self.image_fr = tk.Frame(self.main)
        self.text_fr = tk.Frame(self.main, bg="#FFFFFF")

        # расположение основных фреймов
        self.image_fr.grid(row=0, column=0, sticky="nsew")
        self.text_fr.grid(row=0, column=1, sticky="nsew")

        # поле с текстом:
        self.rec_txt = tk.Text(self.text_fr)
        self.rec_txt.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # поле с картинкой
        self.image_cnv = tk.Canvas(
            self.image_fr, width=480, height=480, background="black")
        self.image_cnv.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # кнопка выбора картинки
        self.select_btn = tk.Button(
            self.main, text="Обзор", command=self.select_file)
        self.select_btn.grid(row=1, column=0, sticky="nsew")

        # настройка drop'a
        self.image_fr.register_drop_target("*")
        self.image_fr.bind("<<Drop>>", self.drop)

        # путь к выбранному файлу, по умолчанию стоит "draganddrop.gif"
        self.image_path = "draganddrop.gif"
        self.update_image(True)

    def select_file(self):
        """Выбор файла через окошко"""
        self.image_path = fd.askopenfilename()
        self.update_image()

    def drop(self, event):
        """Обработка файла который дропнули в окошко"""
        self.image_path = event.data

        if validators.url(self.image_path):
            # Если ссылка
            print(f"URL: {self.image_path}")
            self.image_path = BytesIO(requests.get(self.image_path).content)
        else:
            # Если файл на компьютере, то надо убрать { }
            self.image_path = self.image_path[1:-1]
        self.update_image()

    def update_image(self, silent=False):
        """Обработка и обновление картинки и запуск распознавания"""
        try:
            # Загрузка картинки
            img = Image.open(self.image_path)
            img = img.convert('RGB')
            # сохраняем картинку для распознавания
            self.base_img = img
            # подстраиваем картинку под размер окошка
            img = expand2square(img, (0, 0, 0))
            resized_image = img.resize((480, 480), Image.ANTIALIAS)
            # обновляем картинку в окошке
            self.image = ImageTk.PhotoImage(resized_image)
            self.image_cnv.create_image(0, 0, image=self.image, anchor=tk.NW)
            # запускаем распознавание
            self.recognise_image()
        except Exception as er:
            print(er)
            if not silent:
                messagebox.showerror("Ошибка", "Не получилось открыть файл!")

    def recognise_image(self):
        """Распознавание картинки"""
        text = tess.image_to_string(self.base_img, lang='rus+eng')
        self.rec_txt.delete("1.0", 'end')
        self.rec_txt.insert('1.0', text)


if __name__ == "__main__":
    # Важно использовать именно tkinterDnD чтобы работал drag and drop
    root = tkinterDnD.Tk()
    app = App(root)
    root.mainloop()
