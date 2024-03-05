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

### Парсинг книг по id

```commandline
python parse_tululu_book_id.py --start_id --end_id
```

Аргументы:
Аргументы являются диапазоном номеров книг от и до.
- --start_id - начальный номер.
- --end_id - конечный номер(включительно).

Например:

```commandline
python parse_tululu_book_id.py 22 30
```

Данный пример, скачает книги в диапазоне от 22 до 30.

Также вы можете запустить скрипт без аргументов в ознакомитеном варианте:

```commandline
python parse_tululu_book_id.py
```

Таким образом вы скачаете книги в диапазоне от 1 до 10.

### Парсинг книг по категориям

```commandline
python parse_tululu_category.py --start_page --end_page --dest_folder --skip_imgs --skip_txt
```

Аргументы:
Аргументы являются диапазоном номеров книг от и до.
- --start_id - стартовая страница.
- --end_id - конечная страница(включительно). По-умолчанию является последней страницей категории.
- --dest_folder - каталог загрузки файлов.
- --skip_imgs - пропуск изображений.
- --skip_txt - пропуск книг.

Например:

```commandline
python parse_tululu_category.py --start_page 20 --end_page 25 --dest_folder /opt/my-library/ --skip_imgs
```

Данный пример, скачает книги с 20 страницы по 25, загрузка произойдет в каталог `my-library`, обложки книг скачиваться
не будут.
Также вы можете запустить скрипт без аргументов в ознакомитеном варианте:

```commandline
python parse_tululu_category.py
```

Таким образом вы скачаете книги с 700 по 701 страницу.

### Генерация шаблонов

Для того, чтобы сгенерировать свои html шаблоны:

```shell
python3 render_website.py
```

Страницы сайта будут скачаны в каталог `pages`, расположенный в корневой директории.

Пример сайта: https://weffy61.github.io/parsing_the_online_library/
## Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).
