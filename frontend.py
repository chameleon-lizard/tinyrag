import argparse
import urllib.parse
import requests
from bs4 import BeautifulSoup
import main


def validate_url(url):
    try:
        result = urllib.parse.urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def download_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.text
    except requests.exceptions.RequestException as err:
        print(f"Error downloading page: {err}")
        return None


def extract_text(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text()


def _main():
    parser = argparse.ArgumentParser(
        description="Download a web page, extract text, and save to file."
    )
    parser.add_argument("url", type=str, help="The web link to download")
    args = parser.parse_args()

    if not validate_url(args.url):
        parser.error(
            f"'{args.url}' is not a valid URL. Please provide a valid web link."
        )
        return 1  # Exit with an error code

    html_content = download_page(args.url)
    if html_content is None:
        return 1  # Exit with an error code if download failed

    text = extract_text(html_content)

    with open("file.txt", "w", encoding="utf-8") as file:
        file.write(text)

    c = main.Chatbot(text)
    while True:
        question = input("Q: ")
        answer, documents = c.send_question(question)

        print(f"A: {answer}", end="")
        print(
            "References: "
            + "\n".join(
                f"Doc {idx}, sim {doc[1]:.2f}: {doc[0][:50]}..."
                for idx, doc in enumerate(documents)
            )
        )
        print()


if __name__ == "__main__":
    _main()
