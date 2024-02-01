import argparse
import json
import os
import time
from pathlib import Path
from typing import NamedTuple
from urllib.parse import urljoin, urlsplit, unquote

import requests
from bs4 import BeautifulSoup

from parse_tululu_book_id import get_book, check_for_redirect, download_image, download_book


class BooksParser(NamedTuple):
    start_page: int
    end_page: int
    dest_folder: str
    skip_img: bool
    skip_txt: bool


def parse_args():

    parser = argparse.ArgumentParser(
        description='Загрузка книг в указанном диапазоне'
    )
    parser.add_argument('-s', '--start_page', help='Стартовая страница', type=int, default=700)
    parser.add_argument('-e', '--end_page', help='Последняя страница', type=int, default=701)
    parser.add_argument('-df', '--dest_folder', help='Каталог загрузки', default=Path.cwd())
    parser.add_argument('-i', '--skip_imgs', help='Не скачивать картинки',  action='store_true')
    parser.add_argument('-t', '--skip_txt', help='Не скачивать книги',  action='store_true')

    args = parser.parse_args()
    book_args = BooksParser(
        start_page=args.start_page,
        end_page=args.end_page + 1,
        dest_folder=args.dest_folder,
        skip_img=args.skip_imgs,
        skip_txt=args.skip_txt
    )
    return book_args


def get_last_page_num():
    url = urljoin('https://tululu.org', 'l55/')
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    soup = BeautifulSoup(response.text, 'lxml')
    last_page_num = int(soup.select('#content .npage')[-1].text)
    return last_page_num + 1


def get_links(url, page_num):
    links = []
    response = requests.get(urljoin(url, str(page_num)))
    response.raise_for_status()
    check_for_redirect(response)
    soup = BeautifulSoup(response.text, 'lxml')
    books = soup.select('.d_book')
    for link in books:
        links.append(urljoin(url, link.select_one('a')['href']))
    return links


def download_comments(comments, book_id, dest_folder, folder='comments/'):
    comments_folder = os.path.join(dest_folder, folder)
    os.makedirs(comments_folder, exist_ok=True)
    path = os.path.join(comments_folder, f'{book_id}.txt')
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
        'book_path': os.path.join('books', filename),
        'comments': comments,
        'genres': genres

    }
    return book, filename


def write_json(file_name, books, dest_folder):
    json_path = os.path.join(dest_folder, file_name)
    with open(json_path, 'w', encoding='utf-8') as file:
        json.dump(books, file, ensure_ascii=False, indent=2)


def main():
    books = []
    book_args = parse_args()
    dest_folder = book_args.dest_folder
    if book_args.end_page:
        last_page_num = book_args.end_page
    else:
        last_page_num = get_last_page_num()
    total_links = []
    category_url = urljoin('https://tululu.org', 'l55/')
    for page_num in range(book_args.start_page, last_page_num):
        try:
            total_links.extend(get_links(category_url, page_num))
        except (requests.exceptions.HTTPError, requests.exceptions.MissingSchema,
                requests.exceptions.ConnectionError) as ex:
            print(f'Страница {page_num} недоступна, так как {ex}')
            time.sleep(5)
            continue

    for book_url in total_links:
        book_id = unquote(urlsplit(book_url).path).split('/')[1].lstrip('b')
        try:
            soup = get_book(book_url)
            book, filename = parse_book_page(soup, book_id, book_url)
            image_url = book.get('image_src')
            if not book_args.skip_txt:
                download_book(
                    book_id,
                    filename,
                    folder=os.path.join(dest_folder, 'books/'))
            if not book_args.skip_img:
                download_image(
                    image_url,
                    folder=os.path.join(dest_folder, 'images/'))
            download_comments(book.get('comments'), book_id, dest_folder)
            books.append(book)
        except (requests.exceptions.HTTPError, requests.exceptions.MissingSchema,
                requests.exceptions.ConnectionError) as ex:
            print(f'Книга с id {book_id} недоступна, так как {ex}')
            time.sleep(5)
            continue
    write_json('books.json', books, dest_folder)


if __name__ == '__main__':
    main()
