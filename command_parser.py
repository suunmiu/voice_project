# command_parser.py

def parse_command(text: str):
    text = text.lower()

    # команды подачи (подать бутылку, дай бутылку, принеси бутылку)
    if any(word in text for word in ["бутыл", "вода", "бутылку"]):
        return "GIVE_BOTTLE"

    # кубик
    if "куб" in text:
        # проверяем цвет, если есть
        if "красн" in text:
            return "GIVE_RED_CUBE"
        if "син" in text:
            return "GIVE_BLUE_CUBE"
        # просто куб
        return "GIVE_CUBE"

    # телефон
    if "телефон" in text:
        return "GIVE_PHONE"

    # поднеси к руке
    if any(word in text for word in ["руке", "ладон", "дай в руку"]):
        return "MOVE_TO_HAND"

    # положи обратно
    if any(word in text for word in ["положи", "верни", "убери"]):
        return "PUT_BACK"

    return "UNKNOWN"
