from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import logging

TOKEN = '7250583371:AAGYFPlaX26WzoUHxi9lKKBHbZIjwk6_Znc'
ADMIN_PASSWORD = "14885252"

admins = set()
banned_users = set()

logging.basicConfig(level=logging.INFO)


def start(update: Update, context: CallbackContext):
    update.message.reply_text("Привет! Напиши сообщение, и оно попадёт админу.")


def admin_panel(update: Update, context: CallbackContext):
    if ADMIN_PASSWORD in update.message.text:
        admins.add(update.message.from_user.id)
        update.message.reply_text("✅ Вы вошли в админ-панель.\nДоступные команды:\n/ban <user_id>")
    else:
        update.message.reply_text("❌ Неверный пароль.")


def ban_user(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in admins:
        update.message.reply_text("⛔ У вас нет прав.")
        return
    try:
        target_id = int(context.args[0])
        banned_users.add(target_id)
        update.message.reply_text(f"🔒 Пользователь {target_id} забанен.")
    except:
        update.message.reply_text("⚠️ Использование: /ban <user_id>")


def handle_user_message(update: Update, context: CallbackContext):
    user = update.message.from_user
    if user.id in banned_users:
        update.message.reply_text("⛔ Вы забанены.")
        return

    username = f"@{user.username}" if user.username else "Без username"
    msg = f"📨 Сообщение от {username} (ID: {user.id}):\n\n{update.message.text}"

    # Отправка всем админам
    for admin_id in admins:
        context.bot.send_message(chat_id=admin_id, text=msg)


def admin_reply(update: Update, context: CallbackContext):
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
            context.bot.send_message(chat_id=target_id, text=update.message.text)
            update.message.reply_text("✅ Ответ отправлен.")
        except:
            update.message.reply_text("❌ Не удалось отправить сообщение.")
    else:
        update.message.reply_text("⚠️ Не найден ID пользователя.")


def main():
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("adminpanel", admin_panel))
    dp.add_handler(CommandHandler("ban", ban_user, pass_args=True))
    dp.add_handler(MessageHandler(Filters.text & Filters.reply, admin_reply))
    dp.add_handler(MessageHandler(Filters.text, handle_user_message))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
    
