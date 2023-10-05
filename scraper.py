import requests
from bs4 import BeautifulSoup
import pandas as pd

BASE_URL = "https://yalereview.org"

def get_published_in_info(link):
    # Fetch the individual article content
    response = requests.get(link)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Try to find the div with class "hidden md-1:block md-1:mt-1"
    div = soup.find('div', class_='hidden md-1:block md-1:mt-1')
    if div:
        return div.text.strip()
    else:
        return None

def extract_data_from_page(page_number, topic):
    # Construct the URL
    if page_number == 1:
        url = f'{BASE_URL}/{topic}'
    else:
        url = f"{BASE_URL}/{topic}/p{page_number}#results"
    
    # Fetch the page content
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all the sections
    sections = soup.find_all('div', {'class': 'col-span-2 md:col-span-4 col-start-3'})
    
    results = []
    
    for section in sections:
        # Extract the required data from each section
        category_div = section.find('div', class_='text-xxxxs sm:text-sm font-extrabold uppercase mb-1')
        if category_div is not None:
            category_a = category_div.a
            if category_a is not None:
                category = category_a.text.strip()
            else:
                category = category_div.text.strip()
        else:
            category = None
        link = section.find('h3', class_='text-sm sm:text-3xl display-heading-2 mb-1 leading-tight').a['href']
        title = section.find('h3', class_='text-sm sm:text-3xl display-heading-2 mb-1 leading-tight').a.text.strip()
        author_div = section.find('div', class_='text-xxs sm:text-base font-extrabold inline')
        if author_div is not None:
            author = author_div.text.strip()
        else:
            author = None
        date_div = section.find('div', class_='text-xxxxs sm:text-sm mt-3')
        if date_div is not None:
            date = date_div.text.strip()
        else:
            date = None
        
        # Get the 'PUBLISHED_IN' info
        published_in = get_published_in_info(link)
        
        results.append({
            'CATEGORY': category,
            'LINK': link,
            'TITLE': title,
            'AUTHOR': author,
            'DATE': date,
            'PUBLISHED_IN': published_in
        })
    
    return results

if __name__ == '__main__':
    
    data = []

    topic = 'nonfiction' # change this as necessary
    first_page = 1 # change this as necessary, default 1
    last_page = 31 # change this as necessary, based on the max page # on the website

    for page in range(first_page, last_page+1):
        
        print('Processing page', page)
        new_data = extract_data_from_page(page, topic)
        for line in new_data:
            print(line)
        print('\n'*3)
        data += new_data
    
    df = pd.DataFrame(data)
    df.to_csv('yalereview_nonfiction_data.csv', index=False)

