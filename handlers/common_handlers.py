from aiogram import Router, F, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold

from keyboards.inline import get_main_settings_keyboard
from states.user_states import SettingsStates
from config import (
    DEFAULT_LANGUAGE,
    DEFAULT_SUMMARY_STYLE,
    SUPPORTED_LANGUAGES,
    SUMMARY_STYLES
)


router = Router()



def get_user_settings(user_id: int, dp_user_settings: dict):

    if user_id not in dp_user_settings:
        dp_user_settings[user_id] = {
            "language": DEFAULT_LANGUAGE,
            "summary_style": DEFAULT_SUMMARY_STYLE,
            "summary_style_name": SUMMARY_STYLES[DEFAULT_SUMMARY_STYLE]["name"]
        }
    elif 'summary_style_name' not in dp_user_settings[user_id]:
        current_style_key = dp_user_settings[user_id].get('summary_style', DEFAULT_SUMMARY_STYLE)
        style_info = SUMMARY_STYLES.get(current_style_key, SUMMARY_STYLES[DEFAULT_SUMMARY_STYLE])
        dp_user_settings[user_id]['summary_style_name'] = style_info["name"]

    return dp_user_settings[user_id]



@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext, user_settings: dict, whisper_model: tuple):
    await state.clear()
    user = message.from_user
    user_id = user.id
    current_settings = get_user_settings(user_id, user_settings)

    _, device = whisper_model
    lang_name = SUPPORTED_LANGUAGES.get(current_settings["language"], "Авто")
    style_name = current_settings["summary_style_name"]

    greeting_text = (
        f"Привет, {hbold(user.first_name or 'пользователь')}!\n\n"
        "Вот что я умею:\n"
        "   — Транскрибировать голосовые и аудиосообщени в текст с помощью Whisper\n"
        "   — Генерировать краткое резюме текста с помощью LLM\n\n"
        f"Язык транскрибации: {hbold(lang_name)}\n"
        f"Стиль резюме: {hbold(style_name)}\n"
    )

    await message.answer(greeting_text)


@router.message(Command("help"))
async def cmd_help(message: types.Message, user_settings: dict):
    """Справка по возможностям бота"""
    user_id = message.from_user.id
    current_settings = get_user_settings(user_id, user_settings)

    lang_code = current_settings.get("language", DEFAULT_LANGUAGE)
    lang_name = SUPPORTED_LANGUAGES.get(lang_code, "Авто")

    style_code = current_settings.get("summary_style", DEFAULT_SUMMARY_STYLE)
    style_name = SUMMARY_STYLES.get(style_code, SUMMARY_STYLES[DEFAULT_SUMMARY_STYLE])["name"]

    help_text = (
        "<b>Как пользоваться этим ботом:</b>\n\n"
        "<b>Основные возможности:</b>\n"
        "   — Распознавание голосовых и аудиозаписей\n"
        "   — Суммаризация текста (краткое содержание)\n\n"
        "<b>Как начать:</b>\n"
        "   — Отправить голосовое или аудиосообщение (.ogg; .mp3; т.д.) \n"
        "   — Бот обработает и пришлёт результат\n\n"
        "<b>Настройки:</b>\n"
        f"  — Язык транскрибации: {hbold(lang_name)}\n"
        f"  — Стиль резюме: {hbold(style_name)}\n\n"
        "<b>Дополнительно:</b>\n"
        "   /settings — открыть меню настроек\n"
        "   /cancel — отменить текущее действие\n"
        "   /help — справка"
    )

    await message.answer(help_text)


@router.message(Command("settings"))
async def cmd_settings(message: types.Message, state: FSMContext):
    """Открывает главное меню настроек."""
    await state.set_state(SettingsStates.MAIN_SETTINGS_MENU)
    await message.answer(
        "⚙️ <b>Настройки бота</b>\n\nВыберите, что хотите настроить:",
        reply_markup=get_main_settings_keyboard()
    )


@router.callback_query(F.data == "settings:close", SettingsStates.MAIN_SETTINGS_MENU)
async def cq_settings_close(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Настройки закрыты")
    await callback.answer()


@router.message(Command("cancel"))
@router.callback_query(F.data == "cancel_state")
async def cmd_cancel(event: types.Message | types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        text = "Нет активных действий для отмены"
        if isinstance(event, types.Message):
            await event.answer(text)
        else:
            await event.answer(text, show_alert=True)
        return

    await state.clear()
    text = "Действие отменено"

    if isinstance(event, types.Message):
        await event.answer(text)
    elif isinstance(event, types.CallbackQuery) and event.message:
        try:
            await event.message.edit_text(text)
        except Exception:
            await event.message.answer(text)
        await event.answer()

