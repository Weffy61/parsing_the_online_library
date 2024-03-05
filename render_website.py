import json
import os
from math import ceil

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def on_reload():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('template.html')

    with open('books.json', 'r') as file:
        pages = json.load(file)
    os.makedirs('pages', exist_ok=True)
    page_count = ceil(len(pages) / 20)

    for page_num, books in enumerate(chunked(pages, 20)):
        context = [
            {
                'title': book.get('title'),
                'author': book.get('author'),
                'image_src': book.get('image_src'),
                'book_path': book.get('book_path'),
                'page_num': page_num + 1,
                'page_count': page_count
            } for book
            in books]

        rendered_page = template.render(context=context)

        with open(f'pages/index{page_num + 1}.html', 'w', encoding="utf8") as file:
            file.write(rendered_page)


def main():
    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='.')


if __name__ == '__main__':
    main()
