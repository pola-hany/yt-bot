"""
keyboards.py — لوحات المفاتيح الـ Inline للبوت
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """لوحة المفاتيح الرئيسية: اختيار فيديو أو صوت."""
    keyboard = [
        [
            InlineKeyboardButton("🎥 تحميل فيديو", callback_data="type_video"),
            InlineKeyboardButton("🎧 تحميل صوت",  callback_data="type_audio"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def video_quality_keyboard() -> InlineKeyboardMarkup:
    """لوحة اختيار جودة الفيديو."""
    keyboard = [
        [
            InlineKeyboardButton("📱 144p",          callback_data="quality_144p"),
            InlineKeyboardButton("📺 360p",          callback_data="quality_360p"),
        ],
        [
            InlineKeyboardButton("🖥️ 720p (HD)",     callback_data="quality_720p"),
            InlineKeyboardButton("⭐ أفضل جودة",     callback_data="quality_best"),
        ],
        [
            InlineKeyboardButton("🔙 رجوع",          callback_data="back_to_menu"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def back_keyboard() -> InlineKeyboardMarkup:
    """زر الرجوع فقط."""
    keyboard = [
        [InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)
