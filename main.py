import requests
import os
from bs4 import BeautifulSoup


def get_book(book_id):
    url = f"https://tululu.org/b{book_id + 1}/"
    response = requests.get(url, allow_redirects=True)
    response.raise_for_status()
    return response


def download_book(book_id):
    payload = {
        'id': book_id + 1
    }

    url = "https://tululu.org/txt.php"
    response = requests.get(url, params=payload)
    response.raise_for_status()
    file_name = f'id_{book_id + 1}.txt'
    with open(f'books/{file_name}', 'wb') as file:
        file.write(response.content)


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError('выполнена переадресация со страницы книги')


def parse_book(response):
    soup = BeautifulSoup(response.text, 'lxml')
    title, author = soup.find('h1').text.split('::')
    print(f'Заголовок: {title.strip()}')
    print(f'Автор: {author.strip()}')


def main():
    DIR_NAME = 'books'
    os.makedirs(DIR_NAME, exist_ok=True)
    for book_num in range(1):
        try:
            response = get_book(book_num)
            check_for_redirect(response)
            parse_book(response)
            # download_book(book_num)
        except requests.exceptions.HTTPError as ex:
            print(f'Книга с id {book_num + 1} недоступна, так как {ex}')
            continue


if __name__ == '__main__':
    main()
