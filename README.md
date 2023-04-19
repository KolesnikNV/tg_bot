Проект представляет собой тестовое задание на ваксию разработчика

Как запустить проект:

```git clone git@github.com:Nkoles-stack/tg_bot.git```
```cd tg_bot```

Cоздать и активировать виртуальное окружение:

```python3 -m venv env```
```source env/bin/activate```
```python3 -m pip install --upgrade pip```

Установить зависимости из файла requirements.txt:

```pip install -r requirements.txt```

Создать файл .env и добавить туда ключи API для сервисов Telegram, OpenWeather и APILayer

**OpenWeather - https://home.openweathermap.org/**
**APILayer - https://apilayer.com/**

Бот умеет отправлять информацию о погоде, конвертировать валюту, отправлять фотографии кошек и собак, создавать опросы.
