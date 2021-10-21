# Icon Web Scraper and Generator

This project serves as python scripts for performing the webscraping of restaurant's/business's icons from a Google Search Page.

It was originally developed as a supporting feature for the food finding web app [Delish](https://github.com/cyruskarsan/Delish-Food) that I developed with several colleagues at UCSC.

Selenium is the library utilized for webscraping and the chrome driver is run in a headless manner to facilitate the the scraping.

The desired image/div to be scraped can be altered within the RestaurantIconScraper.py script. After the image is scraped, it is stored within an 'images' directory created at the root.

In order to turn the images retrieved from RestaurantIconScraper.py, one can utilize the ImageConvertToIcon.py script in order to alter every file in the 'images' directory to icons (icon sizing can be specified in this script).

Further development will take place to make the use case more general and exist as a library for web scraping and formatting images on the web.
