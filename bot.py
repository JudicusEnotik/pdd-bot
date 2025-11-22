# bot.py — полная версия для Render.com
import logging
import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InputFile
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

# 🔇 Убираем httpx-спам
logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Состояния
(
    MAIN_MENU,
    ABOUT_MENU,
    CONSULTATION_MENU,
    PHONE_CONSULTATION_NAME,
    PHONE_CONSULTATION_PHONE,
) = range(5)

# ⚙️ НАСТРОЙКИ
BOT_TOKEN = "8514872881:AAGh8--wiPhO6Fe-9CzjGAEyWZZ7nzFF3oM"
ADMIN_CHAT_ID = 8357988210
CHECKLIST_PATH = "checklist.pdf"


async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет только меню — без приветствия (для 'Назад')"""
    text = "Что хочешь сделать?"
    keyboard = [
        ["О курсе «ПДД по-человечески»"],
        ["Консультация"],
        ["🎁 Получить подарок"],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text(text, reply_markup=reply_markup)
    return MAIN_MENU


async def send_welcome_and_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Полное приветствие + меню — только при первом запуске"""
    welcome_text = (
        "Привет! 👋\n"
        "Я — твой бот-помощник курса «ПДД по-человечески» (https://t.me/PDD_Bez_Paniki).\n\n"
        "Со мной ты:\n"
        "✅ Найдёшь ответы на сложные вопросы\n"
        "✅ Быстро свяжешься с инструктором\n"
        "🎁 И даже получишь подарок!"
    )
    await update.message.reply_text(welcome_text)
    return await send_main_menu(update, context)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await send_welcome_and_menu(update, context)


async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    if choice == "О курсе «ПДД по-человечески»":
        keyboard = [
            ["Почему выбирают нас?"],
            ["О курсе"],
            ["Назад"],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
        await update.message.reply_text("Благодарим за интерес к нашему курсу! Что именно тебя интересует?", reply_markup=reply_markup)
        return ABOUT_MENU

    elif choice == "Консультация":
        keyboard = [
            ["Консультация в чате"],
            ["Консультация по телефону"],
            ["Назад"],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
        await update.message.reply_text(
            "Отлично! Как тебе удобнее пообщаться с инструктором?",
            reply_markup=reply_markup,
        )
        return CONSULTATION_MENU

    elif choice == "🎁 Получить подарок":
        if not os.path.isfile(CHECKLIST_PATH):
            await update.message.reply_text(
                "К сожалению, подарок временно недоступен. Напишите инструктору — он пришлёт его вручную!"
            )
            return MAIN_MENU

        try:
            await update.message.reply_text(
                "Отличный выбор! 🎁\n\n"
                "Держи мой бесплатный чек-лист:\n"
                "«10 ловушек в билетах ГИБДД, на которых заваливают 9 из 10».\n\n"
                "Этот материал уже помог сотням учеников не попасться на «каверзные» вопросы!\n"
                "Сохраняй, изучай — и пусть экзамен будет лёгким 😎"
            )
            with open(CHECKLIST_PATH, "rb") as file:
                await update.message.reply_document(document=InputFile(file, filename="10-ловушек-ГИБДД.pdf"))
        except Exception as e:
            logger.error(f"Ошибка отправки PDF: {e}")
            await update.message.reply_text("Произошла ошибка при отправке подарка. Попробуйте позже.")
        return MAIN_MENU

    else:
        await update.message.reply_text("Пожалуйста, выберите один из предложенных вариантов выше.")
        return MAIN_MENU


async def about_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    if choice == "Почему выбирают нас?":
        text = (
            "🔥 ПДД по-человечески — это когда учишься без зевоты и зубрёжки!\n\n"
            "🧠 Теория — не «статья 12.15 ч.3», а нормальный язык:\n"
            "   «Если поедешь на красный — оштрафуют. Или хуже…»\n\n"
            "🛣️ Практика — не в идеальном городе из учебника, а в реальных условиях:\n"
            "   как выехать с двора, не подрезав бабушку на «Запорожце», или что делать, если на перекрёстке все сигналы моргают.\n\n"
            "🌍 Обучение — из любой точки мира. Даже из таёжной избушки (если есть интернет 😅).\n\n"
            "👨‍🏫 Преподаю лично я:\n"
            "   — инструктор с богатым опытом в автошколе,\n"
            "   — инструктор с 93% сдачи с первого раза,\n"
            "   — водитель с опытом работы в разных сферах,\n"
            "   — за плечами — тысячи километров и десятки историй «как я чуть не влетел».\n\n"
            "Хочешь сдать с первого раза и чувствовать себя уверенно за рулём?\n"
            "👉 Жми «Консультация» — расскажу всё по-человечески! 💬"
        )
    elif choice == "О курсе":
        text = (
            "💸 Сколько стоит и что входит в курс «ПДД по-человечески»?\n\n"
            "🎁 Внутри тебя ждёт:\n\n"
            "🔸 10 живых онлайн-уроков с кейсами\n"
            "   Не «слушай и запоминай», а «вот так было — вот как надо».\n"
            "   От знаков и разметки — до тонких моментов манёвров.\n\n"
            "🔸 Разбор всех «каверзных» вопросов из билетов ГИБДД\n"
            "   Не зубри — понимай! Объясню даже те, где фиг разберёшься без контекста.\n\n"
            "🔸 Разбор реальных ошибок учеников\n"
            "   Покажу, где 90% проваливаются — и как этого избежать.\n"
            "   Иногда одна фраза спасает от пересдачи! 🛟\n\n"
            "🔸 Поддержка до самого экзамена\n"
            "   Вопрос в 2 ночи? Написал — получил ответ.\n"
            "   Я не исчезаю после оплаты. Обещаю! ✋ \n\n"
            "Всего 4000 ₽ — и это не просто «видео на Ютубе», а твоя личная подготовка к дороге и экзамену.\n\n"
        )
    elif choice == "Назад":
        return await send_main_menu(update, context)
    else:
        await update.message.reply_text("Пожалуйста, выберите один из предложенных вариантов выше.")
        return ABOUT_MENU

    keyboard = [["Назад"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(text, reply_markup=reply_markup)
    return ABOUT_MENU


async def consultation_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    if choice == "Консультация в чате":
        user = update.effective_user
        admin_msg = (
            f"❗ Новая заявка на чат-консультацию!\n"
            f"Имя: {user.full_name}\n"
            f"ID: {user.id}\n"
            f"Username: @{user.username or 'нет'}"
        )
        try:
            await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_msg)
            await update.message.reply_text(
                "✅ Отлично! Твой запрос на чат-консультацию принят.\n"
                "Скоро инструктор лично свяжется с тобой здесь — в Telegram!"
            )
        except Exception as e:
            logger.error(f"Ошибка отправки в админку: {e}")
            await update.message.reply_text("Произошла ошибка. Попробуйте позже.")
        return await send_main_menu(update, context)

    elif choice == "Консультация по телефону":
        await update.message.reply_text("Хорошо! Напиши, пожалуйста, своё полное имя (ФИО):")
        return PHONE_CONSULTATION_NAME

    elif choice == "Назад":
        return await send_main_menu(update, context)

    else:
        await update.message.reply_text("Пожалуйста, выберите один из предложенных вариантов выше.")
        return CONSULTATION_MENU


async def get_name_for_call(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fio"] = update.message.text.strip()
    await update.message.reply_text(
        "Отлично! Теперь отправь свой номер телефона.\n"
        "Можешь нажать кнопку ниже — это безопасно и удобно 👇",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("📱 Отправить номер", request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )
    return PHONE_CONSULTATION_PHONE


async def get_phone_for_call(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.contact:
        phone = update.message.contact.phone_number
    else:
        phone = update.message.text.strip()

    fio = context.user_data.get("fio", "Не указано")
    user = update.effective_user

    msg = (
        f"📞 Новая заявка на звонок!\n"
        f"ФИО: {fio}\n"
        f"Телефон: {phone}\n"
        f"Telegram: @{user.username or 'нет'} (ID: {user.id})"
    )

    try:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=msg)
        await update.message.reply_text(
            "📞 Принято! Инструктор перезвонит тебе в ближайшее время.\n"
            "Готовься — будет полезно! 😎"
        )
    except Exception as e:
        logger.error(f"Ошибка отправки заявки на звонок: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")

    return await send_main_menu(update, context)


async def fallback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip().lower()
    if text in {"начать", "старт", "start"}:
        return await send_welcome_and_menu(update, context)
    else:
        keyboard = [["Начать"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(
            "Привет! 👋\n\n"
            "Я — бот курса «ПДД по-человечески» (https://t.me/PDD_Bez_Paniki).\n"
            "Нажми кнопку ниже или напиши «Начать», «начать», «Старт» или «старт» — и поехали! 🚗💨",
            reply_markup=reply_markup,
        )


# === ГЛАВНАЯ ФУНКЦИЯ ЗАПУСКА ===
def main():
    if not os.path.isfile(CHECKLIST_PATH):
        logger.warning(f"❗ Файл подарка не найден: {CHECKLIST_PATH}. Положите файл в папку с ботом.")

    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start_command),
            MessageHandler(filters.Regex(r"(?i)^(начать|старт|start)$"), start_command),
        ],
        states={
            MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_handler)],
            ABOUT_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, about_menu_handler)],
            CONSULTATION_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, consultation_menu_handler)],
            PHONE_CONSULTATION_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name_for_call)],
            PHONE_CONSULTATION_PHONE: [
                MessageHandler(filters.CONTACT, get_phone_for_call),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone_for_call),
            ],
        },
        fallbacks=[],
        allow_reentry=True,
    )

    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback_handler))

    # 🔥 ЗАПУСК ВЕБХУКА — БОТ БУДЕТ ЖИТЬ!
    PORT = int(os.environ.get("PORT", 8443))
    WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "https://pdd-bot.onrender.com")

    logger.info(f"🚀 Запуск webhook на порту {PORT} | URL: {WEBHOOK_URL}/{BOT_TOKEN}")

    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}",
        url_path=BOT_TOKEN,
    )


if __name__ == "__main__":
    main()


