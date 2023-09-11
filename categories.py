from typing import List

import requests
from bs4 import BeautifulSoup, Tag


class Category:
    def __init__(self, categories, subcategories):
        self.categories = categories
        self.subcategories = subcategories
        self.final_categories = None

    def pass_final_categories(self, element):
        self.final_categories = element


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


def find_subcategory(new_arrays):
    def check_and_write(text: str, arr):
        if text.startswith("/subcategory"):
            arr.append("https://basalam.com" + text)

    for j in range(len(new_arrays)):
        url = new_arrays[j][0]
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        links: List[Tag] = soup.find_all('a')
        specific_links = []
        for link in links:
            if link['href'] in specific_links:
                continue
            specific_links.append(link['href'])
            check_and_write(link['href'], new_arrays[j])
