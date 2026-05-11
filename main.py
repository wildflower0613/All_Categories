import re
import csv
import time
from typing import Any

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Getting Data from Other Categories


# Base URL of the website (e.g., books.toscrape.com)
BASE_URL = "http://books.toscrape.com/"
all_books_data = []

# Fetch the main page to get all category links
response = requests.get(BASE_URL)
soup = BeautifulSoup(response.text, 'html.parser')

# Locate the categories list sidebar
category_links = soup.select("ul.nav-list ul li a")


def extrbook_data(book_url: str) -> dict:
    page = requests.get(book_url)
    soup = BeautifulSoup(page.content, 'html.parser')
    table = soup.find("table", class_="table table-striped")
    if not table:
        print("Table not found for:", book_url)
        print("Page title was:", soup.title)
        return {}
    extract = table.find("tbody")
    count = 0
    data = list()
    rows = table.find_all("tr")
    for row in rows:
        key = row.find("th").text.strip()
        value = row.find("td").text.strip()
        data.append([key, value])
    book_dict = dict(data)

    ratingtag = soup.find("p", class_="star-rating")
    book_dict["rating"] = ratingtag["class"][1]

    proddescripttag = soup.find("p", attrs={'class': None})
    if proddescripttag:
        proddescript = proddescripttag.get_text()
    else:
        proddescript = ""
    book_dict["description"] = proddescript

    title = (book.h3.a['title'])
    safetitle = re.sub(r'[^\w\-]', '_', title)
    safetitle = safetitle[:80]
    book_dict["title"] = title

    price = book.find('p', class_='price_color').get_text()
    book_dict["price"] = price

    book_dict["category"] = cat_name

    book_imagetag = soup.find("img")["src"]
    imageurl = "https://books.toscrape.com/" + book_imagetag.replace("../../", "")
    image_download = requests.get(imageurl)
    if image_download.status_code == 200:
        imageurl = "https://books.toscrape.com/" + book_imagetag.replace("../../", "")
        image_download = requests.get(imageurl)
        with open("image_" + safetitle + ".jpg", "wb") as f:
            f.write(image_download.content)
    else:
        print("Placeholder or empty image skipped.")

    return book_dict



# Function to save data to separate CSVs
def save_to_csv(cat_name, books_data):
    filename = f"{cat_name.replace(' ', '_')}_books.csv"
    fieldnames = books_data[0].keys()

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(books_data)
    print(f"Saved {len(books_data)} books to {filename}")

# 2. Loop through each category
for cat in category_links:
    cat_name = cat.text.strip()
    cat_url = BASE_URL + cat['href']

    # Start on the first page of the category
    current_url = cat_url

    books_data = []

# 3. Handle pagination within the category
    while current_url:
        print("CURRENT URL:", current_url)
        time.sleep(1)
        cat_response = requests.get(current_url)
        cat_soup = BeautifulSoup(cat_response.text, 'html.parser')

        # Find all books on the current page
        books = cat_soup.find_all('article', class_='product_pod')
        write_header = True

        for book in books:
            relative_url = book.a["href"]
            book_url = urljoin(cat_url, relative_url)
            book_dict = extrbook_data(book_url)
            if book_dict :
                books_data.append(book_dict)


        # Find the "Next" button
        next_button = cat_soup.find("li", class_="next")
        if next_button:

            # Get the relative URL and form the absolute URL
            next_page = next_button.a["href"]
            current_url = urljoin(current_url, next_page)
        else:
            current_url = None

    save_to_csv(cat_name, books_data)



