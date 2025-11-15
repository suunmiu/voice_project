import json
import time
import threading

import sounddevice as sd
import vosk

import cv2
import numpy as np

# -------- НАСТРОЙКИ --------
SAMPLE_RATE = 16000
MODEL_PATH = r"C:\Users\111\Downloads\vosk-model-small-ru-0.22 (1)\vosk-model-small-ru-0.22"  # путь к модели


# IP-камера с телефона (IP Webcam)
CAM_URL = "http://10.232.75.139:8080/video"  # <-- сюда свой URL с /video

# Глобальная команда от голоса
last_command = None
lock = threading.Lock()


# -------- ПАРСЕР КОМАНД --------
def parse_command(text: str):
    """
    Превращаем фразу в команду.
    Сейчас нас интересует только поиск красного объекта.
    """
    t = text.lower()

    # любые фразы типа "найди/подай/покажи предмет/кубик/красный"
    if any(w in t for w in ["подай", "найди", "покажи", "возьми"]) and \
       any(w in t for w in ["кубик", "предмет", "красн"]):
        return "FIND_RED_OBJECT"

    return "UNKNOWN"


# -------- ГОЛОСОВОЙ МОДУЛЬ --------
def voice_thread():
    global last_command

    print("Загружаю модель Vosk...")
    model = vosk.Model(MODEL_PATH)
    rec = vosk.KaldiRecognizer(model, SAMPLE_RATE)
    print("Голосовой модуль запущен. Говори команды (Ctrl+C чтобы выйти).")

    def callback(indata, frames, time_info, status):
        global last_command
        if status:
            print(status, flush=True)

        data_bytes = bytes(indata)
        if rec.AcceptWaveform(data_bytes):
            result = rec.Result()
            j = json.loads(result)
            text = j.get("text", "").strip()
            if text:
                cmd = parse_command(text)
                print(f'\n[VOICE] "{text}" -> команда: {cmd}')
                if cmd != "UNKNOWN":
                    with lock:
                        last_command = cmd

    with sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        blocksize=8000,
        dtype="int16",
        channels=1,
        callback=callback,
    ):
        # просто держим поток живым
        while True:
            sd.sleep(100)


# -------- ПОИСК КРАСНОГО ОБЪЕКТА КАМЕРОЙ --------
def find_red_object():
    print("[CAM] Открываю поток камеры...")
    cap = cv2.VideoCapture(CAM_URL)

    if not cap.isOpened():
        print("❌ [CAM] Не удалось открыть поток. Проверь CAM_URL и IP Webcam.")
        return

    # Диапазон красного в HSV
    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])

    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])

    cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
    cv2.namedWindow("mask", cv2.WINDOW_NORMAL)

    found_any = False
    last_center = None

    print("[CAM] Ищу красный объект... Нажми 'q' чтобы выйти из режима камеры.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠ [CAM] Кадр не прочитан.")
            break

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = mask1 | mask2

        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 500:
                continue

            x, y, w, h = cv2.boundingRect(cnt)
            cx = x + w // 2
            cy = y + h // 2
            last_center = (cx, cy)
            found_any = True

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)
            cv2.putText(frame, f"({cx},{cy})", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        if found_any and last_center is not None:
            print(f"\r[CAM] Центр объекта (пиксели): {last_center}", end="")

        cv2.imshow("frame", frame)
        cv2.imshow("mask", mask)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            print("\n[CAM] Пользователь закрыл режим камеры.")
            break

    cap.release()
    cv2.destroyAllWindows()

    if found_any and last_center is not None:
        print(f"[CAM] Итоговые координаты объекта: {last_center}")
    else:
        print("[CAM] Объект не найден.")


# -------- MAIN --------
def main():
    global last_command

    # запускаем голосовой поток в отдельном потоке
    t = threading.Thread(target=voice_thread, daemon=True)
    t.start()

    print("=== Система запущена ===")
    print("Скажи, например: 'подай красный кубик' или 'найди красный предмет'.")
    print("Когда команда распознана, включится камера и будет искать объект.\n")

    try:
        while True:
            time.sleep(0.1)
            with lock:
                cmd = last_command
                last_command = None

            if cmd == "FIND_RED_OBJECT":
                print("\n[SYS] Получена команда FIND_RED_OBJECT → запускаю камеру.")
                find_red_object()
                print("[SYS] Возврат в режим ожидания голосовых команд.")

    except KeyboardInterrupt:
        print("\n[SYS] Выход по Ctrl+C.")


if __name__ == "__main__":
    main()
