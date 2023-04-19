import asyncio
import logging
import os
import random
import tempfile

import requests
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import (
    KeyboardButton,
    ParseMode,
    ReplyKeyboardMarkup,
)
from aiogram.utils.callback_data import CallbackData
from dotenv import load_dotenv

load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"))
API_WEATHER_KEY = os.getenv("API_WEATHER_KEY")
APILayer = os.getenv("APILayer")
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(
    format=(
        "%(asctime)s, %(name)s, %(levelname)s, %(filename)s, %(funcName)s, %(message)s"
    ),
    level=logging.INFO,
)

menu_callback = CallbackData("menu", "command")


@dp.message_handler(commands=["start"])
async def welcome_message(message: types.Message):
    """Обработчик команды start."""
    menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton(text="\U000026C5 Погода"),
        KeyboardButton(text="\U0001F4B5 Курс валют"),
        KeyboardButton(text="\U0001F436 Милые животные"),
        KeyboardButton(text="\U0001F4D2 Опрос"),
    )
    await message.answer(
        "Привет! \U0001F44B \n\nЯ бот, который может выполнять несколько функций. "
        "Напиши '\U000026C5 Погода' для получения погоды в городе.\n"
        "напиши '\U0001F4B5 Курс валют' для конвертации валюты.\n"
        "напиши '\U0001F436 Милые животные' для получения милых фотографий животных.\n"
        "напиши '\U0001F4D2 Опрос' для создания опросов в групповом чате.\n"
        "\nИ не забывай про кнопки, так будет удобней!",
        reply_markup=menu_keyboard,
    )


@dp.message_handler()
async def message(message: types.Message):
    """Обработчик сообщений."""
    if message.text == "\U000026C5 Погода":
        await process_weather_command(message)
    elif message.text == "\U0001F4B5 Курс валют":
        await process_currency_command(message)
    elif message.text == "\U0001F436 Милые животные":
        await cmd_animals_command(message)
    elif message.text == "\U0001F4D2 Опрос":
        await process_polls(message)
    else:
        await message.answer(
            "Я тебя не понимаю! Для получения списка команд нажми: /start"
        )


class WeatherState(StatesGroup):
    """Класс для прогноза погоды."""

    waiting_for_city = State()


@dp.message_handler(commands=["weather"])
async def process_weather_command(message: types.Message):
    """Обработчик сообщения для прогноза погоды."""
    await message.answer("Введи название города:")
    await WeatherState.waiting_for_city.set()


async def get_weather(city, message: types.Message):
    """Осуществляет запросы к API OpenWeather."""
    try:
        response = requests.get(
            f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=5&appid={API_WEATHER_KEY}"
        )
        response = response.json()[0]
    except Exception as error:
        logging.error(
            "Ошибка доступа к API для определения координат!",
            error,
        )
        await message.answer(
            text="\U0001F6AB Название города введено некорректно. Пожалуйста, введи корректное название города!",
        )
    lat = response.get("lat")
    lon = response.get("lon")
    try:
        response = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={API_WEATHER_KEY}&lang=ru"
        ).json()
    except Exception as error:
        logging.error(
            "Ошибка доступа к API для определения погоды!",
            error,
        )
        await message.answer(
            text="\U0001F6AB Неудалось получить координаты города. Пожалуйста, введи корректное название города!",
        )
    weather_description = response["weather"][0]["description"]
    temperature = response["main"]["temp"]
    feels_like = response["main"]["feels_like"]
    humidity = response["main"]["humidity"]
    wind_speed = response["wind"]["speed"]

    return (
        f"В городе {city} сейчас {weather_description} \U000026A1.\n"
        f"Температура \U0001F321: {temperature:.1f}°C, ощущается как {feels_like:.1f}°C \U0001F975.\n"
        f"Влажность \U0001F4A7: {humidity}%, скорость ветра \U0001F32C: {wind_speed:.1f} м/с \U0001F4A8.\n"
    )


@dp.message_handler(state=WeatherState.waiting_for_city)
async def process_weather_city(message: types.Message, state: FSMContext):
    """Отправляет прогноз пользователю."""
    city = message.text
    weather = await get_weather(city, message)
    await message.answer(weather)
    await state.finish()


class ExchangeState(StatesGroup):
    """Клас для конвертации валют."""

    waiting_for_from = State()
    waiting_for_to = State()
    waiting_for_amount = State()


@dp.message_handler(commands=["exchange"])
async def process_currency_command(message: types.Message):
    """Обработчик первого сообщения для конвертации."""
    await message.answer(
        "Введи валюту, из который ты хочешь перевести. Например, EUR:"
    )
    await ExchangeState.waiting_for_from.set()


@dp.message_handler(state=ExchangeState.waiting_for_from)
async def process_currency_from(message: types.Message, state: FSMContext):
    """Обработчик второго сообщения для конвертации."""
    async with state.proxy() as data:
        data["frm"] = message.text
    await message.answer(
        "Введи валюту, в которую ты хочешь перевести. Например, RUB:"
    )
    await ExchangeState.waiting_for_to.set()


@dp.message_handler(state=ExchangeState.waiting_for_to)
async def process_currency_to(message: types.Message, state: FSMContext):
    """Обработчик третьего сообщения для конвертации."""
    async with state.proxy() as data:
        data["to"] = message.text
    await message.answer("Введи сумму для перевода:")
    await ExchangeState.waiting_for_amount.set()


@dp.message_handler(state=ExchangeState.waiting_for_amount)
async def process_currency_amount(message: types.Message, state: FSMContext):
    """Получает все сообщения."""
    async with state.proxy() as data:
        data["amount"] = message.text

    try:
        data = await state.get_data()
        frm = data.get("frm")
        to = data.get("to")
        amount = data.get("amount")
        result = await get_currency(frm, to, amount, message)
        await message.answer(result)
        await state.finish()
    except Exception as error:
        logging.error(
            "Ошибка при обработке команды 'exchange'",
            error,
        )
        await message.answer(
            text="\U0001F6AB Что-то пошло не так! Попробуй еще раз.",
        )
        await state.finish()
        await process_currency_command(message)


async def get_currency(frm, to, amount, message: types.Message):
    """Получает все сообщения и осуществляет запрос к API APILayer."""
    try:
        url = f"https://api.apilayer.com/exchangerates_data/convert?to={to}&from={frm}&amount={amount}"
        headers = {"apikey": APILayer}
        response = requests.request("GET", url, headers=headers).json()
    except Exception as error:
        logging.error(
            "Ошибка доступа к API для конвертации валют!",
            error,
        )
        await message.answer(
            text="\U0001F6AB Что-то пошло не так! Попробуй еще раз.",
        )

    rate = response.get("query")
    frm_rate = rate.get("from")
    to_rate = rate.get("to")
    result = response.get("result")
    return f"{amount} {frm_rate} равны {result:.2f} {to_rate}"


@dp.message_handler(commands=["animals"])
async def cmd_animals_command(message: types.Message):
    """Обработчик команды animals."""
    cat_url = "https://api.thecatapi.com/v1/images/search"
    dog_url = "https://api.thedogapi.com/v1/images/search"
    URL = random.choice([cat_url, dog_url])
    try:
        response = requests.get(URL)
    except Exception as error:
        logging.error("Ошибка при запросе к  API", error)
        await message.answer(
            text="\U0001F6AB Что-то пошло не так! Попробуй еще раз.",
        )
    response = response.json()
    random_animal = response[0].get("url")
    with tempfile.NamedTemporaryFile() as file:
        img_data = requests.get(random_animal).content
        file.write(img_data)
        file.flush()
        with open(file.name, "rb") as photo:
            await bot.send_photo(message.chat.id, photo)


class CreatePollStates(StatesGroup):
    """Класс для создания опросов."""
    question = State()
    number_of_options = State()
    options = State()


@dp.message_handler(commands=["polls"])
async def process_polls(message: types.Message):
    """Обрабатывает сообщение с вопросом к опросу."""
    await message.answer("Введите вопрос для опроса:")
    await CreatePollStates.question.set()


@dp.message_handler(state=CreatePollStates.question)
async def set_question_handler(message: types.Message, state: FSMContext):
    """Обрабатывает сообщение с количеством вариантов ответа."""
    await state.update_data(question=message.text)
    await message.answer("Введите количество вариантов ответа:")
    await CreatePollStates.number_of_options.set()


@dp.message_handler(state=CreatePollStates.number_of_options)
async def set_number_of_options_handler(
    message: types.Message, state: FSMContext
):
    """Обрабатывает сообщение с вариантоми ответов."""
    await state.update_data(number_of_options=int(message.text))
    await message.answer(
        "Введите варианты ответа (каждый вариант ответа на новой строке):",
        parse_mode=ParseMode.HTML,
    )
    await CreatePollStates.options.set()


@dp.message_handler(state=CreatePollStates.options)
async def set_options_handler(message: types.Message, state: FSMContext):
    """Получает все сообщения и создает опрос."""
    options = message.text.split("\n")
    data = await state.get_data()
    question = data.get("question")
    number_of_options = data.get("number_of_options")

    if len(options) != number_of_options:
        await message.answer(
            "\U0001F6AB Количество вариантов ответа не совпадает с введенным числом"
        )
        return

    poll_options = [types.PollOption(text=option) for option in options]

    poll = types.Poll(
        question=question,
        options=poll_options,
        is_anonymous=True,
        allows_multiple_answers=False,
    )
    await message.answer_poll(
        question=poll.question,
        options=[option.text for option in poll.options],
        is_anonymous=poll.is_anonymous,
        allows_multiple_answers=poll.allows_multiple_answers,
    )

    await state.finish()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
