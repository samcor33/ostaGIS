## Parse the [State Department travel advisory XML feed](https://travel.state.gov/_res/rss/TAsTWs.xml/) to geolocate countries into ISO3 format
### PURPOSE: This code and resulting dataset is desinged for use with ArcGIS Pro to map each Travel Advisory/Warning with the matching country using the ISO3 code.
*The dataset can be used independently for other mapping purposes.*
### Python libraries used:
- Feedparser
- Pandas
- Country Converter (coco)

### Code used to parse and geolocate the data. _(notes within code)_
[RSS_scraper_for_state_dept_travel_advisories](RSS_scraper_for_state_dept_travel_advisories)
### Resulting Dataset - Must be saved in Excel format due to cells containing large HTML values
[travel_advisories.xlsx](travel_advisories.xlsx)
