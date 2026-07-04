import logging
import asyncio
import random
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

load_dotenv()
# --- НАСТРОЙКИ ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPERATOR_USER_ID = int(os.getenv("OPERATOR_USER_ID"))
OPERATOR_USERNAME = os.getenv("OPERATOR_USERNAME")

# Логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# --- ДАННЫЕ ---
CITIES_DISTRICTS = {
    "Киев": ["Печерск", "Шевченковка", "Оболонь", "Голосеево", "Дарница", "Соломенка", "Святошино", "Подол", "Троещина",
             "Позняки", "Осокорки", "Борщаговка", "Виноградарь", "Нивки", "Теремки"],
    "Львов": ["Галицкий", "Сихов", "Лычаков", "Франковский", "Зализничный", "Стрыйский парк", "Винники", "Рясное",
              "Збоища", "Брюховичи"],
    "Одесса": ["Аркадия", "Фонтанка", "Черемушки", "Таирова", "Молдаванка", "Пересыпь", "Слободка", "Лузановка",
               "Поселок Котовского", "Школьный"],
    "Харьков": ["Салтовка", "Алексеевка", "Павловка", "Москалевка", "Гончаровка", "Залютино", "Новые дома", "ХТЗ",
                "Рогань", "Журавлевка", "Нагорный"],
    "Днепр": ["Победа", "Левобережный", "Кодаки", "Мандрыковка", "Фрунзенский", "Красный Камень", "Парус", "Тополь",
              "12 квартал", "Западный"],
    "Винница": ["Вишенка", "Пирогово", "Старый город", "Замостье", "Пятничаны", "Парковая", "Тяжилов"],
    "Житомир": ["Богунский", "Королевский", "Хинчанка", "Путятинка", "Маликова", "Смолянка", "Крошня"],
    "Запорожье": ["Хортица", "Верхняя Хортица", "Павло-Кичкас", "Соцгород", "Арматурный", "Бородинский",
                  "Осипенковский", "Вознесенка"],
    "Ивано-Франковск": ["Пасічна", "Підлісся", "Пирогівка", "Каскад", "Позитрон", "Опришівці", "Вовчинець", "Угорники"],
    "Кропивницкий": ["Фортечный", "Балашовка", "Новостройка", "Лелековка", "Ковалевка", "Большая Балка"],
    "Луцк": ["Теремно", "Вишенка", "Сили", "Глушец", "Старый город", "Завокзальный", "Промышленный"],
    "Николаев": ["Богоявленский", "Соляные", "Терновка", "Макаровка", "Центральный (бывш. Ленинский)", "Корабельный",
                 "Намыв", "Большая Корениха"],
    "Полтава": ["Киевский", "Подол", "Огневка", "Кобыщаны", "Рыбцы", "Яковцы", "Дублянщина"],
    "Ровно": ["Грабово", "Митинский", "Юбилейный", "Новый город", "Старый город", "Золотая", "Против ТЦ Злата"],
    "Сумы": ["Ковпаковский", "Заречный", "Центр", "Солнечный", "Добровольческое", "Лысая гора"],
    "Тернополь": ["Дружба", "Новый мир", "Старый парк", "Центр", "Промышленная", "Аляска", "Кутковцы"],
    "Ужгород": ["Боздос", "Дравцы", "Малаховка", "Радванка", "Корятовича", "Шахта", "Горяны"],
    "Херсон": ["Таврический", "Корабел", "Забалка", "Северный", "Шуменский", "Молодежный", "Жилпоселок"],
    "Хмельницкий": ["Гречаны", "Лесково", "Дубовая", "Озерная", "Раково", "Выставка", "Центр"],
    "Черкассы": ["Дахновка", "Сосновка", "Кривалівка", "Митниця", "Казбет", "Червоная Слобода"],
    "Черновцы": ["Центр", "Калиновка", "Роша", "Садгора", "Ленківці", "Шубранець", "Дружба"],
    "Чернигов": ["Полесье", "Коты", "Шерстянка", "Пески", "Бобровица", "Масаны", "ЗАЗ", "Новозаводской"],
    "Кривой Рог": ["95 квартал", "ВДК", "Игуменка", "Коломойцево", "Рудничный", "Покровский", "Центр", "Долгинцево",
                   "Ингулец"],
    "Мариуполь": ["Центр", "Жовтневый", "Левобережье", "Западный", "Восточный", "Портовая"],
    "Северодонецк": ["Новый город", "Химический", "Квартал-5", "Квартал-8", "Солнечный", "Мирный", "Лесной"],
}

# Полный список товаров с их граммовками и ценами
ALL_PRODUCTS = {
    "💎 Мефедрон Кристалл": {
        "0.5г - 550 UAH": "0.5г",
        "1г - 1080 UAH": "1г",
        "2г - 2120 UAH": "2г",
        "3г - 3150 UAH": "3г",
        "5г - 5080 UAH": "5г",
        "10г - 10020 UAH": "10г"
    },
    "🍚 Мефедрон Мука": {
        "0.5г - 510 UAH": "0.5г",
        "1г - 990 UAH": "1г",
        "2г - 1850 UAH": "2г",
        "3г - 2710 UAH": "3г",
        "5г - 4500 UAH": "5г",
        "10г - 8470 UAH": "10г"
    },
    "⚡ Alpha-PvP": {
        "0.5г - 520 UAH": "0.5г",
        "1г - 1040 UAH": "1г",
        "2г - 1950 UAH": "2г",
        "3г - 2820 UAH": "3г",
        "5г - 4560 UAH": "5г",
        "10г - 8620 UAH": "10г"
    },
    "💨 Амфетамин": {
        "0.5г - 480 UAH": "0.5г",
        "1г - 960 UAH": "1г",
        "2г - 1890 UAH": "2г",
        "3г - 2780 UAH": "3г",
        "5г - 4610 UAH": "5г",
        "10г - 8810 UAH": "10г"
    },
    "💊 Экстази": {
        "2т - 1170 UAH": "2т",
        "4т - 2150 UAH": "4т",
        "6т - 3100 UAH": "6т",
        "10т - 4850 UAH": "10т",
        "20т - 9200 UAH": "20т"
    },
    "🌿 Шишки": {
        "[ТГК🧪:25%] Granddaddy Purple 2г - 600 UAH": "2г",
        "[ТГК🧪:25%] Granddaddy Purple 5г - 1400 UAH": "5г",
        "[ТГК🧪:25%] Granddaddy Purple 10г - 2500 UAH": "10г",
        "[ТГК🧪:24%] Bubblegum 1г - 300 UAH": "1г",
        "[ТГК🧪:24%] Bubblegum 3г - 850 UAH": "3г",
        "[ТГК🧪:24%] Bubblegum 5г - 1400 UAH": "5г",
        "[ТГК🧪:28%] Gorilla Glue 3г - 850 UAH": "3г",
        "[ТГК🧪:28%] Gorilla Glue 5г - 1400 UAH": "5г"
    },
    "🍫 Гашиш": {
        "1г (мягкий) - 500 UAH": "1г",
        "3г (мягкий) - 1300 UAH": "3г",
        "5г (мягкий) - 2100 UAH": "5г",
        "1г (твердый) - 600 UAH": "1г",
        "3г (твердый) - 1600 UAH": "3г",
        "5г (твердый) - 2500 UAH": "5г"
    },
    "🎨 Марки LSD": {
        "1 шт (100µg) - 400 UAH": "1 шт",
        "3 шт (100µg) - 1100 UAH": "3 шт",
        "5 шт (100µg) - 1700 UAH": "5 шт",
        "1 шт (200µg) - 750 UAH": "1 шт",
        "3 шт (200µg) - 2000 UAH": "3 шт"
    },
    "🍄 Грибы Psilocybe": {
        "1г (Microdose) - 350 UAH": "1г",
        "3г (Трип) - 950 UAH": "3г",
        "5г (Героический) - 1500 UAH": "5г"
    }
}

# --- КЭШ ЕЖЕДНЕВНОГО АССОРТИМЕНТА ---
daily_assortment_cache = {}


# --- СОСТОЯНИЯ ДЛЯ FSM ---
class OrderState(StatesGroup):
    waiting_for_city = State()
    waiting_for_district = State()
    waiting_for_product = State()
    waiting_for_product_option = State()
    waiting_for_payment = State()


# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

def get_daily_assortment(district):
    """Возвращает словарь с КАТЕГОРИЯМИ и их рандомными опциями на сегодня."""
    today_str = datetime.now().strftime("%Y-%m-%d")

    if district in daily_assortment_cache and daily_assortment_cache[district]["date"] == today_str:
        return daily_assortment_cache[district]["products"]

    new_assortment = {}

    for category, options in ALL_PRODUCTS.items():
        all_options = list(options.keys())
        num_to_select = random.randint(2, min(5, len(all_options)))
        selected_options = random.sample(all_options, num_to_select)
        new_assortment[category] = selected_options

    daily_assortment_cache[district] = {
        "date": today_str,
        "products": new_assortment
    }

    logging.info(f"🔄 Сгенерирован новый ассортимент для района '{district}'")
    return new_assortment


# --- КЛАВИАТУРЫ ---

def get_cities_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    cities = list(CITIES_DISTRICTS.keys())

    # Добавляем эмодзи для городов
    city_emojis = {
        "Киев": "🏛", "Львов": "🦁", "Одесса": "⚓", "Харьков": "⭐", "Днепр": "🌊",
        "Винница": "🏰", "Житомир": "🏞", "Запорожье": "⚡", "Ивано-Франковск": "🏔",
        "Кропивницкий": "🌻", "Луцк": "🏯", "Николаев": "🚢", "Полтава": "🍐",
        "Ровно": "🎵", "Сумы": "🌳", "Тернополь": "⛲", "Ужгород": "🌸",
        "Херсон": "🌅", "Хмельницкий": "🏭", "Черкассы": "🌲", "Черновцы": "🎭",
        "Чернигов": "⛪", "Кривой Рог": "⛏", "Мариуполь": "🏗", "Северодонецк": "🔬"
    }

    row = []
    for city in cities:
        emoji = city_emojis.get(city, "🏙")
        row.append(InlineKeyboardButton(text=f"{emoji} {city}", callback_data=f"city_{city}"))
        if len(row) == 2:
            keyboard.inline_keyboard.append(row)
            row = []
    if row:
        keyboard.inline_keyboard.append(row)
    return keyboard


def get_districts_keyboard(city):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    districts = CITIES_DISTRICTS.get(city, ["Центральный"])

    for district in districts:
        keyboard.inline_keyboard.append(
            [InlineKeyboardButton(text=f"📍 {district}", callback_data=f"district_{district}")]
        )
    keyboard.inline_keyboard.append(
        [InlineKeyboardButton(text="◀️ Назад к выбору города", callback_data="back_to_cities")]
    )
    return keyboard


def get_products_keyboard(district):
    """Показывает ВСЕ категории товаров."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    for product_name in ALL_PRODUCTS.keys():
        keyboard.inline_keyboard.append(
            [InlineKeyboardButton(text=product_name, callback_data=f"product_{product_name}")]
        )

    keyboard.inline_keyboard.append(
        [InlineKeyboardButton(text="◀️ Назад к районам", callback_data="back_to_districts")]
    )
    return keyboard


def get_product_options_keyboard(district, product_name):
    """Показывает ТОЛЬКО рандомные опции для выбранной категории НА СЕГОДНЯ."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    today_assortment = get_daily_assortment(district)
    options = today_assortment.get(product_name, [])

    if options:
        for option_text in options:
            keyboard.inline_keyboard.append(
                [InlineKeyboardButton(text=f"💰 {option_text}", callback_data=f"option_{product_name}_{option_text}")]
            )
    else:
        keyboard.inline_keyboard.append(
            [InlineKeyboardButton(text="😔 Нет доступных опций", callback_data="none")]
        )

    keyboard.inline_keyboard.append(
        [InlineKeyboardButton(text="◀️ Назад к категориям", callback_data="back_to_products")]
    )
    return keyboard


def get_payment_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить переводом на карту", callback_data="pay_card")],
        [InlineKeyboardButton(text="₿ Оплата через BTC", callback_data="pay_btc")],
        [InlineKeyboardButton(text="◀️ Назад к опциям", callback_data="back_to_options")]
    ])
    return keyboard


# --- ОБРАБОТЧИКИ ---

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer(
        "🔥 <b>Приветствуем, странник!</b> 🔥\n\n"
        "🌈 Добро пожаловать в наш уютный магазинчик — место, где качество встречается с надёжностью!\n\n"
        "✨ <b>Почему выбирают нас:</b>\n"
        "• 🚀 Быстрая доставка по городу\n"
        "• 🎯 Только свежий и проверенный товар\n"
        "• 🤝 Поддержка 24/7\n\n"
        f"📲 По всем вопросам: {OPERATOR_USERNAME}\n\n"
        "👇 <b>Для начала выбери свой город:</b>",
        reply_markup=get_cities_keyboard(),
        parse_mode="HTML"
    )


@dp.callback_query(F.data.startswith('city_'))
async def process_city(callback: types.CallbackQuery, state: FSMContext):
    city = callback.data.replace('city_', '')
    await state.update_data(selected_city=city)
    await callback.answer()

    await callback.message.edit_text(
        text=f"🏙 <b>Твой город:</b> {city}\n\n"
             "📍 Теперь выбери район, где тебе удобно:",
        reply_markup=get_districts_keyboard(city),
        parse_mode="HTML"
    )


@dp.callback_query(F.data == 'back_to_cities')
async def back_to_cities(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    await callback.message.edit_text(
        text="👇 <b>Выбери свой город из списка:</b>",
        reply_markup=get_cities_keyboard(),
        parse_mode="HTML"
    )


@dp.callback_query(F.data.startswith('district_'))
async def process_district(callback: types.CallbackQuery, state: FSMContext):
    district = callback.data.replace('district_', '')
    await state.update_data(selected_district=district)
    await callback.answer()

    await callback.message.edit_text(
        text=f"📍 <b>Район:</b> {district}\n\n"
             "🎁 Выбери категорию товара:",
        reply_markup=get_products_keyboard(district),
        parse_mode="HTML"
    )


@dp.callback_query(F.data == 'back_to_districts')
async def back_to_districts(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    city = user_data.get('selected_city', 'Не выбран')
    await callback.answer()

    await callback.message.edit_text(
        text=f"🏙 <b>Твой город:</b> {city}\n\n"
             "📍 Выбери район:",
        reply_markup=get_districts_keyboard(city),
        parse_mode="HTML"
    )


@dp.callback_query(F.data.startswith('product_'))
async def process_product_selection(callback: types.CallbackQuery, state: FSMContext):
    product_name = callback.data.replace('product_', '')
    user_data = await state.get_data()
    district = user_data.get('selected_district')

    await state.update_data(selected_product=product_name)
    await callback.answer()

    await callback.message.edit_text(
        text=f"🎯 <b>Категория:</b> {product_name}\n\n"
             "⚖️ Выбери подходящий вес:",
        reply_markup=get_product_options_keyboard(district, product_name),
        parse_mode="HTML"
    )


@dp.callback_query(F.data == 'back_to_products')
async def back_to_products(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    district = user_data.get('selected_district', 'Не выбран')
    await callback.answer()

    await callback.message.edit_text(
        text=f"📍 <b>Район:</b> {district}\n\n"
             "🎁 Выбери категорию товара:",
        reply_markup=get_products_keyboard(district),
        parse_mode="HTML"
    )


@dp.callback_query(F.data.startswith('option_'))
async def process_product_option(callback: types.CallbackQuery, state: FSMContext):
    parts = callback.data.split('_', 2)
    product_name = parts[1]
    option_text = parts[2]

    await state.update_data(selected_product_full=f"{product_name} - {option_text}")

    await callback.answer()
    await callback.message.edit_text(
        text=f"✅ <b>Отличный выбор!</b>\n\n"
             f"🛒 <b>Товар:</b> {option_text}\n\n"
             "💳 Выбери способ оплаты:",
        reply_markup=get_payment_keyboard(),
        parse_mode="HTML"
    )


@dp.callback_query(F.data == 'back_to_options')
async def back_to_options(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    product_name = user_data.get('selected_product', 'Не выбрана')
    district = user_data.get('selected_district')

    await callback.answer()
    await callback.message.edit_text(
        text=f"🎯 <b>Категория:</b> {product_name}\n\n"
             "⚖️ Выбери подходящий вес:",
        reply_markup=get_product_options_keyboard(district, product_name),
        parse_mode="HTML"
    )


@dp.callback_query(F.data.startswith('pay_'))
async def process_payment(callback: types.CallbackQuery, state: FSMContext):
    payment_method = "💳 Перевод на карту" if callback.data == 'pay_card' else "₿ Bitcoin (BTC)"
    user_data = await state.get_data()
    city = user_data.get('selected_city', 'Не выбран')
    district = user_data.get('selected_district', 'Не выбран')
    product = user_data.get('selected_product_full', 'Не выбран')

    await callback.answer()
    await callback.message.edit_text(
        text="🎉 <b>Заказ почти оформлен!</b>\n\n"
             "📝 Остался последний шаг:\n\n"
             f"👨‍💼 Свяжись с оператором {OPERATOR_USERNAME}\n"
             "🤝 Он отправит реквизиты и подтвердит заказ!\n\n"
             "✨ <i>Спасибо, что выбрал нас!</i>",
        parse_mode="HTML"
    )

    operator_message = (
        "🛎 <b>НОВЫЙ ЗАКАЗ!</b>\n\n"
        f"👤 <b>Клиент:</b> @{callback.from_user.username or 'нет юзернейма'}\n"
        f"🆔 <b>ID:</b> <code>{callback.from_user.id}</code>\n"
        f"🏙 <b>Город:</b> {city}\n"
        f"📍 <b>Район:</b> {district}\n"
        f"🛒 <b>Товар:</b> {product}\n"
        f"💲 <b>Оплата:</b> {payment_method}\n\n"
        "📞 <b>Свяжись с клиентом для уточнения!</b>"
    )

    try:
        await bot.send_message(OPERATOR_USER_ID, operator_message, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Не удалось отправить сообщение оператору: {e}")
        await callback.message.answer(
            "⚠️ Произошла ошибка при отправке уведомления оператору. Пожалуйста, свяжитесь с ним напрямую."
        )
    await state.clear()


# --- СБРОС КЭША КАЖДЫЙ ДЕНЬ ---
async def reset_daily_cache():
    while True:
        now = datetime.now()
        tomorrow = now + timedelta(days=1)
        midnight = datetime(year=tomorrow.year, month=tomorrow.month, day=tomorrow.day, hour=0, minute=0, second=0)
        seconds_until_midnight = (midnight - now).total_seconds()

        logging.info(f"⏰ Кэш очистится через {seconds_until_midnight:.0f} секунд")
        await asyncio.sleep(seconds_until_midnight)

        daily_assortment_cache.clear()
        logging.info("🔄 Кэш ассортимента очищен! Новый день — новый товар!")


# Запуск бота
async def main():
    # Создаём задачу
    task = asyncio.ensure_future(reset_daily_cache())

    # Добавляем обработчик ошибок
    def handle_task_exception(t):
        if t.exception():
            logging.error(f"Фоновая задача упала: {t.exception()}")

    task.add_done_callback(handle_task_exception)

    try:
        await dp.start_polling(bot)
    finally:
        # Корректно отменяем задачу при остановке
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


if __name__ == '__main__':
    asyncio.run(main())
