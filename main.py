import requests
import os


def download_books():
    for book_num in range(10):
        payload = {
            'id': book_num + 1
        }

        file_name = f'{book_num + 1}.txt'
        url = "https://tululu.org/txt.php"

        response = requests.get(url, params=payload)
        response.raise_for_status()
        with open(f'books/{file_name}', 'wb') as file:
            file.write(response.content)


def main():
    os.makedirs("books", exist_ok=True)
    download_books()


if __name__ == '__main__':
    main()
