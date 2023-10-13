# Парсер книг с сайта tululu.org
Данный скрипт скачивает книги с [tululu](https://tululu.org).

## Установка

```commandline
git clone https://github.com/Weffy61/parsing_the_online_library.git
```

## Установка зависимостей

Переход в директорию с исполняемым файлом

```commandline
cd parsing_the_online_library
```

Установка
```commandline
pip install -r requirements.txt
```

## Запуск

```commandline
python main.py --start_id --end_id
```

Аргументы:  
Аргументы являются диапазоном номеров книг от и до.
- --start_id - начальный номер.
- --end_id - конечный номер(включительно).  

Например:

```commandline
python main.py 22 30
```

Данный пример, скачает книги в диапазоне от 22 до 30.

Также вы можете запустить скрипт без аргументов в ознакомитеном варианте:

```commandline
python main.py
```

Таким образом вы скачаете книги в диапазоне от 1 до 10.

## Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).
