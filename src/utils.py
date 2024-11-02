import openai
import requests
import urllib.parse


from bs4 import BeautifulSoup


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


def send_question(
    prompt: str,
    model: str,
    api_link: str,
    token: str,
    temperature: float,
    max_tokens: int,
):
    client = openai.OpenAI(
        api_key=token,
        base_url=api_link,
    )

    messages = []
    messages.append({"role": "user", "content": prompt})

    response_big = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        n=1,
        max_tokens=max_tokens,
    )

    response = response_big.choices[0].message.content

    return response
