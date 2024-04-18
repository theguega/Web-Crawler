import scraper as scp
from login import credentials


def main():
    scraper = scp.Scraper(username=credentials["username"], password=credentials["password"])
    graph = scraper.get_data()


if __name__ == "__main__":
    main()


