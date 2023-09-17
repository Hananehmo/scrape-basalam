from typing import List
import requests
from bs4 import BeautifulSoup, Tag


class Category:
    def __init__(self, categories, subcategories):
        self.categories = categories
        self.subcategories = subcategories
        self.final_categories = None
        self.product = None
        self.image = []
        self.video = []

    def pass_final_categories(self, elements):
        self.final_categories = elements

    def pass_product(self, elements):
        self.product = elements

    def pass_image(self, images):
        self.image.append(images)

    def pass_video(self, videos):
        self.video.append(videos)


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
        if 'href' in link.attrs:
            if link['href'] in specific_links:
                continue
            specific_links.append(link['href'])
            check_and_write_in_arr(link['href'], categories)
    for element in categories:
        new_array = [element]
        new_arrays.append(new_array)
    return new_arrays


def find_subcategory(cats):
    def check_and_write(text: str, arr, category):
        if text.startswith("/subcategory"):
            link = "https://basalam.com" + text
            subcategory = Category(category, link)
            arr.append(subcategory)
        return arr

    res = []
    for j in range(len(cats)):
        url = cats[j][0]
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        links: List[Tag] = soup.find_all('a')
        specific_links = []
        for link in links:
            if 'href' in link.attrs:
                if link['href'] in specific_links:
                    continue
                specific_links.append(link['href'])
                res = check_and_write(link['href'], res, cats[j][0])
    return res


def find_under_subcategory(subcats: List):
    def check_and_write(text: str, res_inner: Category, result: List) -> List:
        if text.startswith("/search/subcategory"):
            link = "https://basalam.com" + text
            final_categories = Category(res_inner.categories, res_inner.subcategories)
            final_categories.pass_final_categories(link)
            result.append(final_categories)
        return result

    elec_device = Category('https://basalam.com/category/electronic-devices', 'https://basalam.com/category/electronic-devices')
    subcats.append(elec_device)
    result = []
    for i in range(len(subcats)):
        url = subcats[i].subcategories
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        links: List[Tag] = soup.find_all('a')
        specific_links = []
        for link in links:
            if 'href' in link.attrs:
                if link['href'] in specific_links:
                    continue
                specific_links.append(link['href'])
                result = check_and_write(link['href'], subcats[i], result)
    for r in result:
        print(f'{r.categories}, {r.subcategories}, {r.final_categories}')
    return result


def find_products_and_images(finalcats: List[str]):
    def check_and_write(text: str, ress, arrs, product_file):
        if "/product" in text:
            product_link = "https://basalam.com" + text
            product = Category(ress.categories, ress.subcategories)
            product.pass_final_categories(ress.final_categories)
            product.pass_product(product_link)
            img_response = requests.get(product_link)
            img_soup = BeautifulSoup(img_response.content, "html.parser")
            image_links = [img["src"] for img in img_soup.find_all("img")]
            for img_link in image_links:
                if img_link.endswith(("_512X512X70.jpg", "_50X50X70.jpg", ".png", "_512X512X70.jpeg", "_50X50X70.jpeg")):
                    product.pass_image(img_link)
            arrs.append(product)
            product_file.write(f'{product.categories}, {product.subcategories}, {product.final_categories}, {product.product}, {product.image}\n')
        return arrs

    print(finalcats)
    final_res = []
    with open("all links.txt", 'a') as file:
        for i in range(len(finalcats)):
            url = finalcats[i].final_categories
            # page_number = 1
            for p in range(1, 250):
                response = requests.get(url + f'?page={p}')
                # print(url + f'?page={p}' + str(response))
                soup = BeautifulSoup(response.text, 'html.parser')
                links: List[Tag] = soup.select('a')
                specific_links = []
                for link in links:
                    if 'href' in link.attrs:
                        if link['href'] in specific_links:
                            continue
                        specific_links.append(link['href'])
                        final_res = check_and_write(link['href'], finalcats[i], final_res, file)
                if response.status_code == 204:
                    print(url + f'?page={p}' + ' not found!!')
                    break


new_arrays = find_category()
res = find_subcategory(new_arrays)
res = find_under_subcategory(res)
find_products_and_images(res)
