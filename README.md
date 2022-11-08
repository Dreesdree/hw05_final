# hw05_final

[![CI](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml)

Учебный проект от Яндекс.Практикум, представляет собой собственный блог с системой подписок и коментариев, проект покрыт тестами и прошел код ревью.

Стек технологий: Python3 Django Pytest Pillow Bootstrap

Установка: Выполнить pip install -r requirements.txt Выполнить python3 manage.py runserver

Продолжение заданий hw02_community, hw03_forms по созданию социальной сети yatube.

Далее постановка задания из курса.

## Инструкции по установке
***- Клонируйте репозиторий:***
```
git clone git@github.com:Dreesdree/hw05_final.git
```

***- Установите и активируйте виртуальное окружение:***
- для MacOS
```
python3 -m venv venv
```
- для Windows
```
python -m venv venv
source venv/bin/activate
source venv/Scripts/activate
```

***- Установите зависимости из файла requirements.txt:***
```
pip install -r requirements.txt
```

***- Примените миграции:***
```
python manage.py migrate
```

***- В папке с файлом manage.py выполните команду:***
```
python manage.py runserver
```
