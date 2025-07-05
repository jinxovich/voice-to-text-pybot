import logging

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold

from config import SUPPORTED_LANGUAGES, SUMMARY_STYLES
from handlers.common_handlers import get_user_settings
from keyboards.inline import (
    get_language_keyboard,
    get_main_settings_keyboard,
    get_summary_style_keyboard
)
from states.user_states import SettingsStates


logger = logging.getLogger(__name__)
router = Router()

logger.info("settings_handlers.router создан.")


# Обработчики настроек 

@router.callback_query(F.data == "settings:main")
async def cq_back_to_main_settings(callback: types.CallbackQuery, state: FSMContext):
    """Возвращает пользователя в главное меню настроек."""
    user_id = callback.from_user.id
    logger.info(f"cq_back_to_main_settings вызван пользователем {user_id}")

    await state.set_state(SettingsStates.MAIN_SETTINGS_MENU)

    await callback.message.edit_text(
        "<b>Настройки бота</b>\n\nВыберите, что вы хотите настроить:",
        reply_markup=get_main_settings_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "settings:language", SettingsStates.MAIN_SETTINGS_MENU)
async def cq_select_language_menu(callback: types.CallbackQuery, state: FSMContext, user_settings: dict):
    """Открывает меню выбора языка транскрибации."""
    user_id = callback.from_user.id
    logger.info(f"cq_select_language_menu вызван пользователем {user_id}")

    user_prefs = get_user_settings(user_id, user_settings)

    await state.set_state(SettingsStates.CHOOSING_LANGUAGE)
    await callback.message.edit_text(
        "Выбрать язык",
        reply_markup=get_language_keyboard(user_prefs["language"])
    )
    await callback.answer()


@router.callback_query(SettingsStates.CHOOSING_LANGUAGE, F.data.startswith("select_lang:"))
async def cq_set_language(callback: types.CallbackQuery, state: FSMContext, user_settings: dict):
    """Устанавливает выбранный пользователем язык."""
    user_id = callback.from_user.id
    lang_code = callback.data.split(":")[1]

    logger.info(f"cq_set_language вызван пользователем {user_id}, lang_code: {lang_code}")

    if lang_code not in SUPPORTED_LANGUAGES:
        logger.warning(f"Неверный lang_code '{lang_code}' от пользователя {user_id}")
        await callback.answer("Неверный код языка.", show_alert=True)
        return

    user_prefs = get_user_settings(user_id, user_settings)
    user_prefs["language"] = lang_code
    logger.info(f"Язык пользователя {user_id} установлен: {lang_code}")

    selected_lang_name = SUPPORTED_LANGUAGES[lang_code]
    await callback.answer(f"Язык установлен: {selected_lang_name}", show_alert=False)

    await state.set_state(SettingsStates.MAIN_SETTINGS_MENU)
    await callback.message.edit_text(
        f"⚙️ <b>Настройки бота</b>\n\n"
        f"Язык транскрибации изменён на: {hbold(selected_lang_name)}\n"
        f"Выберите, что вы хотите настроить:",
        reply_markup=get_main_settings_keyboard()
    )


@router.callback_query(F.data == "settings:summary_style", SettingsStates.MAIN_SETTINGS_MENU)
async def cq_select_summary_style_menu(callback: types.CallbackQuery, state: FSMContext, user_settings: dict):
    """Открывает меню выбора стиля резюме."""
    user_id = callback.from_user.id
    logger.info(f"cq_select_summary_style_menu вызван пользователем {user_id}")

    user_prefs = get_user_settings(user_id, user_settings)

    await state.set_state(SettingsStates.CHOOSING_SUMMARY_STYLE)
    await callback.message.edit_text(
        "Выберите стиль для генерируемого резюме:",
        reply_markup=get_summary_style_keyboard(user_prefs["summary_style"])
    )
    await callback.answer()


@router.callback_query(SettingsStates.CHOOSING_SUMMARY_STYLE, F.data.startswith("select_style:"))
async def cq_set_summary_style(callback: types.CallbackQuery, state: FSMContext, user_settings: dict):
    """Устанавливает выбранный стиль резюме."""
    user_id = callback.from_user.id
    style_code = callback.data.split(":")[1]

    logger.info(f"cq_set_summary_style вызван пользователем {user_id}, style_code: {style_code}")

    if style_code not in SUMMARY_STYLES:
        logger.warning(f"Неверный style_code '{style_code}' от пользователя {user_id}")
        await callback.answer("Неверный стиль резюме.", show_alert=True)
        return

    user_prefs = get_user_settings(user_id, user_settings)
    user_prefs["summary_style"] = style_code
    user_prefs["summary_style_name"] = SUMMARY_STYLES[style_code]["name"]
    logger.info(f"Стиль резюме пользователя {user_id} установлен: {style_code}")

    selected_style_name = SUMMARY_STYLES[style_code]["name"]
    await callback.answer(f"Стиль резюме установлен: {selected_style_name}", show_alert=False)

    await state.set_state(SettingsStates.MAIN_SETTINGS_MENU)
    await callback.message.edit_text(
        f"⚙️ <b>Настройки бота</b>\n\n"
        f"Стиль резюме изменён на: {hbold(selected_style_name)}\n"
        f"Выберите, что вы хотите настроить:",
        reply_markup=get_main_settings_keyboard()
    )