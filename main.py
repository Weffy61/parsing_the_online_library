import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
from urllib.parse import unquote, urlsplit
import argparse


def get_response(url, payload=None):
    response = requests.get(url, allow_redirects=True, params=payload)
    response.raise_for_status()
    return response


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError('выполнена переадресация со страницы книги')


def download_book(book_id, filename, folder='books/'):
    payload = {
        'id': book_id
    }
    download_url = f'https://tululu.org/txt.php'
    response = get_response(download_url, payload=payload)
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
    response = get_response(url)
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
    for comment in comments:
        book_comment = f"{comment.find(class_='black').text}\n"
        with open(path, 'a') as file:
            file.write(book_comment)


def parse_book_genre(response):
    soup = BeautifulSoup(response.text, 'lxml')
    book_genres = []
    genres = soup.find(id='content').find('span', class_='d_book').find_all('a')
    for genre in genres:
        book_genres.append(genre.text)
    return book_genres


def parse_book_page(soup, book_id):
    title, author = soup.find('h1').text.split('::')
    img_relative_path = soup.find(class_='bookimage').find('img')['src']
    image_url = urljoin('https://tululu.org', img_relative_path)
    genres = [genre.text for genre in soup.find(id='content').find('span', class_='d_book').find_all('a')]
    filename = f'{book_id}. {title.strip()}'
    comments = soup.find_all(class_='texts')

    book = {
        'title': title.strip(),
        'author': author.strip(),
        'image_url': image_url,
        'genres': genres,
        'filename': filename,
        'comments': comments
    }
    return book


def get_book(book_id):
    book_url = f"https://tululu.org/b{book_id}/"
    response = get_response(book_url)
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
            soup = get_book(book_num)
            book = parse_book_page(soup, book_num)
            filename = book['filename']
            image_url = book['image_url']
            download_book(book_num, filename)
            download_image(image_url)
            download_comments(book['comments'], book_num)
            print(f'Название: {book["title"]}')
            print(f'Автор: {book["author"]}')

        except (requests.exceptions.HTTPError, requests.exceptions.MissingSchema) as ex:
            print(f'Книга с id {book_num} недоступна, так как {ex}')
            continue


if __name__ == '__main__':
    main()
