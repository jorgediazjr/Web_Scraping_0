from bs4 import BeautifulSoup
import requests
import pandas as pd

def read_in_bible_file():
    '''
    The purpose of this function is to store the
    Bible book names and the chapter count per book
    in a dictionary where the book name is the key
    and the chapter count is the value
    
    Returns
    -------
    dictionary
        key->value = book_name->chapter_count
        e.g. Genesis->50
    '''

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
    '''
    Creates dataframe so that it can be used
    to organize results efficiently and also
    be able to write to a csv file easily

    Returns
    -------
    pandas dataframe
    '''

    chapters = list()
    temp_book = []
    list_of_books = []
    list_of_chapters = []

    # this for loop creates and works with 2 lists
    # to have an "equal" mapping from book to chapter #
    for book in bible:
        for chapter in range(bible[book]):
            chapters.append(int(chapter+1))
        # this line ensures that there will be the same amount
        # of book name as there are chapters
        temp_book = [book] * len(range(bible[book]))
        list_of_books.extend(temp_book)
        list_of_chapters.extend(chapters)
        temp_book = []
        chapters = []
        
    df = pd.DataFrame([list_of_books, list_of_chapters],  dtype=object).transpose()
    df.columns = ['Book', 'Chapter']
    df = df.fillna('')
    # the following 2 lines adds two more columns to the dataframe
    df['# of words/chapter'] = num_of_words
    df['Approx. reading time (mins)'] = approx_reading_time
    return df

def count_num_of_words(soup):
    '''
    Counts the number of words in a chapter and returns that
    number

    Parameters
    ----------
    soup: BeautifulSoup object
        holds html information about the page we requested to 
        extra text from

    Returns
    -------
    int
        an integer that represents number of words for a given chapter
    '''

    verses = soup.find_all('p')
    # deleting last line because it doesn't relate to chapter
    del verses[-1]
    words = 0 
    for verse in verses:
        words += len(verse.get_text().split()) - 1
    return words

def estimate_reading_time(words):
    '''
    Estimates reading time with the assumption that
    the average adult can read 200 words/mins

    Parameters
    ----------
    words: int
        the number of words is necessary for the calculation

    Returns
    -------
    int
        the number of minutes it takes to read the chapter
    '''

    time_to_read = words / 200
    time_to_read = str(time_to_read)
    minutes = int(time_to_read[0: time_to_read.find(".")])
    seconds = float(time_to_read[time_to_read.find("."):]) * 0.60 
    seconds = round(seconds, 2)
    # we round up if seconds is >= .30
    if seconds >= .30:
        return int(minutes+1)
    else:
        return int(minutes)

def loop_through_chapters_of_the(bible):
    '''
    Retrieves info from url given in order to get each chapter
    of the Bible and extra the text, find amount of time to read, etc.

    Parameters
    ----------
    bible: dict
        is used to specify the url in order to retrieve info

    Returns
    -------
    list: num_of_words
        this is a full list of the number of words for every chapter
        and has a one-to-one mapping with the list_of_books and 
        approx_reading_time
    list: approx_reading_time
        this is similar to above description, just that it holds info
        on the number of minutes it takes to read each chapter 
    '''

    num_of_words = list()
    approx_reading_time = list()
    for book in bible:
        for chapter in range(bible[book]):
            if len(book.split()) > 1: # e.g. 1 Samuel
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
    return num_of_words, approx_reading_time

def write_to_file(df):
    '''
    Writes several files
    1. bible.csv file holds all data
    2. bible_books.csv combines the data from each book which
       results in a 66 row 2 column csv file 
    '''

    df.to_csv("bible.csv", index=False) 
    new_df = df.groupby(df['Book'], sort=False)['# of words/chapter', 'Approx. reading time (mins)'].sum()
    new_df = new_df.rename(columns={"# of words/chapter": "# of words/book"})
    new_df.to_csv("bible_books.csv", index=False)

bible = read_in_bible_file()
num_of_words, approx_reading_time = loop_through_chapters_of_the(bible)

df = create_dataframe(bible, num_of_words, approx_reading_time)
write_to_file(df)
