import json

from livereload import Server
from jinja2 import Environment, FileSystemLoader, select_autoescape


def on_reload():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('template.html')

    with open('books.json', 'r') as file:
        books = json.load(file)

    context = [
        {
            'title': book.get('title'),
            'author': book.get('author'),
            'image_src': book.get('image_src')

        } for book
        in books]

    rendered_page = template.render(context=context)

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)


def main():
    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='.')


if __name__ == '__main__':
    main()
