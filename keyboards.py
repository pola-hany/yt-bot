from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu():
    keyboard = [
        [
            InlineKeyboardButton("🎥 فيديو", callback_data="video"),
            InlineKeyboardButton("🎧 صوت", callback_data="audio")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def quality_menu():
    keyboard = [
        [InlineKeyboardButton("144p", callback_data="144p")],
        [InlineKeyboardButton("360p", callback_data="360p")],
        [InlineKeyboardButton("720p", callback_data="720p")],
        [InlineKeyboardButton("🌟 أفضل جودة", callback_data="best")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back")]
    ]
    return InlineKeyboardMarkup(keyboard)