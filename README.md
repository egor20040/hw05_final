# Yatube - социальная сеть для публикации блогов.

![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)

## Описание проекта:
Приложение с авторизацией на Django, сменой и восстановлением пароля через почту, чтением из БД и записью в неё, генерацией индивидуальных страниц пользователей. Настроена пагинация постов и кеширование. Реализованы тесты , проверяющие работу приложения.
После регистрации можно:
- создавать посты;
- прикреплять изображения;
- подписываться/отписываться на авторов; 
- оставлять к постам комментарии
- удалять/изменять посты (только авторам)

## Запуск проекта

Клонируйте репозиторий: 
 
``` 
https://github.com/emuhich/hw05_final.git
``` 

Перейдите в папку проекта в командной строке:

``` 
cd hw05_final
``` 

Создайте и активируйте виртуальное окружение:

``` 
python -m venv venv
``` 
``` 
venv/Scripts/activate
``` 

Установите зависимости из файла *requirements.txt*: 
 
``` 
pip install -r requirements.txt
``` 


Выполните миграции и соберите статику проекта: 
 
``` 
python manage.py makemigrations
``` 
``` 
python manage.py migrate
``` 

Запустите сервер:
``` 
python manage.py runserver
``` 
