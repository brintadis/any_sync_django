# Any-Sync

Сервис для синхронизации и бэкапа плейлистов и треков из различных музыкальных сервисов.
С помощью библиотек ([spotipy](https://github.com/plamere/spotipy), [yandex-music-api](https://github.com/MarshalX/yandex-music-api)) получаем данные по трекам и отправляем их в БД, затем есть возможность синхронизировать его на другом музыкальном сервисе.

## Поддерживаемые музыкальные сервисы

- Spotify
- Yandex-Music
- в разработке Apple Music

## Сборка репозитория и локальный запуск
Скачайте проект с github:

```
git clone https://github.com/brintadis/any-sync.git
```

Создайте виртуальное окружение и установите зависимости:
```
pip install -r requirments.txt
```

## Запуск проекта
Для корректной работы Spotify, нужно установить зависимости, предварительно создав приложение в [Spotify Dashboard](https://developer.spotify.com/dashboard/).

<img src= "https://imgur.com/hzTnqk6.png" width = "480" height = "360">

На этой странице вам необходимо указать Redirect URIs и точно такой же redirect указать в файле ```webapp/spotify/spotify.py``` в переменной ```REDIRECT_URI```. На этой же странице вы получаете ```Client ID``` и ```Client Secret``` своего Spotify приложения и устанавливаете зависимости в ```Dockerfile```.

```
ENV SPOTIFY_CLIENT_ID=Your Spotify App Client ID
ENV SPOTIFY_CLIENT_SECRET=Your Spotify App Client Secret
```
В файле docker-compose.yml укажите ключ проекта:
```
- FLASK_SECRET=Your unique flask app secret key
```

### Указываем путь к базе данных(опционально)
Путь к базе данных уже указан. Изменяйте при необходимости
файл ```webapp/config.py```
```
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:password@db:5432/playlst'
```
### Запуск сервера
Для запуска сервера в Docker нужно сделать билд в корне проекта с запущенным приложением [Docker desktop](https://www.docker.com/get-started/) и выполнить ряд следующих команд:
```
docker-compose build
docker-compose up
```
Для инициализации базы данных нужно узнать ID docker контейнера нашего приложения, для этого открываем новую консоль и из корня проекта вызываем:
```
docker ps
```
Здесь вы должны видеть примерно следующее(id и др. могут различаться):
```
CONTAINER ID   IMAGE                               COMMAND                  CREATED              STATUS              PORTS                              NAMES
d890ca35bb46   redis:alpine                        "docker-entrypoint.s…"   About a minute ago   Up About a minute   6379/tcp                           any-sync-redis-1
94cc8ad5f9b1   postgres:13-alpine                  "docker-entrypoint.s…"   About a minute ago   Up About a minute   0.0.0.0:5432->5432/tcp             any-sync-db-1
8e5ab52a1fc0   any-sync_celery                     "celery -A webapp.ta…"   About a minute ago   Up About a minute                                      any-sync-celery-1
876f1a708e6c   selenium/standalone-chrome:latest   "/opt/bin/entry_poin…"   About a minute ago   Up About a minute   0.0.0.0:4444->4444/tcp, 5900/tcp   any-sync-selenium-1
1fb028204369   any-sync_webapp                     "flask run -h 0.0.0.…"   About a minute ago   Up About a minute   0.0.0.0:5000->5000/tcp             any-sync-webapp-1
```
Здесь нам нужно скопировать id контейнера any-sync_webapp, в моем случае ```1fb028204369```.
Теперь, когда у нас есть id, нужно зайти в bash внутри контейнера.
Не закрывая терминал вызывайте следующую команду:
```
docker exec -it 1fb028204369 bash
```
Внутри bash вызываем файл ```create_db.py```:
```
python3 create_db.py
```