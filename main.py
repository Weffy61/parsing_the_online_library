import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
from urllib.parse import unquote, urlsplit


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


def parse_image_url(response):
    soup = BeautifulSoup(response.text, 'lxml')
    relative_path = soup.find(class_='bookimage').find('img')['src']
    path = urljoin('https://tululu.org', relative_path)
    return path


def parse_book_genre(response):
    soup = BeautifulSoup(response.text, 'lxml')
    book_genres = []
    genres = soup.find(id='content').find('span', class_='d_book').find_all('a')
    for genre in genres:
        book_genres.append(genre.text)
    return book_genres


def parse_book_page(response):
    pass


def download_txt(url, filename, folder='books/'):
    os.makedirs(folder, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    normalized_filename = f'{sanitize_filename(filename)}.txt'
    path = os.path.join(folder, normalized_filename)
    with open(path, 'wb') as file:
        file.write(response.content)
    return path


def download_image(url, folder='images/'):
    os.makedirs(folder, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    filename = unquote(urlsplit(url).path).split('/')[-1]
    normalized_filename = f'{sanitize_filename(filename)}'
    path = os.path.join(folder, normalized_filename)
    with open(path, 'wb') as file:
        file.write(response.content)


def download_comments(response, book_id, folder='comments/'):
    os.makedirs(folder, exist_ok=True)
    soup = BeautifulSoup(response.text, 'lxml')
    comments = soup.find_all(class_='texts')
    path = os.path.join(folder, f'{book_id}.txt')
    for comment in comments:
        new_comment = f"{comment.find(class_='black').text}\n"
        with open(path, 'a') as file:
            file.write(new_comment)


def main():
    os.makedirs('books', exist_ok=True)
    for book_num in range(10):
        try:
            book_url = f"https://tululu.org/b{book_num + 1}/"
            txt_url = f'https://tululu.org/txt.php?id={book_num + 1}'
            response_book = check_url_exist(book_url)
            check_for_redirect(response_book)
            book_title = parse_book(response_book)
            response_txt = check_url_exist(txt_url)
            check_for_redirect(response_txt)
            # filename = f'{book_num + 1}. {book_title}'
            # download_txt(txt_url, filename)
            # image_url = parse_image_url(response_book)
            # download_image(image_url)
            download_comments(response_book, book_num)
            book_genres = parse_book_genre(response_book)

        except requests.exceptions.HTTPError as ex:
            print(f'Книга с id {book_num + 1} недоступна, так как {ex}')
            continue


if __name__ == '__main__':
    main()
