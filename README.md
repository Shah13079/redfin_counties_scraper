# redfin_counties_scraper
Python scrapy script to crawl properties listings from counties included for sale and sold.

### Goal <br />
Collect information from land listings on RedFin.

### Input <br />
A CSV with three columns. First column is County. Second Column is State. Third colum is Filter. This is comes from the URL when the search results are filtered by time.
Script support For Sales (no filter), and all filters like 1 Month (sold-1mo), 3 Months (sold-3mo), 6 Months (sold-6mo) and 1 Year (sold-12yr).

### Output <br />
A new CSV matching the format of the `Example of Output CSV`


### Behavior of Script <br />
1. Read CSV file
2. Loop through each county and make a search given the search parameters (ex: Teller County, CO and 6mo)
3. Visit all listing results for the search (ex: In Teller County, there's about 198 sold listings).
   This includes navigating to each search result page.
4. Scrape the following information from each listing: </br>
Status, County, State, City, Address, Zip, Latitutde, Longitude, APN, Lot Size, Price, Community, Description, Sold Date, Days On Market, MLS, HOA Dues, Sales History, Link

### Technologies <br />
Python Scrapy framework is entirely used in this project and scrapy-selenium is used for some request to main page of listings. 

### Technical approach <br />
1. The program first take location from list of csv.
2. Find out its latitude and longitude coordinates by calling a third party API.
3. Sending request to another URL combination of Google map and redfin website, to get route search URL for location.
4. Then sending request to route URL with different filters, and saving data into csv file.

### Run the Program <br />
1. Install required dependecies by ( pip install -r requirements.txt) in cmd (at project directory).
2. command: scrapy crawl listings




