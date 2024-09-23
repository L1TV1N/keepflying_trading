import cv2
import numpy as np
import logging
import time
from PIL import ImageGrab
import pyautogui
import pytesseract
import keyboard  # Для отслеживания нажатия клавиш

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Загружаем координаты из файла calibration_results.py
def load_calibration_data():
    try:
        with open('calibration_results.py', 'r') as f:
            calibration_code = f.read()
            exec(calibration_code, globals())
            logging.info("Координаты успешно загружены из calibration_results.py")
    except FileNotFoundError:
        logging.error("Файл calibration_results.py не найден.")
    except Exception as e:
        logging.error(f"Ошибка при загрузке координат: {e}")

# Порог для принятия решения (210%)
decision_threshold = 210

# Пути к изображению таймера (например, когда осталось 6 секунд)
timer_images = {
    6: 'timer_6.png',
    5: 'timer_5.png',
}

is_running = False  # Флаг для управления ботом


def capture_region(x1, y1, x2, y2):
    """Захватываем экран в области с указанными координатами."""
    screen = ImageGrab.grab(bbox=(x1, y1, x2, y2))
    screen_np = np.array(screen)
    return cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)


def load_timer_image(timer_value):
    """Загружает эталонное изображение таймера."""
    if timer_value in timer_images:
        return cv2.imread(timer_images[timer_value], cv2.IMREAD_GRAYSCALE)
    return None


def match_timer_with_image(timer_image):
    """Сравнивает текущее изображение таймера с эталонным."""
    current_timer = capture_region(*timer_coords)
    current_gray = cv2.cvtColor(current_timer, cv2.COLOR_BGR2GRAY)

    result = cv2.matchTemplate(current_gray, timer_image, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(result)

    logging.info(f"Совпадение таймера: {max_val:.2f}")

    return max_val > 0.8


def preprocess_for_ocr(image):
    """Улучшение изображения для OCR: делаем его черно-белым и повышаем контраст."""
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary_image = cv2.threshold(gray_image, 120, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary_image


def extract_text_from_region(x1, y1, x2, y2):
    """Распознавание текста в области с помощью Tesseract."""
    screen = capture_region(x1, y1, x2, y2)
    processed_image = preprocess_for_ocr(screen)
    text = pytesseract.image_to_string(processed_image, config='--psm 7')
    return text.strip()


def click_button(x, y):
    """Нажатие кнопки по координатам."""
    pyautogui.click(x, y)


def bot_logic():
    logging.info("Запуск бота...")
    try:
        while True:
            # Проверяем, запущен ли бот
            if not is_running:
                time.sleep(1)
                continue

            timer_image = load_timer_image(6)
            if timer_image is None:
                logging.error("Изображение таймера для 6 секунд не найдено.")
                time.sleep(1)
                continue

            if match_timer_with_image(timer_image):
                logging.info("Таймер показывает 6 секунд. Принятие решения!")

                red_text = extract_text_from_region(*red_area_coords)
                try:
                    red_percent = int(red_text.replace('%', '').replace(' ', ''))
                except ValueError:
                    logging.error(f"Ошибка распознавания красного процента: '{red_text}'")
                    red_percent = 0

                green_text = extract_text_from_region(*green_area_coords)
                try:
                    green_percent = int(green_text.replace('%', '').replace(' ', ''))
                except ValueError:
                    logging.error(f"Ошибка распознавания зеленого процента: '{green_text}'")
                    green_percent = 0

                logging.info(f"Красный процент: {red_percent}%, Зеленый процент: {green_percent}%")

                if red_percent > decision_threshold:
                    logging.info("Красный процент выше порога. Нажатие на красную кнопку.")
                    click_button(*red_button_coords)
                elif green_percent > decision_threshold:
                    logging.info("Зеленый процент выше порога. Нажатие на зеленую кнопку.")
                    click_button(*green_button_coords)
                else:
                    logging.info("Проценты ниже порога. Ожидание следующего раунда.")
            else:
                logging.info("Таймер не совпадает с 6 секундами, продолжаем ожидание.")

            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Остановка бота")


def toggle_bot():
    """Функция для включения/выключения работы бота."""
    global is_running
    if is_running:
        logging.info("Остановка бота по нажатию 'S'.")
        is_running = False
    else:
        logging.info("Запуск бота по нажатию 'S'.")
        is_running = True


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    load_calibration_data()  # Загрузка координат перед запуском

    # Отслеживаем нажатие клавиши 'S' для старта/остановки
    keyboard.add_hotkey('s', toggle_bot)

    # Запуск основной логики
    bot_logic()
