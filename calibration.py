import tkinter as tk
from tkinter import messagebox
import pyautogui
import time


class CalibrationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Калибровка координат")
        self.root.geometry("400x400")

        # Создаем метки и кнопки для каждой области
        self.create_widgets()

        # Для хранения координат
        self.coordinates = {}

    def create_widgets(self):
        tk.Label(self.root, text="Нажмите на кнопку для калибровки").pack(pady=10)

        self.red_button = tk.Button(self.root, text="Калибровать Красную Область",
                                    command=lambda: self.calibrate("red_area"))
        self.red_button.pack(pady=10)

        self.green_button = tk.Button(self.root, text="Калибровать Зеленую Область",
                                      command=lambda: self.calibrate("green_area"))
        self.green_button.pack(pady=10)

        self.timer_button = tk.Button(self.root, text="Калибровать Область Таймера",
                                      command=lambda: self.calibrate("timer"))
        self.timer_button.pack(pady=10)

        self.red_click_button = tk.Button(self.root, text="Калибровать Красную Кнопку",
                                          command=lambda: self.calibrate("red_button"))
        self.red_click_button.pack(pady=10)

        self.green_click_button = tk.Button(self.root, text="Калибровать Зеленую Кнопку",
                                            command=lambda: self.calibrate("green_button"))
        self.green_click_button.pack(pady=10)

        # Кнопка для завершения калибровки (салатовый цвет)
        self.done_button = tk.Button(self.root, text="Завершить калибровку", command=self.finish_calibration,
                                     bg="#98FB98", fg="black")
        self.done_button.pack(pady=20)

        # Кнопка для сохранения результата (зелёный цвет)
        self.save_button = tk.Button(self.root, text="Сохранить результат", command=self.save_results, bg="green",
                                     fg="white")
        self.save_button.pack(pady=10)

    def calibrate(self, area_name):
        # Сообщаем пользователю, что нужно выбрать точку
        messagebox.showinfo("Инструкция", f"Пожалуйста, наведите курсор на {area_name} и нажмите 'OK'.")

        # Ожидание перед захватом координат
        time.sleep(3)
        x1, y1 = pyautogui.position()
        messagebox.showinfo("Инструкция", f"Теперь наведите на противоположный угол {area_name} и нажмите 'OK'.")

        time.sleep(3)
        x2, y2 = pyautogui.position()

        # Сохранение координат
        self.coordinates[area_name] = (x1, y1, x2, y2)
        messagebox.showinfo("Готово", f"Координаты для {area_name} сохранены!")

    def finish_calibration(self):
        # Выводим координаты
        result_text = "Калибровка завершена. Вот сохраненные координаты:\n"
        for area, coords in self.coordinates.items():
            result_text += f"{area}: {coords}\n"

        messagebox.showinfo("Результаты", result_text)

        # # Закрываем окно
        # self.root.quit()

    def save_results(self):
        # Создаем строку для сохранения в формате, который вы указали
        result_text = (
            f"# Координаты областей экрана\n"
            f"red_area_coords = {self.coordinates.get('red_area', '(не калибровано)')}  # Область красного процента\n"
            f"green_area_coords = {self.coordinates.get('green_area', '(не калибровано)')}  # Область зеленого процента\n"
            f"timer_coords = {self.coordinates.get('timer', '(не калибровано)')}  # Область таймера\n\n"
            f"# Координаты кнопок\n"
            f"red_button_coords = {self.coordinates.get('red_button', '(не калибровано)')}  # Координаты для нажатия на красную кнопку\n"
            f"green_button_coords = {self.coordinates.get('green_button', '(не калибровано)')}  # Координаты для нажатия на зеленую кнопку\n"
        )

        # Сохраняем результат в файл
        with open("calibration_results.py", "w") as file:
            file.write(result_text)

        messagebox.showinfo("Сохранение", "Координаты успешно сохранены в файл 'calibration_results.py'!")


# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = CalibrationApp(root)
    root.mainloop()
