## Scrape the [CIA World Factbook - Terrorist Organizations](https://www.cia.gov/the-world-factbook/references/terrorist-organizations/) to geolocate referenced "Areas of Operation" in ISO3 format
### PURPOSE: This code and resulting dataset is desinged for use with ArcGIS Pro to map each CIA World Factbook Terrorist Organizaion's *Area(s) of Operation* with the matching country using the ISO3 code.
*The dataset can be used independently for other mapping purposes.*
### Python libraries used:
- Beautiful Soup
- Pandas
- Country Converter (coco)

\
**See [HOW_TO_SCRAPE_LINKS.md](HOW_TO_SCRAPE_LINKS.md) for the best way to prepare for sraping.**
### Example of HTML file used - NOTE: to run the code as designed, the HTML should be saved as stated above.
[CIA_t_o.html](CIA_t_o.html)
### This notebook contains the code used to scrape and geolocate the data.
[geolocate_t_orgs.ipynb](geolocate_t_orgs.ipynb)
### Resulting Dataset
[wfb_t_orgs_geolocated.csv](wfb_t_orgs_geolocated.csv)
### This notebook contains the arcpy code required to convert the *wfb_t_orgs_geolocated.csv* dataset into a combined feature class and if needed, feature classes containing the area(s) of operation for each t_org individually.
[arcgis_map_t_org_aors.ipynb](ArcGIS_mapping_t_orgs/arcgis_map_t_org_aors.ipynb)
