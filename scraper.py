import requests
from bs4 import BeautifulSoup

BASE_URL = "https://yalereview.org/poetry"

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

def extract_data_from_page(page_number):
    # Construct the URL
    if page_number == 1:
        url = BASE_URL
    else:
        url = f"{BASE_URL}/p{page_number}#results"
    
    # Fetch the page content
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all the sections
    sections = soup.find_all('div', {'class': 'col-span-2 md:col-span-4 col-start-3'})
    
    results = []
    
    for section in sections:
        # Extract the required data from each section
        category = section.find('div', class_='text-xxxxs sm:text-sm font-extrabold uppercase mb-1').a.text.strip()
        link = section.find('h3', class_='text-sm sm:text-3xl display-heading-2 mb-1 leading-tight').a['href']
        title = section.find('h3', class_='text-sm sm:text-3xl display-heading-2 mb-1 leading-tight').a.text.strip()
        author = section.find('div', class_='text-xxs sm:text-base font-extrabold inline').text.strip()
        date = section.find('div', class_='text-xxxxs sm:text-sm mt-3').text.strip()
        
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

# Example usage
data = extract_data_from_page(1)
print(data)
