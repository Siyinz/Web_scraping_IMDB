# Web Crawler for IMDB Movie data
This is Siyin Zheng's final project for SI 507 (2020 Winter).

Project Demo Video: https://www.youtube.com/watch?v=KyLZdBQrUjQ

During this unprecedented time, everyone in the state is asked for staying at home and reducing the time of going out. People want to watch more movies with their beloved ones at home. Let's know more about IMDB Top 250 movies and find the most interesting one to watch!

### Project code
- Link to GitHub repo for your final project code:
https://github.com/Siyinz/IMDB_web_scraping
- README containing any special instructions for running your code (e.g., how to apply API keys) as well as a brief description of how to interact with your program.

After running the program, please open up a browser tab and type http://127.0.0.1:5000/ into the address bar. You will be shown a website with five questions, which gives you five different options to visualize data from the data source. Based on the questions you pick, you may be able to add extra filters to explore the data. For example, for question one, you could enter the number of movies you want to see and add a country filter, the default value will be with all the records. For question four, when you see the visualization, you are able to use the slider to choose different time periods to visualize. All the visualizations are provided through Plotly and Flask.

● Required Python packages for this project to work:
- beautifulsoup4 4.8.2
- Flask 1.1.1
- numpy 1.18.1
- plotly 4.2.1
- pandas 0.25.1
- requests 2.22.0

### Data sources
#### IMDB Website
- Origin: https://www.imdb.com/chart/top/
- Format: HTML
- I used beautiful soup to crawl and scrape data from the website. I used the caching and saved the data I got from the website into a json file (currently in .gitignore). Then I imported data from cache into two csv tables - movies table and directors table.
- Summary of data
1. For the movie table, there are 250 records available (top 250 movies) and I retrieved 250 records. For each record, I included Movie Title, Director Name, Country, Release Year, IMDB Rating, Vote Number, Gross USA (in USD), Gross World (in USD), URL (link to the IMDB page of the movie).
2. For the director table, for 250 movies, there is supposed to be 250 directors. After removing duplicates, I retrieved 152 records. For each record, I included Director Name, Born Year, Born Country, Born State, and Director’s Height.

### Database
Database schema (SQL CREATE TABLE statements indicating table names, fields, data types, and constraints)
![database](https://github.com/Siyinz/IMDB_web_scraping/blob/master/SQLdatabase.png)
There is one foreign key-primary key relation: DirectorId in Movies Table = Id in Directors Table.

### Interaction and Presentation Options
Users are able to make commands to see five kinds of results, which will be implemented by a command function.
1. Top-rated movies details (users could enter the number of movies and the specific country they want to see). Details will be provided in a table.
2. Years for most popular movies. Top 250 movies will be grouped by release year, and the count of movies in each year will be presented by a bar chart. Users are able to filter the country.
3. Average rating and votes by country. Top 250 movies will be grouped by the produced country, and the average movie rating and votes of each country will be presented by a bubble chart.
4. Higher rating, the higher grossing of the movie? An animated scatter plot will be used to show the relations between the movie’s rating and world gross number. Users are able to use the slider to select a specific time period to visualize.
5. The country with the most talented directors. 152 directors will be grouped by their born places. A treemap is used to explore which country and area have the most talented directors. The size depends on the sum of the movie ratings by directors who were born in the selected area.

I use both Flask and Plotly. Plotly will be used to produce 4 visualizations. The first option will be presented in a table via flask. The interactive parts and presentation will be supported by Flask, where the main page provides five options. After users choose an option, the page will be directed to correspondent visualizations (charts/table).

After running the program, please open up a browser tab and type http://127.0.0.1:5000/ into the address bar. You will be shown a website which five questions, which gives you five different options to visualize data from the data source. Based on the questions you pick, you may be able to add extra filters to explore the data. For example, for question one, you could enter the number of movies you want to see and add a country filter, the default value will be with all the records. For question four, when you see the visualization, you are able to use the slider to choose different time periods to visualize.
