from ultralytics import YOLO
import cv2

# поток с IP Webcam
URL = "http://192.168.1.253:8080/video"  # подставь свой IP, тот же что уже работал

def main():
    # маленькая модель YOLOv8n, в ней есть класс "bottle"
    model = YOLO("yolov8n.pt")

    cap = cv2.VideoCapture(URL)
    if not cap.isOpened():
        print("❌ Не удалось открыть поток")
        return

    print("✔ Ищу бутылку... Нажми 'q' для выхода")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠ Кадр не прочитан")
            break

        # детекция
        results = model(frame)

        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                label = model.names[cls_id]

                # интересует только бутылка
                if label != "bottle":
                    continue

                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2

                # рисуем рамку и центр
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)
                cv2.putText(frame, f"bottle ({cx},{cy})", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                print(f"\rБутылка: центр в пикселях ({cx}, {cy})", end="")

        cv2.imshow("Bottle finder", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    print("\nЗавершено.")
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
