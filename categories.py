from typing import List

import requests
from bs4 import BeautifulSoup, Tag


def find_category():
    def check_and_write_in_arr(text: str, arr):
        if text.startswith("/category"):
            arr.append("https://basalam.com" + text)
        return arr

    url = "https://basalam.com"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    links: List[Tag] = soup.find_all('a')
    specific_links = []
    new_arrays = []
    categories = []
    for link in links:
        if link['href'] in specific_links:
            continue
        specific_links.append(link['href'])
        check_and_write_in_arr(link['href'], categories)
    for element in categories:
        new_array = [element]
        new_arrays.append(new_array)
    return new_arrays
