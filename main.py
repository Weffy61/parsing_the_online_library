import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_url_exist(url):
    response = requests.get(url, allow_redirects=True)
    response.raise_for_status()
    return response


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError('выполнена переадресация со страницы книги')


def parse_book(response):
    soup = BeautifulSoup(response.text, 'lxml')
    title = soup.find('h1').text.split('::')[0].strip()
    return title


def download_txt(url, filename, folder='books/'):
    os.makedirs(folder, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    normalized_filename = f'{sanitize_filename(filename)}.txt'
    path = os.path.join(folder, normalized_filename)
    with open(path, 'wb') as file:
        file.write(response.content)
    return path


def main():
    DIR_NAME = 'books'
    os.makedirs(DIR_NAME, exist_ok=True)
    for book_num in range(10):
        try:
            book_url = f"https://tululu.org/b{book_num + 1}/"
            txt_url = f'https://tululu.org/txt.php?id={book_num + 1}'
            response_book = check_url_exist(book_url)
            check_for_redirect(response_book)
            book_title = parse_book(response_book)
            response_txt = check_url_exist(txt_url)
            check_for_redirect(response_txt)
            filename = f'{book_num + 1}. {book_title}'
            download_txt(txt_url, filename)
        except requests.exceptions.HTTPError as ex:
            # print(f'Книга с id {book_num + 1} недоступна, так как {ex}')
            print(f'Книга с id {book_num + 1} недоступна, так как {ex}')
            continue


if __name__ == '__main__':
    main()
