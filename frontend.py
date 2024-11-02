import argparse
import main

import src.utils as utils


def _main():
    parser = argparse.ArgumentParser(
        description="Download a web page, extract text, and save to file."
    )
    parser.add_argument("url", type=str, help="The web link to download")
    args = parser.parse_args()

    if not utils.validate_url(args.url):
        parser.error(
            f"'{args.url}' is not a valid URL. Please provide a valid web link."
        )
        return 1  # Exit with an error code

    html_content = utils.download_page(args.url)
    if html_content is None:
        return 1  # Exit with an error code if download failed

    text = utils.extract_text(html_content)

    c = main.Chatbot(text)
    while True:
        question = input("Q: ")
        answer, documents = c.send_question(question)

        print(f"A: {answer}", end="")
        print(
            "References: \n"
            + "\n".join(
                f"Doc {idx}, sim {doc[1]:.2f}: {doc[0][:50]}..."
                for idx, doc in enumerate(documents)
            )
        )
        print()


if __name__ == "__main__":
    _main()
