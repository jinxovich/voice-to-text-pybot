import g4f
from config import SUMMARY_STYLES


async def generate_summary(text: str, style_key: str) -> str:
    # Получаем стиль по ключу или используем "default"
    style = SUMMARY_STYLES.get(style_key, SUMMARY_STYLES["default"])
    system_prompt = style["prompt"]

    # Формируем диалог для модели
    conversation = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text}
    ]

    try:
        # Запрашиваем ответ от модели
        raw_response = await g4f.ChatCompletion.create_async(
            model  = g4f.models.gpt_4o_mini,
            messages = conversation,
            stream = False
        )

        # Проверяем ответ
        if raw_response and isinstance(raw_response, str) and raw_response.strip():
            return raw_response.strip()
        else:
            return "Ошибка: пустой ответ"

    except Exception as error:
        return f"Не удалось получить ответ: {str(error)}"