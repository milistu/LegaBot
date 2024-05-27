# Scraper

This script scrapes law articles from a list of URLs and saves them as JSON files.

## Usage

To run the script, use the following command:

```bash
python scraper/scraper.py --file scraper/urls.txt --output-dir laws_test
```

## Arguments
- `--url`: A single URL to scrape.
- `--file`: Path to a text file containing URLs separated by newlines.
- `--output-dir`: Directory to save the JSON files (default is scraper/laws).

## Example
To scrape law articles from a single URL (example: Serbian Labor Law) and save the output in the `scraper/laws` directory:
```bash
python scraper/scraper.py --url "https://www.paragraf.rs/propisi/zakon_o_radu.html" --output-dir scraper/laws
```

To scrape law articles from a list of URLs in urls.txt and save the output in the `scraper/laws` directory:
```bash
python scraper/scraper.py --file scraper/urls.txt --output-dir scraper/laws
```
> ⚠️ _**Note**: Ensure you are in the root directory of the project before running the script._

## Output
The output JSON files will be saved in the specified output directory, with each file named after the corresponding URL's stem.
