import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- НАСТРОЙКИ ---
BOT_TOKEN = "8286072312:AAFbVXSvxIQZv8NQY37ahXB5YW3GBfJR7nQ"  # Замените на токен вашего бота
OPERATOR_USER_ID = 7695561909  # Замените на Telegram ID оператора @user1461474
OPERATOR_USERNAME = "@user1461474"

# Логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


# --- СОСТОЯНИЯ ДЛЯ FSM ---
class OrderState(StatesGroup):
    waiting_for_city = State()
    waiting_for_category = State()
    waiting_for_product = State()
    waiting_for_payment = State()


# --- КЛАВИАТУРЫ ---

# Главное меню (выбор города)
def get_cities_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    cities = [
        "Винница", "Днепр", "Житомир", "Запорожье",
        "Ивано-Франковск", "Киев", "Кропивницкий", "Луцк",
        "Львов", "Николаев", "Одесса", "Полтава",
        "Ровно", "Сумы", "Тернополь", "Ужгород",
        "Харьков", "Херсон", "Хмельницкий", "Черкассы",
        "Черновцы", "Чернигов"
    ]
    # Создаем ряды по 2 кнопки
    row = []
    for city in cities:
        row.append(InlineKeyboardButton(text=city, callback_data=f"city_{city}"))
        if len(row) == 2:
            keyboard.inline_keyboard.append(row)
            row = []
    if row:
        keyboard.inline_keyboard.append(row)
    return keyboard


# Меню категорий товаров
def get_categories_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Мефедрон", callback_data="cat_Мефедрон")],
        [InlineKeyboardButton(text="Alpha_PvP", callback_data="cat_Alpha_PvP")],
        [InlineKeyboardButton(text="Шишки", callback_data="cat_Шишки")],
        [InlineKeyboardButton(text="◀️ Назад к выбору города", callback_data="back_to_cities")]
    ])
    return keyboard


# Меню товаров (зависит от категории)
def get_products_keyboard(category):
    products = {
        "Мефедрон": [
            "Мефедрон мука 1г - 740 UAH", "Мефедрон мука 2г - 1430 UAH",
            "Мефедрон мука 3г - 2150 UAH", "Мефедрон мука 5г - 3500 UAH",
            "Мефедрон кристаллы 1г - 880 UAH", "Мефедрон кристаллы 2г - 1720 UAH",
            "Мефедрон кристаллы 3г - 2550 UAH", "Мефедрон кристаллы 5г - 4100 UAH"
        ],
        "Alpha_PvP": [
            "Alpha_PvP кристаллы 1г - 780 UAH", "Alpha_PvP кристаллы 2г - 1490 UAH",
            "Alpha_PvP кристаллы 3г - 2250 UAH", "Alpha_PvP кристаллы 5г - 3600 UAH"
        ],
        "Шишки": [
            "[ТГК🧪:25%] Granddaddy Purple 2г - 600 UAH", "[ТГК🧪:25%] Granddaddy Purple 5г - 1400 UAH",
            "[ТГК🧪:25%] Granddaddy Purple 10г - 2500 UAH",
            "[ТГК🧪:24%] Bubblegum 1г - 300 UAH", "[ТГК🧪:24%] Bubblegum 3г - 850 UAH",
            "[ТГК🧪:24%] Bubblegum 5г - 1400 UAH",
            "[ТГК🧪:28%] Gorilla Glue 3г - 850 UAH", "[ТГК🧪:28%] Gorilla Glue 5г - 1400 UAH"
        ]
    }

    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for product in products.get(category, []):
        keyboard.inline_keyboard.append([InlineKeyboardButton(text=product, callback_data=f"product_{product}")])
    keyboard.inline_keyboard.append(
        [InlineKeyboardButton(text="◀️ Назад к категориям", callback_data="back_to_categories")])
    return keyboard


# Меню способа оплаты
def get_payment_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить переводом на карту", callback_data="pay_card")],
        [InlineKeyboardButton(text="₿ Оплата через BTC", callback_data="pay_btc")],
        [InlineKeyboardButton(text="◀️ Назад к категориям", callback_data="back_to_categories")]
    ])
    return keyboard


# --- ОБРАБОТЧИКИ ---

@dp.message(Command("start"))
async def start_command(message: types.Message):
    """Обработчик команды /start"""
    await message.answer(
        """
        Приветствуем!❤️‍🔥
        Добро пожаловать в наш бот – место, где вас ждет лучший сервис!

        📌 Актуальные вакансии:
        — Рекрутер: онлайн-работа, если у вас есть талант находить лучших специалистов, мы ждем вас в команде!
        — Курьер: стабильный доход и свободный график – отличная возможность для тех, кто хочет быть в движении!
        — Городской супергерой: расклейка стикеров:
        Отличный вариант для тех кто хочет быстро и легко заработать, а главное безопасно 😉
        """
        f"✍🏻По вопросам связанными с оплатами писать: {OPERATOR_USERNAME}\n\n"
        "Для покупки выберите свой город из списка снизу:",
        reply_markup=get_cities_keyboard()
    )


@dp.callback_query(F.data.startswith('city_'))
async def process_city(callback: types.CallbackQuery, state: FSMContext):
    """Обработка выбора города и переход к категориям"""
    city = callback.data.replace('city_', '')
    await state.update_data(selected_city=city)
    await callback.answer()

    await callback.message.edit_text(
        text=f"🏙 Ваш город: <b>{city}</b>\nВыберите категорию товара:",
        reply_markup=get_categories_keyboard(),
        parse_mode="HTML"
    )


@dp.callback_query(F.data == 'back_to_cities')
async def back_to_cities(callback: types.CallbackQuery):
    """Возврат к выбору города"""
    await callback.answer()
    await callback.message.edit_text(
        text="Для покупки выберите свой город из списка снизу:",
        reply_markup=get_cities_keyboard()
    )


@dp.callback_query(F.data.startswith('cat_'))
async def process_category(callback: types.CallbackQuery, state: FSMContext):
    """Обработка выбора категории и отображение товаров"""
    category = callback.data.replace('cat_', '')
    await state.update_data(selected_category=category)
    await callback.answer()

    await callback.message.edit_text(
        text=f"🍽 Категория: <b>{category}</b>\nВыберите товар:",
        reply_markup=get_products_keyboard(category),
        parse_mode="HTML"
    )


@dp.callback_query(F.data == 'back_to_categories')
async def back_to_categories(callback: types.CallbackQuery, state: FSMContext):
    """Возврат к категориям товаров"""
    user_data = await state.get_data()
    city = user_data.get('selected_city', 'Не выбран')
    await callback.answer()

    await callback.message.edit_text(
        text=f"🏙 Ваш город: <b>{city}</b>\nВыберите категорию товара:",
        reply_markup=get_categories_keyboard(),
        parse_mode="HTML"
    )


@dp.callback_query(F.data.startswith('product_'))
async def process_product(callback: types.CallbackQuery, state: FSMContext):
    """Обработка выбора товара и предложение способа оплаты"""
    product = callback.data.replace('product_', '')
    await state.update_data(selected_product=product)
    await callback.answer()

    await callback.message.edit_text(
        text=f"🛒 Вы выбрали: <b>{product}</b>\n\nВыберите способ оплаты:",
        reply_markup=get_payment_keyboard(),
        parse_mode="HTML"
    )


@dp.callback_query(F.data.startswith('pay_'))
async def process_payment(callback: types.CallbackQuery, state: FSMContext):
    """Финализация заказа, отправка уведомления оператору и клиенту"""
    payment_method = "Перевод на карту 💳" if callback.data == 'pay_card' else "Bitcoin (BTC) ₿"
    user_data = await state.get_data()
    city = user_data.get('selected_city', 'Не выбран')
    product = user_data.get('selected_product', 'Не выбран')

    await callback.answer()

    # Сообщение клиенту
    await callback.message.edit_text(
        text=f"✅ <b>Заказ почти оформлен!</b>\n\n"
             f"Для оплаты и получения реквизитов обращайтесь к оператору {OPERATOR_USERNAME}",
        parse_mode="HTML"
    )

    # Уведомление оператору
    operator_message = (
        f"🛎 <b>НОВЫЙ ЗАКАЗ!</b>\n\n"
        f"👤 Клиент: @{callback.from_user.username or 'нет юзернейма'} "
        f"(ID: <code>{callback.from_user.id}</code>)\n"
        f"🏙 Город: <b>{city}</b>\n"
        f"🛒 Товар: <b>{product}</b>\n"
        f"💲 Способ оплаты: <b>{payment_method}</b>\n\n"
        f"📞 Не забудьте связаться с клиентом для уточнения деталей и отправки реквизитов."
    )

    try:
        await bot.send_message(OPERATOR_USER_ID, operator_message, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Не удалось отправить сообщение оператору: {e}")
        await callback.message.answer(
            "⚠️ Произошла ошибка при отправке уведомления оператору. Пожалуйста, свяжитесь с ним напрямую."
        )

    # Сброс состояния
    await state.clear()


# Запуск бота
async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
