import categories
import os
new_arrays = categories.find_category()
res = categories.find_subcategory(new_arrays)
res = categories.find_under_subcategory(res)
categories.find_products_and_images(res)

