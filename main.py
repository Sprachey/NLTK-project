from bs4 import BeautifulSoup
import pandas as pd
import requests
import os
from nltk import word_tokenize
from nltk.corpus import stopwords
import re

# nltk.download('punkt')
# nltk.download('stopwords')


#DATA EXTRACTION OR SCRAPING

df = pd.read_excel('Input.xlsx')

for index, row in df.iterrows():

    url = row['URL']
    url_id = row['URL_ID']

    header = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"}
    try:
        response = requests.get(url,headers=header)
    except:
        print("can't get response of {}".format(url_id))

    try:
        soup = BeautifulSoup(response.content, 'html.parser')
    except:
        print("can't get page of {}".format(url_id))
    
    try:
        title = soup.find('h1').get_text()
    except:
        print("can't get title of {}".format(url_id))
        continue
    
    article = ""
    try:
        for p in soup.find_all('p'):
            article+= p.get_text()
    except:
        print("can't get text of {}".format(url_id))

    file_name ="TitleText/" + str(url_id) + '.txt'
    with open(file_name, 'w',encoding="utf-8") as file:
        file.write(title + '\n' + article)


text_dir = "TitleText"
stopwords_dir = "StopWords"
sentiment_dir = "MasterDictionary"

#CLEANIN USING STOP WORDS LISTS

stop_words = set()
for files in os.listdir(stopwords_dir):
    with open(os.path.join(stopwords_dir,files),'r',encoding="ISO-8859-1") as f:
        stop_words.update(set(f.read().splitlines()))

docs = []
for text_file in os.listdir(text_dir):
    with open(os.path.join(text_dir,text_file),'r',encoding="utf-8") as f:
        text = f.read()

    words = word_tokenize(text)
    filtered_text = [word for word in words if word.lower() not in stop_words]
    docs.append(filtered_text)

#CREATING A DICTIONARY OF POSITIVE AND NEGATIVE WORDS

pos=set()
neg=set()


for files in os.listdir(sentiment_dir):
    if files =='positive-words.txt':
        with open(os.path.join(sentiment_dir,files),'r',encoding='ISO-8859-1') as f:
            pos.update(f.read().splitlines())
    else:
        with open(os.path.join(sentiment_dir,files),'r',encoding='ISO-8859-1') as f:
            neg.update(f.read().splitlines())

#EXTRACTING DERIVED VARIABLES

positive_words = []
Negative_words =[]
positive_score = []
negative_score = []
polarity_score = []
subjectivity_score = []

for i in range(len(docs)):
    positive_words.append([word for word in docs[i] if word.lower() in pos])
    Negative_words.append([word for word in docs[i] if word.lower() in neg])
    positive_score.append(len(positive_words[i]))
    negative_score.append(len(Negative_words[i]))
    polarity_score.append((positive_score[i] - negative_score[i]) / ((positive_score[i] + negative_score[i]) + 0.000001))
    subjectivity_score.append((positive_score[i] + negative_score[i]) / ((len(docs[i])) + 0.000001))
   
# ANALYSIS OF READABILITY

avg_sentence_length = []
Percentage_of_Complex_words  =  []
Fog_Index = []
complex_word_count =  []
avg_syllable_word_count =[]

stopwords = set(stopwords.words('english'))

def readability(file):
    with open(os.path.join(text_dir,file),'r',encoding="utf-8") as f:
        text=f.read()
        text = re.sub(r'[^\w\s.]','',text)
        sentences = text.split('.')
        num_sentences = len(sentences)
        words = [word  for word in text.split() if word.lower() not in stopwords ]
        num_words = len(words)

    complex_words = []
    for word in words:
        vowels = 'aeiou'
        syllable_count_word = sum( 1 for letter in word if letter.lower() in vowels)
        if syllable_count_word > 2:
            complex_words.append(word)    
 
    syllable_count = 0
    syllable_words =[]
    for word in words:
        if word.endswith('es'):
            word = word[:-2]
        elif word.endswith('ed'):
            word = word[:-2]
        vowels = 'aeiou'
        syllable_count_word = sum( 1 for letter in word if letter.lower() in vowels)
        if syllable_count_word >= 1:
            syllable_words.append(word)
            syllable_count += syllable_count_word


    avg_sentence_len = num_words / num_sentences
    avg_syllable_word_count = syllable_count / len(syllable_words)
    Percent_Complex_words  =  len(complex_words) / num_words
    Fog_Index = 0.4 * (avg_sentence_len + Percent_Complex_words)

    return avg_sentence_len, Percent_Complex_words, Fog_Index, len(complex_words),avg_syllable_word_count


# AVERAGE NO. OF WORDS PER SENTENCE
# COMPLEX WORD COUNT
# SYLLABLE COUNT PER WORD

for file in os.listdir(text_dir):
    x,y,z,a,b = readability(file)
    avg_sentence_length.append(x)
    Percentage_of_Complex_words.append(y)
    Fog_Index.append(z)
    complex_word_count.append(a)
    avg_syllable_word_count.append(b)

# WORD COUNT

def cleaned_words(file):
    with open(os.path.join(text_dir,file), 'r',encoding='utf-8') as f:
        text = f.read()
        text = re.sub(r'[^\w\s]', '' , text)
        words = [word  for word in text.split() if word.lower() not in stopwords]
        length = sum(len(word) for word in words)
        average_word_length = length / len(words)
    return len(words),average_word_length

#AVERAGE WORD LENGTH

word_count = []
average_word_length = []
for file in os.listdir(text_dir):
    x, y = cleaned_words(file)
    word_count.append(x)
    average_word_length.append(y)

# PERSONAL PRONOUNS

def count_personal_pronouns(file):
    with open(os.path.join(text_dir,file), 'r',encoding='utf-8') as f:
        text = f.read()
        personal_pronouns = ["I", "we", "my", "ours", "us"]
        count = 0
        for pronoun in personal_pronouns:
            count += len(re.findall(r"\b" + pronoun + r"\b", text)) 
    return count

pp_count = []
for file in os.listdir(text_dir):
    x = count_personal_pronouns(file)
    pp_count.append(x)

output_df = pd.read_excel('Output Data Structure.xlsx')


output_df.drop([44-37,57-37,144-37], axis = 0, inplace=True)


variables = [positive_score,
            negative_score,
            polarity_score,
            subjectivity_score,
            avg_sentence_length,
            Percentage_of_Complex_words,
            Fog_Index,
            avg_sentence_length,
            complex_word_count,
            word_count,
            avg_syllable_word_count,
            pp_count,
            average_word_length]


for i, var in enumerate(variables):
    output_df[output_df.columns[i+2]] = var


output_df.to_csv('Output_Data.csv')
