import pandas as pd
import numpy as np 
import requests
from bs4 import BeautifulSoup


inps = pd.read_excel('Input.xlsx')

for index, row in inps.iterrows():
    
    # Specify the website link
    url = row['URL']
    print(url)
    # Send a request to the website and get the response
    response = requests.get(url)
    
    # Extract the HTML content from the response
    html_content = response.content
    
    # Create a Beautiful Soup object with the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    
    article_title = ""
    try:
        article_title = soup.find('h1').text.strip()
    except:
        print(f"no header in {row['URL_ID']}")
    # Extract the article title
    
    article_text = ''
    try:
        post_content_div = soup.find('div', {'class': 'td-post-content'}) 
        # Extract the article text
        article_text_elements = post_content_div.find_all('p')
        for element in article_text_elements:
            article_text += element.text.strip() + '\n'
    except:
        print(f"no text in {row['URL_ID']}")
        
        
    file = open("txt_files/" + str(row['URL_ID']) + ".txt","w", encoding='utf-8')
    file.writelines(article_title + '\n' + article_text)
    file.close()
    