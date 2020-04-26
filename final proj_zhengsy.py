#################################
##### Name: Siyin Zheng 
##### Uniqname: zhengsy
#################################

from bs4 import BeautifulSoup
import requests, re, csv
import json
import pandas as pd
import time, sqlite3
from flask import Flask, render_template, request
import plotly.graph_objects as go
import plotly.express as px
import numpy as np 

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


##### STEP FOUR: Interactive choices #####
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


##### First vis: Movie table #####
def get_top_movies(number=None, country = None):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    limit = f'LIMIT {number}'
    where_movie = ''
    if (country != None):
        where_movie = f'WHERE Country = "{country}"'
    
    q = f'''
        SELECT MovieTitle, ReleaseYear, Country, DirectorName, ImdbRating, Vote
        FROM Movies
        JOIN Directors
        ON DirectorId = Directors.Id
        {where_movie}
        {limit}
    '''
    data = cur.execute(q).fetchall()
    conn.close()
    return data


@app.route('/movie_detail', methods=['POST'])
def bars():
    num = request.form['rank']
    country = request.form['country']
    if country == '':
        country = None
    results = get_top_movies(number = num,country = country)
    return render_template('table.html', results=results,
        country=country)


##### Second vis: Movie Peak Year #####
def pop_movie_year(country = None):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    where_movie = ''
    if (country != None):
        where_movie = f'WHERE Country = "{country}"'
    q = f'''
        SELECT ReleaseYear
        FROM Movies
        {where_movie}
        '''
    data = cur.execute(q).fetchall()
    df = pd.DataFrame(data)
    df.columns = ['ReleaseYear']
    conn.close()
    return df


@app.route('/movie_year', methods=['POST'])
def year():
    country = request.form['country_year']
    if country == '':
        country = None
    df = pop_movie_year(country)
    years = df['ReleaseYear'].value_counts().keys().tolist()
    counts = df['ReleaseYear'].value_counts().tolist()
    bars_data = go.Bar(x=years, y=counts)
    fig = go.Figure(data=bars_data)
    fig.update_layout(title="Years for most popular movies", xaxis_title="Year", yaxis_title="Movie counts")
    div = fig.to_html(full_html=False)
    return render_template("plot1.html", plot1_div=div)


##### Third vis: Movie Rating #####
def pop_movie_country_ave_vote():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    q = f'''
        SELECT Country, ImdbRating, Vote
        FROM Movies
        '''
    data = cur.execute(q).fetchall()
    conn.close()
    df = pd.DataFrame(data)
    df.columns = ['Country', 'ImdbRating','Vote']
    return df


@app.route('/movie_rating')
def rating():
    df = pop_movie_country_ave_vote()
    country = df.groupby(['Country']).mean().reset_index()[['Country']].round(1).Country.tolist()
    rating = df.groupby(['Country']).mean().reset_index()[['ImdbRating']].round(1).ImdbRating.tolist()
    vote = df.groupby(['Country']).mean().reset_index()[['Vote']].round(1).Vote.tolist()
    count = df.groupby(['Country']).count().reset_index()[['Vote']].Vote.tolist()
    fig = px.scatter(x = rating, y = vote, size=count,color= country, hover_name= country, size_max=60, 
            range_x=[8,9], range_y=[0,1600000])
    fig.update_layout(title="Hub for most popular movies", xaxis_title="Average IMDB Rating", yaxis_title="Average Votes")
    div = fig.to_html(full_html=False)
    return render_template("plot2.html", plot2_div=div)


##### Fourth vis: Movie Gross #####
def pop_movie_rating_gross():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    q = f'''
        SELECT MovieTitle, ImdbRating, GrossWorld, ReleaseYear
        FROM Movies
        '''
    data = cur.execute(q).fetchall()
    conn.close()
    df = pd.DataFrame(data)
    df.columns = ['MovieTitle', 'ImdbRating', 'GrossWorld', 'ReleaseYear']
    df['Time'] = np.where(df['ReleaseYear'] < 1950 , '1940s','later')
    df.loc[(df.ReleaseYear < 1960)&(df.ReleaseYear >= 1950),'Time']='1950s'
    df.loc[(df.ReleaseYear < 1970)&(df.ReleaseYear >= 1960),'Time']='1960s'
    df.loc[(df.ReleaseYear < 1980)&(df.ReleaseYear >= 1970),'Time']='1970s'
    df.loc[(df.ReleaseYear < 1990)&(df.ReleaseYear >= 1980),'Time']='1980s'
    df.loc[(df.ReleaseYear < 2000)&(df.ReleaseYear >= 1990),'Time']='1990s'
    df.loc[(df.ReleaseYear < 2010)&(df.ReleaseYear >= 2000),'Time']='2000s'
    df.loc[(df.ReleaseYear < 2020)&(df.ReleaseYear >= 2010),'Time']='2010s'
    df.dropna(how='all')
    return df


@app.route('/movie_gross')
def gross():
    df = pop_movie_rating_gross()
    fig = px.scatter(df, x = 'ImdbRating', y = 'GrossWorld', color= 'ImdbRating', hover_name= 'MovieTitle', animation_frame="Time", 
            category_orders={'Time':['1940s','1950s','1960s','1970s','1980s','1990s','2000s','2010s']}, 
            animation_group='MovieTitle', log_y = True)
    fig.update_layout(xaxis_title="IMDB Rating", yaxis_title="World Gross")
    div = fig.to_html(full_html=False)
    return render_template("plot3.html", plot3_div=div)


##### Fifth vis: Directors #####
def pop_director_country():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    q = f'''
        SELECT ImdbRating, BornCountry, BornState, DirectorName
        FROM Directors
        JOIN Movies
        ON Directors.Id = Movies.DirectorId
        GROUP BY DirectorName
        '''
    data = cur.execute(q).fetchall()
    conn.close()
    df = pd.DataFrame(data)
    df.columns = ['Rating', 'BornCountry', 'BornState','DirectorName']
    df = df.replace('Austria-Hungary [now Austria]','Austria')
    df = df.replace('Czechoslovakia [now Czech Republic]','Czech Republic')
    df = df.replace('Austria-Hungary [now Hungary]','Hungary')
    df = df.loc[~((df['BornCountry']=='No info'))]
    BornCountry = df.BornCountry.tolist()
    BornCountry = [item.replace(']','') for item in BornCountry]
    df['BornCountry']=BornCountry
    return df


@app.route('/directors')
def director():
    df = pop_director_country()
    fig = px.treemap(df, path=['BornCountry', 'BornState'], values='Rating')
    div = fig.to_html(full_html=False)
    return render_template("plot4.html", plot4_div=div)


##### Main Function #####
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

    ## Using Flask to present visualizations 
    app.run(debug=True)

