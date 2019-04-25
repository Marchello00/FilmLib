# FilmLib bot
Telegram бот для поиска фильмов и составления своей фильмотеки. 
Доступен как @filmlib_bot
## Запуск своего бота
Для работы необходим токен бота, который можно получить у @BotFather в Telegram
 ([создание бота](https://core.telegram.org/bots#3-how-do-i-create-a-bot)), 
 apiKey для [omdbapi](http://www.omdbapi.com), а так же url вашей базы данных
 
Можно добавить эти переменные в переменные окружения с именами:
* TOKEN для токена бота
* APIKEY для apikey с omdbapi
* DATABASE_URL для адреса базы данных

А можно написать и в формате json записать в него те е данные:
* token для токена бота
* apikey для apikey с omdbapi
* db_url для адреса базы данных

Пример JSON-файла:
```
{
  "apikey": "123a4567",
  "token": "123456789:AAA-BBBcOdD1efF3GhigkLMNOPQ1rS8t59U",
  "db_url": "sqlite:///db.sqlite"
}
```

Для запуска бота в терминале:
```
$ python3 bot.py
```

Если вы выбрали JSON-файл, то запустите с параметром `-c` и путём до
вашего JSON-файла, например:
```
$ python3 run.py -c config.json
```

Для запуска в режиме отладки используйте параметр `-d`:
```
$ python3 run.py -d
```

 