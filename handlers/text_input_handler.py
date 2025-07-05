import logging

from aiogram import F, Router, types
from aiogram.utils.markdown import hbold

from config import (
    MAX_MESSAGE_LENGTH,
    SUMMARY_DISPLAY_CHUNK_SIZE,
    SUMMARY_STYLES
)
from handlers.common_handlers import get_user_settings
from services.summarization import generate_summary


logger = logging.getLogger(__name__)
router = Router()

logger.info("text_input_handler.router создан.")


# Обработчик текстовых сообщений
@router.message(F.text, ~F.text.startswith('/'))
async def handle_text_input(message: types.Message, user_settings: dict):
    """Обрабатывает текстовые сообщения пользователей для генерации резюме."""
    user_id = message.from_user.id
    logger.info(f"handle_text_input вызван пользователем {user_id} с текстом: '{message.text[:50]}...'")

    status_msg = await message.answer("Генерирую резюме для вашего текста")

    user_prefs = get_user_settings(user_id, user_settings)
    selected_summary_style = user_prefs.get("summary_style")
    logger.debug(f"Пользователь {user_id}: стиль резюме = {selected_summary_style}")

    try:
        text_input = message.text
        summary = await generate_summary(text_input, selected_summary_style)
        logger.info(f"Резюме сгенерировано для пользователя {user_id}, длина: {len(summary)}")

        style_name = SUMMARY_STYLES.get(selected_summary_style, {}).get('name', 'Стандартный')
        summary_header = f"<b>Краткое резюме</b> (Стиль: {hbold(style_name)}):"
        full_response_text = f"{summary_header}\n{summary}"

        if len(full_response_text) <= MAX_MESSAGE_LENGTH:
            await status_msg.edit_text(full_response_text)
        else:
            await status_msg.edit_text("Резюме готово! Отправляю результат частями")
            await message.answer(summary_header)

            for i in range(0, len(summary), SUMMARY_DISPLAY_CHUNK_SIZE):
                chunk = summary[i:i + SUMMARY_DISPLAY_CHUNK_SIZE]
                await message.answer(chunk)

        logger.info(f"Текст успешно обработан для пользователя {user_id}")

    except Exception as e:
        logger.error(f"Ошибка при обработке текста от пользователя {user_id}: {e}", exc_info=True)
        await status_msg.edit_text(f"Ошибка при генерации резюме: {e}")