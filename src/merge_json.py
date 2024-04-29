import os
import json


def merge_json(path: str) -> None:
    content: list[dict] = []

    for file in os.listdir(path):
        file_path: str = os.path.join(path, file)
        with open(file_path, 'r', encoding='utf-8') as json_file:
            file_content: list[dict] = json.load(json_file)
            content += file_content

    output_file: str = os.path.join(path, 'merged_data.json')
    with open(output_file, 'w', encoding='utf-8') as merge:
        json.dump(content, merge)


def main():
    merge_json('../data_json')


if __name__ == '__main__':
    main()

