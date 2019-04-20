# FilmLib bot

## config.json
В файле в формате JSON должны быть записаны telegram_token - токен бота в telegram,
 и omdb_apikey - apikey для OMDb API.
 
 ## Deploy(DEV)
 heroku ps:scale worker=1 -a my-film-bot
 heroku logs --tail -a my-film-bot