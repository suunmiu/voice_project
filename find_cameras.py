import cv2

for i in range(6):
    print(f"Пробую камеру {i}...")
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"✅ Камера {i} доступна!")
        cap.release()
    else:
        print(f"❌ Камера {i} недоступна")
