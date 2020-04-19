#################################
##### Name: Siyin Zheng 
##### Uniqname: zhengsy
#################################

from bs4 import BeautifulSoup
import requests, re, csv
import json
import time, sqlite3

CACHE_FILE_NAME = 'cache.json'
CACHE_DICT = {}
baseurl = 'https://www.imdb.com/chart/top'
baseurl2 = 'https://www.imdb.com'

headers = {
    'User-Agent': 'UMSI 507 Course Final Project - Python Web Scraping',
    'From': 'zhengsy@umich.edu',
    'Course-Info': 'https://si.umich.edu/programs/courses/507'
}

##### STEP ONE: CACHE SETUP #####
def open_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    
    Parameters
    ----------
    None
    
    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILE_NAME, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache


def save_cache(cache):
    ''' Saves the current state of the cache to disk
    
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    
    Returns
    -------
    None
    '''
    cache_file = open(CACHE_FILE_NAME, 'w')
    contents_to_write = json.dumps(cache)
    cache_file.write(contents_to_write)
    cache_file.close()


def make_url_request_using_cache(url, cache):
    '''Check the cache for a saved result f
    or this url. If the result is found, return it. 
    Otherwise send a new request, save it, then return it.
    
    Parameters
    ----------
    url: string
        The URL for the API endpoint
    cache: dict
        The dictionary that save

    Returns
    -------
    dict
        the results of the query as a dictionary loaded from cache
        JSON
    '''
    if (url in cache.keys()): # the url is our unique key
        #print("Using cache")
        return cache[url]
    else:
        #print("Fetching")
        time.sleep(1)
        response = requests.get(url, headers=headers)
        cache[url] = response.text
        save_cache(cache)
        return cache[url]

##### STEP TWO: GET DATA FROM IMDB #####
# class Movie:
#     '''Top rated movie from IMDB

#     Instance Attributes
#     -------------------
#     MovieTitle: string
#         the title of a movie (e.g. 'The Shawshank Redemption')
#         some sites have blank category.
    
#     ReleaseYear: string
#         the release year of a movie (e.g. '1994')

#     Director: string
#         the director name of a movie (e.g. 'Frank Darabont')

#     Country: string
#         the produce country of a movie (e.g. 'USA')

#     ImdbRating: string
#         the phone of a movie (e.g. '9.3')
    
#     Vote: string
#         the vote number of a movie (e.g. '2,219,117')

#     URL: string
#         the URL of the IMDB page of a moviw 

#     '''
#     def __init__(self, MovieTitle, ReleaseYear, Director, Country, ImdbRating, Vote, URL):
#         self.MovieTitle = MovieTitle
#         self.ReleaseYear = ReleaseYear 
#         self.Director = Director
#         self.Country = Country
#         self.ImdbRating = ImdbRating
#         self.Vote = Vote
#         self.URL = URL

#     # def info(self):
#     #     '''Get the information of the name, category, address, zipcode, phone of the site.

#     #     Parameters
#     #     ----------
#     #     none

#     #     Returns
#     #     -------
#     #     str
#     #         The information of the site
#     #     '''
#     #     return f"{self.name} ({self.category}): {self.address} {self.zipcode}"


def build_movie_url_dict():
    ''' Make a dictionary that maps top rated movie name to movie page url from "https://www.imdb.com/chart/top/"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a movie name and value is the url
        e.g. {'The Shawshank Redemption':https://www.imdb.com/title/tt0111161/?pf_rd_m=A2FGELUUNOQJNL&pf_rd_p=e31d89dd-322d-4646-8962-327b42fe94b1&pf_rd_r=P8HB2RJ6S5S6NXEWNTWE&pf_rd_s=center-1&pf_rd_t=15506&pf_rd_i=top&ref_=chttp_tt_1, ...}
    '''
    response = make_url_request_using_cache(baseurl, CACHE_DICT)
    soup = BeautifulSoup(response, 'html.parser')
    movie_url = {}
    movies = soup.find(class_="lister-list")
    movie = movies.find_all(class_="titleColumn")
    for m in movie:
        movie_title = m.find("a").text.strip().lower()
        movie_u = m.find("a").get('href')
        movie_url[movie_title]=baseurl2+movie_u
    return movie_url


def get_movie_list(movie_url):
    '''Make a movie instances list from a movie URL.
    
    Parameters
    ----------
    movie_url: string
        The URL for a movie page in IMDB
    
    Returns
    -------
    list
        a movie instance list 
    '''
    response = make_url_request_using_cache(movie_url, CACHE_DICT)
    soup = BeautifulSoup(response, 'html.parser')
    #instances
    MovieTitle = (soup.find("div",{"class":"title_wrapper"}).get_text(strip=True).split('|')[0]).split('(')[0]
    ReleaseYear = ((soup.find("div",{"class":"title_wrapper"}).get_text(strip=True).split('|')[0]).split('(')[1]).split(')')[0]
    ImdbRating = soup.find("span",{"itemprop":"ratingValue"}).text
    Vote = soup.find("span",{"itemprop":"ratingCount"}).text
    Vote = Vote.replace(',','')
    people = soup.find("div",{"class":"credit_summary_item"})
    Director = people.find('a').text.strip()

    detail=[]
    d={'Country':'', 'Gross USA':'','Cumulative Worldwide Gross':''}
    for a in soup.find_all("div",{"class":"txt-block"}):
        c = a.get_text(strip=True).split(':')
        if c[0] in d:
            detail.append(c)
    for i in detail:
        if i[0] in d: 
            d.update({i[0]:i[1]}) 
    Country = d['Country'].split('|')[0]
    GrossUSA = d['Gross USA'].split(' ')[0]
    GrossUSA = GrossUSA.replace('$','')
    GrossUSA = GrossUSA.replace(',','')
    GrossWorld = d['Cumulative Worldwide Gross'].split(' ')[0]
    GrossWorld= GrossWorld.replace('$','')
    GrossWorld= GrossWorld.replace(',','')
    URL = movie_url
    movie_instance = [MovieTitle, Director, Country, ReleaseYear, ImdbRating, Vote, GrossUSA, GrossWorld,URL]
    return movie_instance

def get_director_list(movie_url):
    '''Make a diector instances list from a movie URL.
    
    Parameters
    ----------
    movie_url: string
        The URL for a movie page in IMDB
    
    Returns
    -------
    list
        a director instance list 
    '''
    response = make_url_request_using_cache(movie_url, CACHE_DICT)
    soup = BeautifulSoup(response, 'html.parser')
    #go to director page
    director_url = soup.find("div",{"class":"credit_summary_item"}).find('a').get('href')
    director_url = baseurl2 +director_url
    print(director_url)
    res = make_url_request_using_cache(director_url, CACHE_DICT)
    dir_soup = BeautifulSoup(res, 'html.parser')
    NameSection = dir_soup.find('div',{'id':'name-overview-widget'})
    DirectorName = NameSection.find(class_='itemprop').text.strip()
    try:
        BornInfo = dir_soup.find('div',{'id':'name-born-info'})
        BornYear = BornInfo.find_all('a')[-2].text.strip()
        BornPlace = BornInfo.find_all('a')[-1].text.strip()
        BornCountry = BornPlace.split(', ')[-1]
        BornState = BornPlace.split(', ')[-2]
    except:
        BornYear = 'No info'
        BornState = 'No info'
        BornCountry = 'No info'
    try:
        Height = dir_soup.find('div',{'id':'details-height'}).text.strip()
        Height = Height.replace('Height:','').strip()
    except:
        Height = 'No info'
    director_instance = [DirectorName,BornYear,BornCountry,BornState,Height]
    return director_instance

def write_csv(filepath, data):
    '''
    Write <data> to the .csv file specified by <filename>

    Parameters
    ----------
    filepath: string 
        the name of the file which stores the data
    data: list

    Returns
    -------
        None
    '''
    with open(filepath,"w", newline="") as f:
        wr = csv.writer(f)
        for row in data:
            wr.writerow(row)

##### STEP THREE: BUILD DATABASE #####
def create_imdb_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    drop_movie = '''
        DROP TABLE IF EXISTS "Movies";
    '''
    drop_director = '''
        DROP TABLE IF EXISTS "Directors";
    '''

    create_director = '''
        CREATE TABLE IF NOT EXISTS "Directors" (
            "Id"        INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            "DirectorName"  TEXT NOT NULL,
            "BornYear" INTEGER NOT NULL,
            "BornCountry"  TEXT NOT NULL,
            "BornState"    TEXT NOT NULL,
            "Height"    TEXT NOT NULL
        );
    '''
    create_movie = '''
        CREATE TABLE IF NOT EXISTS "Movies" (
            "Id"        INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            "MovieTitle"  TEXT NOT NULL,
            "DirectorId" INTEGER NOT NULL,
            "Country"  TEXT NOT NULL,
            "ReleaseYear"    INTEGER NOT NULL,
            "ImdbRating"    REAL NOT NULL,
            "Vote"    INTEGER NOT NULL,
            "GrossUSA"    TEXT NOT NULL,
            "GrossWorld"    TEXT NOT NULL,
            "URL"  TEXT NOT NULL,
        FOREIGN KEY("DirectorId") REFERENCES "Directors"("Id")
        );
    '''
    cur.execute(drop_director)
    cur.execute(create_director)
    cur.execute(drop_movie)
    cur.execute(create_movie)

def load_movies():
    file_contents = open('movie_table.csv', 'r')
    csv_reader = csv.reader(file_contents)
    
    select_director_id_sql = '''
        SELECT Id FROM Directors
        WHERE DirectorName = ?
    '''
    insert_bar_sql = '''
        INSERT INTO Movies
        VALUES (NULL, ?, ?, ?, ?, ?, ?, ?,?,?)
    '''

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    for row in csv_reader:
        # get Id for director name
        cur.execute(select_director_id_sql, [row[1]])
        res = cur.fetchone()
        director_id = None
        if res is not None:
            director_id = res[0]

        cur.execute(insert_bar_sql, [
            row[0], # MovieTitle
            director_id, # DirectorID
            row[2], # Country
            row[3], # ReleaseYear
            row[4], # Imdbrating
            row[5], # Vote
            row[6], # URL
            row[7], # GrossUSA
            row[8]  # GrossWorld
        ])
    conn.commit()
    conn.close()

def load_directors(): 
    file_contents = open('director_table.csv', 'r')
    csv_reader = csv.reader(file_contents)

    insert_bar_sql = '''
        INSERT INTO Directors
        VALUES (NULL, ?, ?, ?, ?, ?)
    '''

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    for row in csv_reader:
        cur.execute(insert_bar_sql, [
            row[0], # DirectorName
            row[1], # BornYear
            row[2], # BornCountry
            row[3], # BornState
            row[4], # Height
        ])
    conn.commit()
    conn.close()

##### STEP FOUR: Interactive choices
# def get_top_movies(num):

# def pop_movie_year():

# def pop_movie_country_ave_vote():

# def pop_movie_rating_gross():

# def pop_ave_height_director_country():

# def commend():

if __name__ == "__main__":
    CACHE_DICT = open_cache()
    movie_list = build_movie_url_dict()
    movies = []
    directors = []

    ## Load data to csv file:
    # for k,v in movie_list.items():
    #     movie_instance = get_movie_list(v)
    #     movies.append(movie_instance)
    #     director_instance = get_director_list(v)
    #     if director_instance not in directors:
    #         directors.append(director_instance)
    # movie_path = 'movie_table.csv'
    # director_path = 'director_table.csv'
    # write_csv(movie_path,movies)
    # write_csv(director_path,directors)

    ## Import csv file to sqlite database
    DB_NAME = 'IMDB.db'
    create_imdb_db()
    load_directors()
    load_movies()

    ## 
