import cv2

URL = "http://10.232.75.139:8080/video"   # поменяй IP

cap = cv2.VideoCapture(URL)

if not cap.isOpened():
    print("❌ Не удалось открыть поток.")
    exit()

print("✔ Видео поток открыт!")

while True:
    ret, frame = cap.read()
    if not ret:
        print("⚠ Кадр не прочитан")
        break

    cv2.imshow("IP Camera Test", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
