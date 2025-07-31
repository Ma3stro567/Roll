from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import logging

TOKEN = '7250583371:AAGYFPlaX26WzoUHxi9lKKBHbZIjwk6_Znc'
ADMIN_PASSWORD = "14885252"

admins = set()
banned_users = set()

logging.basicConfig(level=logging.INFO)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет тут ты можешь связаться со мной.")


async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if ADMIN_PASSWORD in update.message.text:
        admins.add(update.message.from_user.id)
        await update.message.reply_text("✅ Вы вошли в админ-панель.\nДоступные команды:\n/ban <user_id>")
    else:
        await update.message.reply_text("❌ Неверный пароль.")


async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in admins:
        await update.message.reply_text("⛔ У вас нет прав.")
        return
    try:
        target_id = int(context.args[0])
        banned_users.add(target_id)
        await update.message.reply_text(f"🔒 Пользователь {target_id} забанен.")
    except (IndexError, ValueError):
        await update.message.reply_text("⚠️ Использование: /ban <user_id>")


async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    if user.id in banned_users:
        await update.message.reply_text("⛔ Вы забанены.")
        return

    username = f"@{user.username}" if user.username else "Без username"
    msg = f"📨 Сообщение от {username} (ID: {user.id}):\n\n{update.message.text}"

    # Отправка всем админам
    for admin_id in admins:
        await context.bot.send_message(chat_id=admin_id, text=msg)


async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from_user = update.message.from_user.id
    if from_user not in admins or not update.message.reply_to_message:
        return

    # Ищем ID в тексте оригинального сообщения
    lines = update.message.reply_to_message.text.splitlines()
    target_id = None
    for line in lines:
        if 'ID:' in line:
            try:
                target_id = int(line.split("ID:")[1].split(")")[0].strip())
                break
            except:
                pass

    if target_id:
        try:
            await context.bot.send_message(chat_id=target_id, text=update.message.text)
            await update.message.reply_text("✅ Ответ отправлен.")
        except:
            await update.message.reply_text("❌ Не удалось отправить сообщение.")
    else:
        await update.message.reply_text("⚠️ Не найден ID пользователя.")


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("adminpanel", admin_panel))
    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(MessageHandler(filters.TEXT & filters.REPLY, admin_reply))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_message))

    app.run_polling()


if __name__ == '__main__':
    main()
    
