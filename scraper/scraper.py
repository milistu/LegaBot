import argparse
import json
from pathlib import Path
from typing import Dict, List, Literal

import requests
from bs4 import BeautifulSoup
from loguru import logger
from tqdm.auto import tqdm
from tqdm.contrib.logging import tqdm_logging_redirect


def check_class_element(element, class_name: Literal["normal", "clan"]) -> bool:
    """Check if the element has a class 'normal'."""
    return element.get("class") == [class_name]


def run_scraper(soup: BeautifulSoup, url: str) -> List[Dict]:
    """
    Scrape law articles from the provided BeautifulSoup object.

    This function processes the HTML content parsed by BeautifulSoup to extract law articles.
    Each article is identified by a specific class and contains a title, a list of text paragraphs,
    and a link to the article section.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object containing the parsed HTML content.
        url (str): The base URL of the website to construct full article links.

    Returns:
        List[Dict]: A list of dictionaries, each representing a law article with the following keys:
            - "title" (str): The title of the article.
            - "texts" (List[str]): A list of text paragraphs within the article.
            - "link" (str): The URL link to the specific article section.
    """
    law_articles = []
    article_title = None
    article_texts = []
    article_link = None

    # Find all <p> elements in the HTML
    elements = soup.find_all("p")
    for el in elements:
        # Determine the class name of the element
        class_name = (
            "clan" if check_class_element(element=el, class_name="clan") else "normal"
        )

        # If the element is a title (class "clan"), start a new article
        if class_name == "clan":
            if article_title:
                # Save the previous article
                law_articles.append(
                    {
                        "title": article_title,
                        "texts": article_texts,
                        "link": article_link,
                    }
                )
                article_texts = []
            # Get the article title
            article_title = el.get_text(strip=True)

            # Get the link to the article section
            name_attr = el.find("a").get("name") if el.find("a") else None
            article_link = f"{url}#{name_attr}" if name_attr else None
        # If the element is part of an article's text, add it to the current article
        elif article_title and class_name == "normal":
            article_texts.append(el.get_text(strip=True))

    # Save the last article
    if article_title and article_texts:
        law_articles.append(
            {"title": article_title, "texts": article_texts, "link": article_link}
        )

    return law_articles


def main(urls: List[str], output_dir: Path) -> None:
    """
    Scrape law articles from a list of URLs and save them as JSON files.

    Args:
        urls (List[str]): A list of URLs to scrape.
        output_dir (Path): The directory where the JSON files will be saved.
    """
    # Ensure the output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    with tqdm_logging_redirect():
        for url in tqdm(urls, desc="Scraping laws", total=len(urls)):
            save_path = output_dir / f"{Path(url).stem}.json"

            try:
                response = requests.get(url)
                # Ensure we handle HTTP errors
                response.raise_for_status()
            except requests.RequestException as e:
                logger.error(f'Failed to fetch URL: "{url}" - {e}')
                continue

            soup = BeautifulSoup(response.content, "lxml")

            try:
                law_articles = run_scraper(soup=soup, url=url)
            except Exception as e:
                logger.error(f'Failed to scrape data from URL: "{url}" - {e}')
                continue

            try:
                with open(save_path, "w", encoding="utf-8") as file:
                    json.dump(law_articles, file, indent=4, ensure_ascii=False)
                logger.info(f'Successfully saved data to "{save_path}"')
            except Exception as e:
                logger.error(f'Failed to save data to "{save_path}" - {e}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape law articles from URLs.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", type=str, help="Single URL to scrape.")
    group.add_argument(
        "--file",
        type=Path,
        help="Path to text file containing URLs separated by newlines.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("scraper/laws"),
        help="Directory to save the JSON files.",
    )

    args = parser.parse_args()

    if args.url:
        urls = [args.url]
    elif args.file:
        with open(args.file, "r", encoding="utf-8") as file:
            urls = [line.strip() for line in file if line.strip()]

    main(urls=urls, output_dir=args.output_dir)
