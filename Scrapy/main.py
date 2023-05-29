import redis
from redis_lru import RedisLRU
from mongoengine import DoesNotExist
from models import Author, Quotes

client = redis.StrictRedis(host="localhost", port=6379, password=None)
cache = RedisLRU(client)


def find_quotes_by_author(name: str):
    try:
        author = Author.objects(fullname__startswith=name.title()).first()
        quotes = Quotes.objects(author=author)
        result = [f"{quote.quote} ({quote.author.fullname}, {', '.join(quote.tags)})" for quote in quotes]
        for quote in result:
            print(quote)
    except DoesNotExist:
        print(f"Can't find author {name.title()}")


@cache
def find_quotes_by_name(value):
    try:
        author = Author.objects(fullname__startswith=value.title())[0]
        quotes = Quotes.objects(author=author)
        if quotes:
            result = []
            for quote in quotes:
                r = f"{quote.quote}\n{quote.author.fullname}    tags:{', '.join(quote.tags)}"
                result.append(r)
            return result
    except DoesNotExist:
        print(f"Can't find quotes by {value}")


@cache
def find_one_tag(tag: str):
    try:
        quotes = Quotes.objects(tags__startswith=tag.lower())
        result = [f"{quote.quote} ({quote.author.fullname}, {', '.join(quote.tags)})" for quote in quotes]
        for quote in result:
            print(quote)
    except DoesNotExist:
        print(f"Can't find tag: {tag.lower()}")


@cache
def find_all_tags(tags: list):
    try:
        quotes = Quotes.objects(tags__in=tags)
        result = [f"{quote.quote} ({quote.author.fullname}, {', '.join(quote.tags)})" for quote in quotes]
        for quote in result:
            print(quote)
    except DoesNotExist:
        print(f"Tags {str([tag.lower() for tag in tags])} not exists")


@cache
def find_quotes_by_tags(value):
    try:
        result = []
        for quote in Quotes.objects(tags__startswith=value):
            r = f"{quote.quote}\n{quote.author.fullname}    tags: {', '.join(quote.tags)}"
            result.append(r)
        return result
    except DoesNotExist:
        print(f"Quotes with tags: {value} not exists")


def main():
    while True:
        user_command = input("Enter command: ").lower()
        if user_command == "exit":
            print("Good bye. See you next time.")
        else:
            try:
                input_text = user_command.split(":")
                command = input_text[0]
                data = input_text[1].strip().split(",")
                if len(data) <= 1:
                    data = data[0]
                match command:
                    case "author":
                        find_quotes_by_author(data)
                    case "name":
                        find_quotes_by_name(data)
                    case "one tag":
                        find_one_tag(data)
                    case "all tags":
                        find_all_tags(data)
                    case "quote by tags":
                        find_quotes_by_tags(data)
                    case _:
                        print("Unknown command")
            except Exception as err:
                print(f"Error: {err}")


if __name__ == '__main__':
    main()
