![Python Version](https://img.shields.io/badge/python-blue)
![Aiogram](https://img.shields.io/badge/aiogram-orange)
![Telegram](https://img.shields.io/badge/Telegram-%40your_telegram_username-blue)
![OpenWeather API](https://img.shields.io/badge/OpenWeather%20API-green)
![APILayer API](https://img.shields.io/badge/APILayer%20API-green)

# Проект "Многофункциональный бот"
Проект представляет собой многофункционального бота на платформе Telegram. Он предоставляет возможность получать информацию о погоде, конвертировать валюту, просматривать милые фотографии животных и создавать опросы в групповом чате.

Установка и запуск
Установите зависимости, указанные в файле requirements.txt, выполнив команду:
```pip install -r requirements.txt```

Создайте файл .env в корневой директории проекта и добавьте в него следующие переменные окружения:
```BOT_TOKEN=<ваш_токен_бота>
API_WEATHER_KEY=<ключ_API_OpenWeather>
APILayer=<ключ_API_APILayer>```

Запустите бота, выполнив команду:
```python main.py```

Команды бота
/start - запуск бота и вывод списка команд.
\U000026C5 Погода - получение погоды в заданном городе.
\U0001F4B5 Курс валют - конвертация валюты.
\U0001F436 Милые животные - получение случайной фотографии милого животного.
\U0001F4D2 Опрос - создание опроса в групповом чате.
Используемые API
API OpenWeather (v1.0) - для получения данных о погоде.
API APILayer (v1.0) - для конвертации валют.
