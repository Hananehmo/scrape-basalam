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
    def check_and_write(text: str, arr, category):
        if text.startswith("/subcategory"):
            link = "https://basalam.com" + text
            subcategory = Category(category, link)
            arr.append(subcategory)
        return arr

    res = []
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
            res = check_and_write(link['href'], res, new_arrays[j][0])
    return res


def find_under_subcategory(subcats: List):
    def check_and_write(text: str, res_inner: List, result: List) -> List:
        if text.startswith("/search/subcategory"):
            link = "https://basalam.com" + text
            final_categories = Category(res_inner.categories, res_inner.subcategories)
            final_categories.pass_final_categories(link)
            result.append(final_categories)
        return result

    elec_device = Category('https://basalam.com/category/electronic-devices', 'https://basalam.com/category'
                                                                              '/electronic-devices')
    subcats.append(elec_device)
    result = []
    for i in range(len(subcats)):
        url = subcats[i].subcategories
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        links: List[Tag] = soup.find_all('a')
        specific_links = []
        for link in links:
            if link['href'] in specific_links:
                continue
            specific_links.append(link['href'])
            result = check_and_write(link['href'], subcats[i], result)
    return result


def find_products(finalcats: List):
    def check_and_write(text: str, ress, arrs):
        if "/product" in text:
            product_link = "https://basalam.com" + text
            product = Category(ress.categories, ress.subcategories)
            product.pass_product(product_link)
            arrs.append(product)
        return arrs

    final_res = []
    for i in range(len(finalcats)):
        url = finalcats[i].final_categories
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        links: List[Tag] = soup.find_all('a')
        specific_links = []
        for link in links:
            if 'href' not in link.attrs:

                if link['href'] in specific_links:
                    continue
                specific_links.append(link['href'])
                final_res = check_and_write(link['href'], finalcats[i], final_res)
            if not specific_links:
                break

    for res_obj in final_res:
        print(
            f'{res_obj.categories}{", "}{res_obj.subcategories}{", "}{res_obj.final_categories}{", "}{res_obj.prodect}')
        print()
