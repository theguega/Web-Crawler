import scraper as scp
import json_parser as jsp
from login import credentials


def main():
    scraper = scp.Scraper(username=credentials["username"], password=credentials["password"])
    graph = scraper.get_data()

    #data_parser = jsp.JSONParser()
    #data_parser.parse('../data_json/merged_data.json')
    #activity_graph = data_parser.get_data()


if __name__ == "__main__":
    main()


