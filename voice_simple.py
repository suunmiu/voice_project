import sounddevice as sd
import vosk
import json
from command_parser import parse_command


MODEL_PATH = r"C:\Users\111\Downloads\vosk-model-small-ru-0.22 (1)\vosk-model-small-ru-0.22"  # путь к модели
SAMPLE_RATE = 16000

def main():
    print("Загружаю модель Vosk...")
    model = vosk.Model(MODEL_PATH)
    recognizer = vosk.KaldiRecognizer(model, SAMPLE_RATE)

    print("Готово! Говори в микрофон. (Ctrl+C чтобы выйти)\n")

    def callback(indata, frames, time, status):
        if status:
            print(status, flush=True)

        # конвертируем в bytes, чтобы не было ошибки CFFI
        data_bytes = bytes(indata)

        if recognizer.AcceptWaveform(data_bytes):
            result = recognizer.Result()
            data = json.loads(result)
            text = data.get("text", "").strip()
            if text:
                cmd = parse_command(text)
                print(f"Распознано: {text} → Команда: {cmd}")


    with sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        blocksize=8000,
        dtype='int16',
        channels=1,
        callback=callback
    ):
        try:
            while True:
                sd.sleep(100)
        except KeyboardInterrupt:
            print("\nВыход.")

if __name__ == "__main__":
    main()
