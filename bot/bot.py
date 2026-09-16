"""
Rus tili o'rganish boti
------------------------
Funksiyalari:
  /start - botni ishga tushirish, tugmalar bilan menyu
  /soz   - tasodifiy rus so'zi va uning o'zbekcha tarjimasini ko'rsatadi
  /test  - 4 variantli test: rus so'zi beriladi, to'g'ri tarjimani tanlash kerak

O'rnatish:
  pip install python-telegram-bot

Ishga tushirish:
  1. Pastdagi BOT_TOKEN o'rniga @BotFather bergan tokenni qo'ying
  2. python bot.py
"""

import os
import random
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# ============ SOZLAMALAR ============
# Token endi kodning ichida emas, balki serverning "Environment Variable"
# (muhit o'zgaruvchisi) qismidan o'qiladi. Bu tokenni GitHub'da ochiq
# ko'rsatib qo'ymaslik uchun kerak.
#
# - Railway/Render kabi serverda: "Variables" bo'limiga BOT_TOKEN nomi
#   bilan qo'shasiz.
# - O'zingizning kompyuteringizda sinab ko'rmoqchi bo'lsangiz, pastdagi
#   qatorni vaqtincha o'chirib, o'rniga to'g'ridan-to'g'ri
#   BOT_TOKEN = "haqiqiy_tokeningiz" deb yozishingiz mumkin.
BOT_TOKEN = os.environ.get("BOT_TOKEN", "BU_YERGA_TOKENINGIZNI_QOYING")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ============ SO'ZLAR LUG'ATI ============
# Kerak bo'lsa bu ro'yxatga istalgancha so'z qo'shishingiz mumkin
WORDS = {
    "привет": "salom",
    "спасибо": "rahmat",
    "пожалуйста": "iltimos / marhamat",
    "да": "ha",
    "нет": "yo'q",
    "друг": "do'st",
    "семья": "oila",
    "дом": "uy",
    "вода": "suv",
    "хлеб": "non",
    "работа": "ish",
    "школа": "maktab",
    "книга": "kitob",
    "любовь": "sevgi",
    "время": "vaqt",
    "деньги": "pul",
    "город": "shahar",
    "улица": "ko'cha",
    "машина": "mashina",
    "человек": "inson",
}

# Foydalanuvchining joriy test javobini vaqtincha saqlash uchun (oddiy usul)
active_tests = {}


# ============ /start ============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📖 Yangi so'z", callback_data="new_word")],
        [InlineKeyboardButton("📝 Test boshlash", callback_data="new_test")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Salom! Men rus tilini o'rganishga yordam beruvchi botman.\n\n"
        "🔹 /soz - yangi rus so'zi va tarjimasini ko'rish\n"
        "🔹 /test - 4 variantli test ishlash\n\n"
        "Yoki quyidagi tugmalardan foydalaning:",
        reply_markup=reply_markup,
    )


# ============ /soz ============
async def send_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rus_soz = random.choice(list(WORDS.keys()))
    tarjima = WORDS[rus_soz]
    text = f"🇷🇺 *{rus_soz}*\n🇺🇿 {tarjima}"

    keyboard = [
        [InlineKeyboardButton("📖 Yana bitta so'z", callback_data="new_word")],
        [InlineKeyboardButton("📝 Test qilib ko'rish", callback_data="new_test")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        await update.callback_query.message.reply_text(
            text, parse_mode="Markdown", reply_markup=reply_markup
        )


# ============ /test ============
async def send_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Savol uchun so'z va noto'g'ri variantlarni tanlash
    rus_soz = random.choice(list(WORDS.keys()))
    togri_javob = WORDS[rus_soz]

    boshqa_tarjimalar = [v for k, v in WORDS.items() if k != rus_soz]
    notogri_variantlar = random.sample(boshqa_tarjimalar, min(3, len(boshqa_tarjimalar)))

    variantlar = notogri_variantlar + [togri_javob]
    random.shuffle(variantlar)

    # To'g'ri javobni shu foydalanuvchi uchun eslab qolamiz
    active_tests[user_id] = togri_javob

    keyboard = [
        [InlineKeyboardButton(variant, callback_data=f"answer|{variant}")]
        for variant in variantlar
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = f"❓ *{rus_soz}* so'zining o'zbekcha tarjimasi qaysi?"

    if update.message:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        await update.callback_query.message.reply_text(
            text, parse_mode="Markdown", reply_markup=reply_markup
        )


# ============ Tugmalar bosilganda ============
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "new_word":
        await send_word(update, context)

    elif query.data == "new_test":
        await send_test(update, context)

    elif query.data.startswith("answer|"):
        user_id = update.effective_user.id
        tanlangan = query.data.split("|", 1)[1]
        togri_javob = active_tests.get(user_id)

        if tanlangan == togri_javob:
            natija = "✅ To'g'ri! Ajoyib ish."
        else:
            natija = f"❌ Noto'g'ri. To'g'ri javob: *{togri_javob}*"

        keyboard = [
            [InlineKeyboardButton("📝 Yana test", callback_data="new_test")],
            [InlineKeyboardButton("📖 Yangi so'z", callback_data="new_word")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            natija, parse_mode="Markdown", reply_markup=reply_markup
        )


# ============ Botni ishga tushirish ============
def main():
    if BOT_TOKEN == "BU_YERGA_TOKENINGIZNI_QOYING":
        print(
            "XATOLIK: BOT_TOKEN topilmadi!\n"
            "Serverda 'Variables' bo'limiga BOT_TOKEN qo'shing, "
            "yoki shu faylda to'g'ridan-to'g'ri tokeningizni yozing."
        )
        return

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("soz", send_word))
    app.add_handler(CommandHandler("test", send_test))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot ishga tushdi... To'xtatish uchun Ctrl+C bosing.")
    app.run_polling()


if __name__ == "__main__":
    main()
