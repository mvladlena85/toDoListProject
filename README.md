# TODOList: описание проекта
Дипломная работа курса **"Профессия Python разработчик 2.0"**. </br>
Многопользовательское приложение планировщик задач.
В проекте реализовано 3 объекта:
- доска
- категория
- цель

**Доска** - пространство, где пользователь может создавать свои цели (задачи) и распределять их 
по категориям. Автор доски может поделиться ею с другими пользователями, выдав им права:
- владелец - полный доступ к доске, как и у ее автора
- редактор - может редактировать и создавать новые цели 
- читатель - может только просматривать данные доски. </br>

Доска делится на 3 колонки по статусам:
- К выполнению — цели, которые пользователь просто складывает, но не приступает к ним (некоторого рода «бэклог»).
- В работе — цели, которые пользователь в данный момент пытается достичь.
- Выполнено — цели, которые были достигнуты.

**Категория** - группа целей, объединенных по какому-либо признаку. Категория привязывается к конкретной доске.

**Цель** - задача/задание, которое предстоит выполнить. Содержит поля:
- название - краткое описание цели
- описание - подробное описание
- приоритет:
  - низкий,
  - средний,
  - высокий,
  - критический.
- дата дедлайна
- категория
- статус:
  - к выполнению
  - в работе
  - выполнено


Телеграм-бот позволяет пользователю просматривать цели, которые он создал, а так же создавать новые.

## Cтек 
- Python 3.10, 
- Django 4.1.6, 
- Postgres
Полный список: requirements.txt

## Фронт
Код фронта: sermalenk/skypro-front:lesson-38

## Переменные окружения
### Django secret key
SECRET_KEY - секретный ключ джанго
### База данных Postgres
DB_USER - имя пользователя БД </br>
DB_PASSWORD - пароль для пользователя БД </br>
DB_DATABASE - название базы </br>
DB_HOST - ip/host name </br>
DB_PORT - порт </br>
DATABASE_URL - url Для подключения к БД: postgres://<DB_USER>:<DB_PASSWORD>@<DB_HOST>:<DB_PORT>/<DB_DATABASE>
### Авторизация через соц. сеть VK
SOCIAL_AUTH_VK_OAUTH2_KEY - ID приложения	 </br>
SOCIAL_AUTH_VK_OAUTH2_SECRET - защищённый ключ </br>
### Бот
BOT_TOKEN - токен для доступа к HTTP API


## Где посмотреть
Адрес сайта: http://mvladlena.ga/auth </br>
Телеграм-бот: https://t.me/SkyproToDoListProdBot






