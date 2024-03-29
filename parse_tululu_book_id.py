import time
import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
from urllib.parse import unquote, urlsplit
import argparse


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError('выполнена переадресация со страницы книги')


def download_book(book_id, filename, folder='books/'):
    payload = {
        'id': book_id
    }
    download_url = f'https://tululu.org/txt.php'
    response = requests.get(download_url, params=payload)
    response.raise_for_status()
    check_for_redirect(response)
    os.makedirs(folder, exist_ok=True)
    normalized_filename = f'{sanitize_filename(filename)}.txt'
    path = os.path.join(folder, normalized_filename)
    with open(path, 'wb') as file:
        file.write(response.content)
    return path


def download_image(url, folder='images/'):
    os.makedirs(folder, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    filename = unquote(urlsplit(url).path).split('/')[-1]
    normalized_filename = f'{sanitize_filename(filename)}'
    path = os.path.join(folder, normalized_filename)
    with open(path, 'wb') as file:
        file.write(response.content)


def download_comments(comments, book_id, folder='comments/'):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f'{book_id}.txt')
    book_comments = []
    for comment in comments:
        book_comments.append(comment)
    if book_comments:
        with open(path, 'w') as file:
            file.writelines(book_comments)


def parse_book_page(soup, book_id, book_url):
    title, author = soup.select_one('h1').text.split('::')
    img_relative_path = soup.select_one('.bookimage img')['src']
    image_url = urljoin(book_url, img_relative_path)
    genres = [genre.text for genre in soup.select('#content span.d_book a')]
    filename = f'{book_id}. {title.strip()}'
    comments = [comment.text for comment in soup.select('.texts .black')]

    book = {
        'title': title.strip(),
        'author': author.strip(),
        'image_src': image_url,
        'genres': genres,
        'book_path': os.path.join('books', filename),
        'comments': comments
    }

    return book, filename


def get_book(book_url):
    response = requests.get(book_url)
    response.raise_for_status()
    check_for_redirect(response)
    soup = BeautifulSoup(response.text, 'lxml')
    return soup


def parse_book_ids():
    parser_book_id = argparse.ArgumentParser(
        description='Загрузка книги в указанном диапазоне'
    )
    parser_book_id.add_argument('start_id', help='ID начальной книги', type=int, nargs='?', default=1)
    parser_book_id.add_argument('end_id', help='ID конечной книги', type=int, nargs='?', default=10)
    book_args = parser_book_id.parse_args()
    return book_args.start_id, book_args.end_id


def main():
    start_id, end_id = parse_book_ids()
    for book_num in range(start_id, end_id + 1):
        try:
            book_url = f"https://tululu.org/b{book_num}/"
            soup = get_book(book_url)
            book, filename = parse_book_page(soup, book_num, book_url)
            image_url = book['image_src']
            download_book(book_num, filename)
            download_image(image_url)
            download_comments(book['comments'], book_num)
            print(f'Название: {book["title"]}')
            print(f"Жанр(ы): {book['genres']}")
            print(f'Автор: {book["author"]}')

        except (requests.exceptions.HTTPError, requests.exceptions.MissingSchema,
                requests.exceptions.ConnectionError) as ex:
            print(f'Книга с id {book_num} недоступна, так как {ex}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()
