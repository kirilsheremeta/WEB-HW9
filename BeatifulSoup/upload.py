import json

from models import Author, Quotes


def load_authors(filename):
    with open(filename, "r", encoding="utf-8") as fd:
        authors = json.load(fd)

        for a in authors:
            author = Author(fullname=a.get("fullname"),
                            date_of_birth=a.get("date_of_birth"),
                            place_of_birth=a.get("place_of_birth"),
                            description=a.get("description"))
            author.save()


def load_quotes(filename):
    with open(filename, "r", encoding="utf-8") as fd:
        quotes = json.load(fd)

        for quote in quotes:
            author = Author.objects(fullname=quote.get("author", None))
            new_quote = Quotes(tags=quote.get("tags"),
                               quote=quote.get("quote", None),
                               author=author[0])
            new_quote.save()


if __name__ == '__main__':
    load_authors("authors.json")
    load_quotes("quotes.json")
