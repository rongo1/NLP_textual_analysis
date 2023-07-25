import pandas as pd
import numpy as np 
import requests
from bs4 import BeautifulSoup
import re
import os

def polarity(p, n):
    return  (p - n)/ ((p + n) + 0.000001)

def subjectivity(p, n, t):
    return (p + n)/ (t + 0.000001)

def syllable_count(word):
    count = 0
    vowels = "aeiouy"
    if word[0] in vowels:
        count += 1
    for index in range(1, len(word)):
        if word[index] in vowels and word[index - 1] not in vowels:
            count += 1
            if word.endswith("e"):
                count -= 1
    if count == 0:
        count += 1
    return count
def word_complexity(word):
    if syllable_count(word) > 2:
        return 1
    else:
        return 0
    

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

inps = pd.read_excel('Input.xlsx')

for index, row in inps.iterrows():
    print(f"processing article with URL_ID = {int(row['URL_ID'])}")
    # Specify the website link
    url = row['URL']
    # Send a request to the website and get the response
    response = requests.get(url)    
    # Extract the HTML content from the response
    html_content = response.content    
    # Create a Beautiful Soup object with the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    # There are some websites with no content
    article_title = ""
    try:
        article_title = soup.find('h1').text.strip()
    except:
        print(f"no title in {int(row['URL_ID'])}")
        
    article_text = ''
    try:
        post_content_div = soup.find('div', {'class': 'td-post-content'}) 
        # Extract the article text
        article_text_elements = post_content_div.find_all('p')
        for element in article_text_elements:
            article_text += element.text.strip() + '\n'
    except:
        print(f"no text in {int(row['URL_ID'])}")
    
    
    #saving txt
    filename = "txt_files/" + str(int(row['URL_ID'])) + ".txt"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    file = open(filename,"w", encoding='utf-8')
    file.writelines(article_title + '\n' + article_text)
    file.close()
    
    
    


# Creating np array with stop words
fileNameSW = ['StopWords_Auditor', 'StopWords_Currencies', 'StopWords_DatesandNumbers', 
              'StopWords_Generic', 'StopWords_GenericLong', 'StopWords_Geographic', 'StopWords_Names']
stopWords = []
for fileName in fileNameSW:
    fileSW = open('StopWords/' + fileName + '.txt', 'r', encoding='ISO-8859-1')
    lineSW = fileSW.read().splitlines()
    for line in lineSW:
        new_words = re.split(r'[\n|\s]+', line.lower())[0]
        stopWords.extend([new_words])
npStopWords = np.array(stopWords)


# Creating np array with negative words
negWords = []
fileNG = open('MasterDictionary/' + 'negative-words' + '.txt', 'r', encoding='ISO-8859-1')
lineNG = fileNG.read().splitlines()
for line in lineNG:
    negWords.extend([re.split(r'[\n|\s]+', line.lower())[0]])    
npNegWords = np.array(negWords)
mask = np.char.equal(npNegWords, '')
npNegWords = npNegWords[~mask]


# Creating np array with posotive words
posWords = []
filePS = open('MasterDictionary/' + 'positive-words' + '.txt', 'r', encoding='ISO-8859-1')
linePS = filePS.read().splitlines()
for line in linePS:
    posWords.extend([re.split(r'[\n|\s]+', line.lower())[0]])
npPosWords = np.array(posWords)
mask = np.char.equal(npPosWords, '')
npPosWords = npPosWords[~mask]

# Counting all variables. There are 3 articles with no title and text (URL_ID = 44, 57, 144), I left them empty.
inps = pd.read_excel('Input.xlsx')
for index, row in inps.iterrows():
    words = []
    sentences = 0 
    personal_pronouns = 0
    file = open("txt_files/" + str(int(row['URL_ID']))  + ".txt", 'r', encoding='utf-8')
    lines = file.read().splitlines()    
    for line in lines:
        sentences += line.count('.') + line.count('!') + line.count('?')
        personal_pronouns += line.count('i') + line.count('we') + line.count('my') + line.count('ours') + line.count('us')
        check_for_us = re.split(r'[“”",!;:.\s\n()?]+', line)
        words.extend(re.split(r'[“”",!;:.\s\n()?]+', line.lower()))        
        # Paying special attention to US and us
        if 'US' in check_for_us:
            if 'us' in check_for_us:
                words.extend(['US'])
            else:
                words[words.index('us')] = 'US'
    # removing stop words
    npWords = np.array(words)
    indices_to_remove = np.where(np.isin(npWords, npStopWords))[0]
    words_filtered = np.delete(words, indices_to_remove)
    mask = np.char.equal(words_filtered, '')
    words_filtered = words_filtered[~mask]
    
    
    if sentences != 0:
        inps.loc[index, 'POSITIVE SCORE'] = len(np.where(np.isin(words_filtered, npPosWords))[0])
        inps.loc[index, 'NEGATIVE SCORE'] = len(np.where(np.isin(words_filtered, npNegWords))[0])
        inps.loc[index, 'POLARITY SCORE'] = polarity(inps.loc[index, 'POSITIVE SCORE'], inps.loc[index, 'NEGATIVE SCORE']) 
        inps.loc[index, 'SUBJECTIVITY SCORE'] = subjectivity(inps.loc[index, 'POSITIVE SCORE'], inps.loc[index, 'NEGATIVE SCORE'], len(words_filtered)) 
        inps.loc[index, 'AVG SENTENCE LENGTH'] = len(words_filtered)/sentences
        inps.loc[index, 'PERCENTAGE OF COMPLEX WORDS'] = sum(map(word_complexity, words_filtered)) / len(words_filtered)
        inps.loc[index, 'FOG INDEX'] = 0.4 * (inps.loc[index, 'AVG SENTENCE LENGTH'] + inps.loc[index, 'PERCENTAGE OF COMPLEX WORDS'] )
        inps.loc[index, 'AVG NUMBER OF WORDS PER SENTENCE'] = len(words_filtered)/sentences 
        inps.loc[index, 'COMPLEX WORD COUNT'] = sum(map(word_complexity, words_filtered)) 
        inps.loc[index, 'WORD COUNT'] = len(words_filtered)
        inps.loc[index, 'SYLLABLE PER WORD'] = sum(map(word_complexity, words_filtered)) / len(words_filtered)
        inps.loc[index, 'PERSONAL PRONOUNS'] = personal_pronouns
        inps.loc[index, 'AVG WORD LENGTH'] = sum(map(len, words_filtered))/len(words_filtered)

inps.to_excel("Output Data Structure.xlsx", index = False)



    