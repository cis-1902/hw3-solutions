import json
from collections import defaultdict

import requests
from bs4 import BeautifulSoup

URL = "https://quotes.toscrape.com"


def get_author_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    name = soup.find("h3", class_="author-title").text
    birth_date = soup.find("span", class_="author-born-date").text
    birth_place = soup.find("span", class_="author-born-location").text
    description = soup.find("div", class_="author-description").text.strip()
    birth_place = birth_place.replace("in ", "")

    return {
        "name": name,
        "birth_date": birth_date,
        "birth_place": birth_place,
        "description": description,
    }


def get_authors_data(authors):
    authors_data = []
    for _, url in authors.items():
        data = get_author_data(URL + url)
        authors_data.append(data)

    authors_data.sort(key=lambda x: x["name"])
    return authors_data


def get_quotes(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    quote_blocks = soup.find_all("div", class_="quote")
    quotes = []
    authors = dict()
    for quote in quote_blocks:
        text = quote.find("span", class_="text").text
        text = text.replace("“", "").replace("”", "")
        author_name = quote.find("small", class_="author").text
        author_link = quote.find("a")["href"]
        tags = quote.find_all("a", class_="tag")
        authors[author_name] = author_link
        quotes.append(
            {
                "quote": text,
                "author_name": author_name,
                "tags": list(sorted([tag.text for tag in tags])),
            }
        )
    return quotes, authors


def main():
    # have to get all quotes
    index = 1
    all_quotes = []
    all_authors = dict()
    while True:
        quotes, authors = get_quotes(URL + "/page/" + str(index))
        if not quotes:
            break
        all_quotes.extend(quotes)
        all_authors.update(authors)
        index += 1

    all_quotes.sort(key=lambda x: (x["author_name"], x["quote"]))
    for i, quote in enumerate(all_quotes):
        quote["id"] = i

    authors = get_authors_data(all_authors)
    author_name_to_quote_ids = defaultdict(list)
    tags_to_quote_ids = defaultdict(list)

    for quote in all_quotes:
        author_name_to_quote_ids[quote["author_name"]].append(quote["id"])
        for tag in quote["tags"]:
            tags_to_quote_ids[tag].append(quote["id"])

    for author in authors:
        author["quote_ids"] = author_name_to_quote_ids[author["name"]]

    tags = []
    for tag_name, quote_ids in tags_to_quote_ids.items():
        tags.append({"tag": tag_name, "quote_ids": quote_ids})
    tags.sort(key=lambda x: x["tag"])

    # dump data
    with open("quotes.json", "w") as f:
        json.dump(
            {
                "quotes": all_quotes,
                "authors": authors,
                "tags": tags,
            },
            f,
            indent=2,
        )


if __name__ == "__main__":
    main()
