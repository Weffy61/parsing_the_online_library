import requests
import os


def get_book(book_id):
    payload = {
        'id': book_id + 1
    }


    url = "https://tululu.org/txt.php"

    response = requests.get(url, params=payload, allow_redirects=True)
    response.raise_for_status()
    return response


def download_book(response, book_id):
    file_name = f'id_{book_id + 1}.txt'
    with open(f'books/{file_name}', 'wb') as file:
        file.write(response.content)


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError('выполнена переадресация со страницы книги')


def main():
    DIR_NAME = 'books'
    os.makedirs(DIR_NAME, exist_ok=True)
    for book_num in range(10):
        try:
            response = get_book(book_num)
            check_for_redirect(response)
            download_book(response, book_num)
        except requests.exceptions.HTTPError as ex:
            print(f'Книга с id {book_num + 1} недоступна, так как {ex}')
            continue


if __name__ == '__main__':
    main()
