# IMDB_web_scraping
This is Siyin Zheng's final project for SI 507 (2020 Winter).

Data Source: https://www.imdb.com/chart/top/

More Info: After running the program, please open up a browser tab and type http://127.0.0.1:5000/ into the address bar. You will be shown a website with five questions, which gives you five different options to visualize data from the data source. Based on the questions you pick, you may be able to add extra filters to explore the data. For example, for question one, you could enter the number of movies you want to see and add a country filter, the default value will be with all the records. For question four, when you see the visualization, you are able to use the slider to choose different time periods to visualize. All the visualizations are provided through Plotly and Flask.

Structure: Caching was set up first, the database was created, then the data source was scraped and crawled and information was stored into the tables. Data was processed from the database and then mapped. 
