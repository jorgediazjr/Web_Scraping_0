from bs4 import BeautifulSoup
import requests
import pandas as pd

def read_in_bible_file():
    bible_dict = {}
    with open("bible.txt", "r") as file:
        for line in file:
            temp_line = line.split(" ")
            # if its just a book and chapter number execute this code
            # else if there is more than one book e.g. 1 Kings
            # or if the name of the book is long e.g. The Song of Solomon
            if len(temp_line) == 2:
                bible_dict[temp_line[0]] = int(temp_line[-1].replace('\n',''))
            else:
                bible_dict[' '.join(temp_line[0:-1])] = int(temp_line[-1].replace('\n',''))
    return bible_dict

def create_dataframe(bible, num_of_words, approx_reading_time):
    updated_bible_dict = dict()
    chapters = list()
    temp_book = []
    list_of_books = []
    list_of_chapters = []

    for book in bible:
        for chapter in range(bible[book]):
            chapters.append(int(chapter+1))
        temp_book = [book] * len(range(bible[book]))
        list_of_books.extend(temp_book)
        list_of_chapters.extend(chapters)
        temp_book = []
        chapters = []
        
    df = pd.DataFrame([list_of_books, list_of_chapters],  dtype=object).transpose()
    df.columns = ['Book', 'Chapter']
    df = df.fillna('')
    df['# of words/chapter'] = num_of_words
    df['Approx. reading time (mins)'] = approx_reading_time
    print(df)
    return df


def count_num_of_words(soup):
    verses = soup.find_all('p')
    del verses[-1]
    words = 0 
    for verse in verses:
        words += len(verse.get_text().split()) - 1
    return words


def estimate_reading_time(words):
    time_to_read = words / 250
    time_to_read = str(time_to_read)
    minutes = int(time_to_read[0: time_to_read.find(".")])
    seconds = float(time_to_read[time_to_read.find("."):]) * 0.60 
    seconds = round(seconds, 2)
    if seconds >= .30:
        return int(minutes+1)
    else:
        return int(minutes)

def loop_through_chapters_of_the(bible):
    num_of_words = list()
    approx_reading_time = list()
    for book in bible:
        for chapter in range(bible[book]):
            if len(book.split()) > 1:
                upd_book = book.replace(" ","-")
                url = "https://www.kingjamesbibleonline.org/{}-Chapter-{}/".format(upd_book, chapter+1)
                page = requests.get(url)
                soup = BeautifulSoup(page.content, 'html.parser')
                words = count_num_of_words(soup)
                reading_time = estimate_reading_time(words)
                num_of_words.append(words)
                approx_reading_time.append(reading_time)
            else:
                url = "https://www.kingjamesbibleonline.org/{}-Chapter-{}/".format(book, chapter+1) 
                page = requests.get(url)
                soup = BeautifulSoup(page.content, 'html.parser')
                words = count_num_of_words(soup)
                reading_time = estimate_reading_time(words)
                num_of_words.append(words)
                approx_reading_time.append(reading_time)
            print(url)
    print(len(num_of_words))
    print(len(approx_reading_time))
    return num_of_words, approx_reading_time


def write_to_file(df):
    df.to_csv("bible.csv", index=False) 
    df.to_csv("display.csv", index=False, sep="\t")    


bible = read_in_bible_file()
num_of_words, approx_reading_time = loop_through_chapters_of_the(bible)

df = create_dataframe(bible, num_of_words, approx_reading_time)
write_to_file(df)
