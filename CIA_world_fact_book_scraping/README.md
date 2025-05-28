## Scrape country links from the CIA World Factbook and geolocate in ISO3 format
### PURPOSE: This code and resulting dataset is desinged for use with ArcGIS Pro to map each CIA World Factbook entry (link) with the matching country using the ISO3 code.
*The datasets can be used independently for other mapping purposes.*
### Python libraries used:
- Selenium
- Time
- Pandas
- Country Converter (coco)

\
**See [HOW_TO_SCRAPE_LINKS.md](https://github.com/samcor33/ostaGIS/main/CIA_world_fact_book_scraping/HOW_TO_SCRAPE_LINKS.md) for the best way to prepare for sraping.**
### Example of HTML file used - NOTE: to run the code as designed, the HTML should be saved as stated above.
[CIA_wfb.html](https://github.com/samcor33/ostaGIS/main/CIA_world_fact_book_scraping/CIA_wfb.html)
### This notebook contains the code used to scrape and geolocate the data
[wfb_scrape.ipynb](https://github.com/samcor33/ostaGIS/main/CIA_world_fact_book_scraping/wfb_scrape.ipynb)
### Resulting Datasets
[wfb_countries_coded.csv](https://github.com/samcor33/ostaGIS/main/CIA_world_fact_book_scraping/wfb_countries_coded.csv)
<br>
[wfb_countries_no_code.csv](https://github.com/samcor33/ostaGIS/main/CIA_world_fact_book_scraping/wfb_countries_no_code.csv)
