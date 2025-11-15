import cv2
import numpy as np

# 👉 сюда вставь свой URL, который работает в браузере, но с /video в конце
URL = "http://10.232.75.139:8080/video"  # <-- сюда свой URL с /video

def main():
    cap = cv2.VideoCapture(URL)

    if not cap.isOpened():
        print("❌ Не удалось открыть поток. Проверь URL.")
        return

    # HSV-диапазон для красного (можно подстроить)
    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])

    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])

    cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
    cv2.namedWindow("mask", cv2.WINDOW_NORMAL)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠ Кадр не прочитан.")
            break

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # маска красного
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = mask1 | mask2

        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        target_center = None

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 500:  # отсекаем мелкий шум
                continue

            x, y, w, h = cv2.boundingRect(cnt)
            cx = x + w // 2
            cy = y + h // 2
            target_center = (cx, cy)

            # рисуем рамку и точку
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)
            cv2.putText(frame, f"({cx},{cy})", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        if target_center is not None:
            print("Центр объекта (пиксели):", target_center, end="\r")

        cv2.imshow("frame", frame)
        cv2.imshow("mask", mask)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
