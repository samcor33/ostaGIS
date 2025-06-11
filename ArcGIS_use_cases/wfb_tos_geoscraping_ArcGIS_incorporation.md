# Map CIA designated bad actors using ArcGIS Pro
### Scrape and geolocate the [CIA World Factbook - Terrorist Organizations](https://www.cia.gov/the-world-factbook/references/terrorist-organizations/) using `wfb_tos_geoscraper()` and `parse_country()` as seen below.
```
ostaGIS.parse_country(
    df=wfb_tos_geoscraper(saved_html = r"C:/Users/me/my_project/CIA_t_o.html"), 
    col_to_be_parsed="area of operation", 
    new_match_column="country_aor"
).to_csv("C:/Users/me/my_project/datasets/wfb_t_orgs_geolocated.csv")
```
#### Resulting Dataset
[wfb_t_orgs_geolocated.csv](wfb_t_orgs_geolocated.csv)
<br>
<br>

---
### Use `goematch_and_multiply()` in ArcGIS Pro to convert `wfb_t_orgs_geolocated.csv` into feature classes containing the area(s) of operation for each t_org individually.

**Example:**
```
ostaGIS.geomatch_and_multiply(
    countries_fc = "World_Countries_one_poly_per_c",
    iso_table = "wfb_t_orgs_geolocated",
    name_col="index"
)
```
#### ArcGIS Results
```
country_mult.gdb
 > indidivual_fc (feature dataset)
 >> all indiv mapped feature classes
 > countries_muliplied (polygon feature class)
 > stats_table
```

**countries_multiplied**
![image](https://github.com/user-attachments/assets/130ac670-8406-4ac9-abdb-1e29ff92b769)


**individual_fc - all feature classes**
![image](https://github.com/user-attachments/assets/ceb52d63-53da-4461-95d3-f468f7af32e8)

---
### Assign specific symbology to all individual t_orgs within a group layer using `apply_style_to_gp_lyr()` to show hot spots of overlapping countries.

**Example:**
~~~
ostaGIS.apply_style_to_gp_lyr(
    gp_lyr_name="gp_lyr",
    style_name='t_org_aor'
)
~~~
Resulting Map with overlapping layers using transparency to identify country hotspots.
![image](https://github.com/user-attachments/assets/0483f860-62a4-46a3-a322-bf236fbf76dd)
