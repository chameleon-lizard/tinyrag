import argparse
import main

import src.utils as utils


def _main():
    parser = argparse.ArgumentParser(
        description="Download a web page, extract text, and save to file."
    )
    parser.add_argument("url", type=str, help="The web link to download", required=False)
    parser.add_argument('--query', default='What were the tags for this question?'#'''What the question is about?'''
                        , type=str, help='The question to ask', required=False)
    args = parser.parse_args()

    if not utils.validate_url(args.url):
        parser.error(
            f"'{args.url}' is not a valid URL. Please provide a valid web link."
        )

    print(f"Downloading page: {args.url}")
    html_content = utils.download_page(args.url)

    if html_content is None:
        return 1  # Exit with an error code if download failed

    text = utils.extract_text(html_content)

    c = main.Chatbot(text)
    print_before = not utils.is_gpu_available()

    while True:
        try:
            if args.query is not None:
                question = args.query
            else:
                question = input("Q: ")

            ranked = c.retrieve(question)

            if print_before:
                print()
                utils.print_references(ranked, args.url)
                print("Generating response...")
                print()

            answer = c.send_question(question, ranked)

            print(f"A: {answer}", end="")

            if not print_before:
                print()
                utils.print_references(ranked, args.url)
                print()

            if args.query is not None:
                c.shutdown()
                break
        except (KeyboardInterrupt, EOFError):
            c.shutdown()
            break

if __name__ == "__main__":
    _main()
