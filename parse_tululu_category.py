import json
import os
import time
from urllib.parse import urljoin, urlsplit, unquote

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def get_book(book_url):
    response = requests.get(book_url)
    check_for_redirect(response)
    soup = BeautifulSoup(response.text, 'lxml')
    return soup


def get_links(category_id, page_count):
    url = f'https://tululu.org/{category_id}/'
    links = []
    for page in range(page_count + 1):
        response = requests.get(urljoin(url, str(page)))
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        books = soup.select('.d_book')
        for link in books:
            links.append(urljoin('https://tululu.org', link.select_one('a')['href']))
    return links


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError('выполнена переадресация со страницы книги')


def download_comments(comments, book_id, folder='comments/'):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f'{book_id}.txt')
    book_comments = []
    for comment in comments:
        book_comments.append(comment)
    if book_comments:
        with open(path, 'w') as file:
            file.writelines(book_comments)


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


def write_json(file_path, books):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(books, file, ensure_ascii=False, indent=2)


def main():
    category = {
        'Научная фантастика': 'l55'
    }
    books = []
    total_links = get_links(category.get('Научная фантастика'), 1)
    for book_url in total_links:
        book_id = unquote(urlsplit(book_url).path).split('/')[1].lstrip('b')
        try:
            soup = get_book(book_url)
            book, filename = parse_book_page(soup, book_id, book_url)
            books.append(book)
            image_url = book.get('image_src')
            download_book(book_id, filename)
            download_image(image_url)
            download_comments(book.get('comments'), book_id)
        except (requests.exceptions.HTTPError, requests.exceptions.MissingSchema,
                requests.exceptions.ConnectionError) as ex:
            print(f'Книга с id {book_id} недоступна, так как {ex}')
            time.sleep(5)
            continue
    write_json('books.json', books)


if __name__ == '__main__':
    main()
