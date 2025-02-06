import os
import random
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# Получаем токен из переменных окружения
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Подключение к базе данных
conn = sqlite3.connect("users.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, balance REAL)")
conn.commit()

# Функция получения баланса
def get_balance(user_id):
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    return result[0] if result else 0

# Функция изменения баланса
def update_balance(user_id, amount):
    if get_balance(user_id) == 0:
        cursor.execute("INSERT INTO users (user_id, balance) VALUES (?, ?)", (user_id, amount))
    else:
        cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (amount, user_id))
    conn.commit()

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    user_id = message.from_user.id
    update_balance(user_id, 0)  # Добавляем пользователя, если его нет
    await message.answer(f"Привет, {message.from_user.first_name}! Ваш баланс: {get_balance(user_id)} XRocket.")

@dp.message_handler(commands=["roll"])
async def roll_dice(message: types.Message):
    user_id = message.from_user.id
    bet = 10  # Фиксированная ставка
    
    if get_balance(user_id) < bet:
        await message.answer("Недостаточно средств для игры.")
        return

    await message.answer("Выбирайте число от 1 до 6:")

    @dp.message_handler()
    async def get_guess(msg: types.Message):
        try:
            guess = int(msg.text)
            if guess < 1 or guess > 6:
                await msg.answer("Введите число от 1 до 6.")
                return

            update_balance(user_id, -bet)  # Снимаем ставку
            result = random.randint(1, 6)
            await msg.answer(f"Выпало число: {result}")

            if guess == result:
                winnings = bet * 3
                update_balance(user_id, winnings)
                await msg.answer(f"Поздравляем! Вы выиграли {winnings} XRocket. Новый баланс: {get_balance(user_id)} XRocket.")
            else:
                await msg.answer(f"Вы проиграли. Новый баланс: {get_balance(user_id)} XRocket.")

        except ValueError:
            await msg.answer("Введите корректное число.")

# Запуск бота
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
  
