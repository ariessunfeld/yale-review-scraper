from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

import requests
from bs4 import BeautifulSoup
import pandas as pd

BASE_URL = "https://yalereview.org"

def get_last_page(topic):
    """Find how many pages the topic has on the Yale Review site"""
    # Fetch the homepage content for the topic
    url = f'{BASE_URL}/{topic}'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the last page link
    last_page_link = soup.find('a', class_='flex text-blue p-1')
    if last_page_link:
        # Extract the page number from the link
        page_num = int(last_page_link['href'].split('p')[-1].split('#')[0])
        return page_num
    return 1

def extract_category(row):
    """Parse the Category from the row"""
    category = None
    category_div = row.find('div', class_='text-xxxxs sm:text-sm font-extrabold uppercase mb-1')
    if category_div is not None:
        category_a = category_div.a
        if category_a is not None:
            category = category_a.text.strip()
        else:
            category = category_div.text.strip()
    return category

def extract_link(row):
    """Parse the Link from the row"""
    link = None
    link_h3 = row.find('h3', class_='text-sm sm:text-3xl display-heading-2 mb-1 leading-tight')
    if link_h3:
        link_a = link_h3.a
        if link_a:
            link = link_a['href']
    return link

def extract_title(row):
    """Parse the Title from the row"""
    title = None
    title_h3 = row.find('h3', class_='text-sm sm:text-3xl display-heading-2 mb-1 leading-tight')
    if title_h3:
        title_a = title_h3.a
        if title_a:
            title = title_a.text.strip() 
    return title

def extract_author(row):
    """Parse the Author from the row"""
    author = None
    author_div = row.find('div', class_='text-xxs sm:text-base font-extrabold inline')
    if author_div:
        author = author_div.text.strip()
    return author

def extract_date(row):
    """Parse the Date from the row"""
    date = None
    date_div = row.find('div', class_='text-xxxxs sm:text-sm mt-3')
    if date_div:
        date = date_div.text.strip()
    return date

def get_published_in_info(link):
    """Checks whether the item has been published in print
    
    Returns: 'See this issue' if published in print; None otherwise
    """
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
    """Parses the data from all rows on a given page for a given topic"""
    # Construct the URL
    if page_number == 1:
        url = f'{BASE_URL}/{topic}'
    else:
        url = f"{BASE_URL}/{topic}/p{page_number}#results"
    
    # Fetch the page content
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all the rows
    rows = soup.find_all('div', {'class': 'col-span-2 md:col-span-4 col-start-3'})
    
    with ThreadPoolExecutor(8) as executor:
        results = list(executor.map(process_row, rows))

    return results

def process_row(row):
    """Process a single row of information on a page"""
    category = extract_category(row)
    link = extract_link(row)
    title = extract_title(row)
    author = extract_author(row)
    date = extract_date(row)
    
    # Get the 'PUBLISHED_IN' info
    published_in = get_published_in_info(link)
    
    return {
        'CATEGORY': category,
        'LINK': link,
        'TITLE': title,
        'AUTHOR': author,
        'DATE': date,
        'PUBLISHED_IN_PRINT': True if published_in == 'See this issue' else False
    }

def process_topic(topic):
    """Process all pages for a given topic (subpage) of the Yale Review site"""
    first_page = 1
    last_page = get_last_page(topic)
    data = []

    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(extract_data_from_page, page, topic) for page in range(first_page, last_page+1)]
        
        for future in futures:
            data.extend(future.result())

    return data

def make_csv(data, topic):
    df = pd.DataFrame(data)
    df = df.sort_values('PUBLISHED_IN_PRINT')
    savename = f'YaleReview{topic.capitalize()}.csv'
    df.to_csv(savename, index=False)
    print(f'\tWrote {savename}')

if __name__ == '__main__':
    
    topics = ['nonfiction', 'fiction', 'poetry', 'interviews', 'folios']

    for topic in topics:
        print(f'Processing https://yalereview.org/{topic}...')
        data = process_topic(topic)
        make_csv(data, topic)
