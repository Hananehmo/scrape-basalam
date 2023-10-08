import sqlite3
import time
from typing import List
import requests
from bs4 import BeautifulSoup, Tag
import threading

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
HEADERS = {
    'User-Agent': USER_AGENT,
}

# Create a lock for thread synchronization
lock = threading.Lock()

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
    response = requests.get(url, headers=HEADERS, verify=False)
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
    # for arr in new_arrays:
    #     print(arr)
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
        url = cats[j]
        # print(url)
        response = requests.get(url, headers=HEADERS, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')

        links: List[Tag] = soup.find_all('a')
        specific_links = []
        for link in links:
            if 'href' in link.attrs:
                if link['href'] in specific_links:
                    continue
                specific_links.append(link['href'])
                res = check_and_write(link['href'], res, cats[j])
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
        # print(url)
        response = requests.get(url, headers=HEADERS, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        links: List[Tag] = soup.find_all('a')
        specific_links = []
        for link in links:
            if 'href' in link.attrs:
                if link['href'] in specific_links:
                    continue
                specific_links.append(link['href'])
                result = check_and_write(link['href'], subcats[i], result)

    return result


def find_products_and_images(finalcats: List[str]):
    connection = sqlite3.connect('test.db')
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    categories TEXT,
                    subcategories TEXT,
                    final_categories TEXT,
                    product TEXT,
                    image TEXT
                )''')

    cursor.execute("SELECT * FROM products ORDER BY id DESC LIMIT 1")
    last_row = cursor.fetchone()

    def check_and_write(text: str, ress, arrs):
        if "/product" in text:
            product_link = "https://basalam.com" + text
            print(product_link)
            cursor.execute("SELECT COUNT(*) FROM products WHERE product = ?", (product_link,))
            count = cursor.fetchone()[0]
            if count == 0:
                product = Category(ress.categories, ress.subcategories)
                product.pass_final_categories(ress.final_categories)
                product.pass_product(product_link)
                img_response = requests.get(product_link, headers=HEADERS, verify=False)
                img_soup = BeautifulSoup(img_response.content, "html.parser")
                image_links = [img["src"] for img in img_soup.find_all("img")]
                for img_link in image_links:
                    if img_link.endswith(("_512X512X70.jpg", "_50X50X70.jpg", ".png", "_512X512X70.jpeg", "_50X50X70.jpeg")):
                        product.pass_image(img_link)
                arrs.append(product)
                # print('test1')
                with lock:
                    cursor.execute('''INSERT OR IGNORE INTO products (categories, subcategories, final_categories, product, image)
                                                VALUES (?, ?, ?, ?, ?)''',
                                   (product.categories, product.subcategories, product.final_categories, product.product, ', '.join(product.image)))
                    connection.commit()
                    # print('test2')

        if last_row:
            for row in cursor.execute("SELECT * FROM products WHERE id > ? ORDER BY id", (last_row[0],)):
                product = Category(row[1], row[2])
                product.pass_final_categories(row[3])
                product.pass_product(row[4])
                product.pass_image(row[5].split(", "))
                arrs.append(product)

        return arrs

    final_res = []
    for i in range(len(finalcats)):
        url = finalcats[i].final_categories
        for p in range(1, 250):
            while True:
                try:
                    response = requests.get(url + f'?page={p}', headers=HEADERS, verify=False)
                    print(url + f'?page={p}' + str(response))
                    soup = BeautifulSoup(response.text, 'html.parser')
                    links = soup.select('a')
                    specific_links = []
                    for link in links:
                        if 'href' in link.attrs:
                            if link['href'] in specific_links:
                                continue
                            specific_links.append(link['href'])
                            final_res = check_and_write(link['href'], finalcats[i], final_res)
                    if response.status_code == 204:
                        print(url + f'?page={p}' + ' not found!!')
                        break
                except ConnectionError:
                    print("Connection error occurred. Retrying...")
                    time.sleep(1.5)
                break

    connection.close()
    return final_res


def process_category(category):
    subcategory = find_subcategory(category)
    finalcat = find_under_subcategory(subcategory)
    find_products_and_images(finalcat)

categories = find_category()

threads = []

for category in categories:
    thread = threading.Thread(target=process_category, args=(category,))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()
