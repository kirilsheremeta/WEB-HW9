import json

import requests
from bs4 import BeautifulSoup

URL = "http://quotes.toscrape.com"


def get_links():
    links = []
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")
    quotes = soup.find_all("div", class_="quote")
    for quote in quotes:
        links.append(quote.find("a", href=True).get("href"))
    return links


def author_spider():
    data = []
    author_links = get_links()
    for link in author_links:
        resource = requests.get(URL + link)
        soup = BeautifulSoup(resource.text, "lxml")
        content = soup.select("div[class=container] div[class=author-details]")
        for el in content:
            fullname = el.find("h3", attrs={"class": "author-title"}).text.strip()
            date_of_birth = el.find("span", attrs={"class": "author-born-date"}).text.strip()
            place_of_birth = el.find("span", attrs={"class": "author-born-location"}).text.strip()
            description = el.find("div", attrs={"class": "author-description"}).text.strip()
            result = {"fullname": fullname,
                      "date_of_birth": date_of_birth,
                      "place_of_birth": place_of_birth,
                      "description": description
                      }
            data.append(result)

    with open("authors.json", "w", encoding="utf-8") as fd:
        json.dump(data, fd, ensure_ascii=False, indent=4)


def quote_spider():
    data = []
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")
    content = soup.select("div[class = col-md-8] div[class=quote]")
    for el in content:
        result = {}
        quote = el.find("span", attrs={"class": "text"}).text
        author = el.find("small", attrs={"class": "author"}).text
        tags = (list(filter(bool,  [t.text.strip() for t in el.find("div")][1:])))
        result.update({"author": author, "tags": tags, "quote": quote})
        data.append(result)

    with open("quotes.json", "w", encoding="utf-8") as fd:
        json.dump(data, fd, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    author_spider()
    quote_spider()
