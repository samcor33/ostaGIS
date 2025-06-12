# ostaGIS - Open Source Threat Analysis GIS
### Methods for collecting OSINT to conduct threat analysis through GIS.

##### [state_dept_twas](#ostagispy----state_dept_twas)
##### [parse_country](#ostagispy----parse_country)
##### [vals_to_df](#ostagispy----vals_to_df)
##### [wfb_country_scraper](#ostagispy----wfb_country_scraper)
##### [wfb_tos_geoscraper](#ostagispy----wfb_tos_geoscraper)
##### [geomatch_and_multiply](#ostagispy----geomatch_and_multiply)
##### [apply_style_to_gp_lyr](#ostagispy----apply_style_to_gp_lyr)

**For specific use cases in ArcGIS Pro see [this folder](ArcGIS_use_cases)**
___
# ostaGIS.py - > state_dept_twas
[Back to top](#ostagis---open-source-threat-analysis-gis)
#### PURPOSE: Parse the [State Department travel advisory XML feed](https://travel.state.gov/_res/rss/TAsTWs.xml/) to geolocate countries into ISO3 format.
###### NOTE: This code and resulting dataset is designed for use with ArcGIS Pro to map each country's Travel Warning/Advisory using the ISO3 code.
*The dataset can be used independently for other mapping purposes.*
#### Python libraries used:
- Feedparser
- Pandas
- Country Converter (coco)
- Logging
- Typing

##### Extract RSS feed and goelocate State Department Travel Warnings/Advisories.
~~~
def state_dept_twas(export_path, log="CRITICAL"):
    """
    Description:
        Extract RSS feed and goelocate State Department Travel Warnings/Advisories. Exports to Excel.
        Geolocated using ISO3 code.
        *Desinged for use with GIS software.
        State Dept RSS Feed - 'https://travel.state.gov/_res/rss/TAsTWs.xml/'
    Params:
        export_path: destination for dataset(.xlsx)
        log: "CRITICAL" or "INFO" will denote whether the 'not found' regexes are displayed as an error.
              CRITICAL - 'not found' regexes will not be displayed.
              INFO - 'not found' regexes will be displayed.
    """
    import feedparser
    import pandas as pd
    import country_converter as coco
    import logging
    from typing import Any
    
    # Check that the 'log' param is 'CRITICAL' or 'INFO'
    if log == "CRITICAL":
        coco_logger = coco.logging.getLogger()
        coco_logger.setLevel(logging.CRITICAL)
    elif log == "INFO":
        coco_logger = coco.logging.getLogger()
        coco_logger.setLevel(logging.INFO)
    else:
        raise Exception(f"log param cannot equal '{log}'...log must equal 'CRITICAL' or 'INFO'")

    if not export_path.endswith(".xlsx"):
        raise Exception("exported dataset is an excel file and must end with '.xlsx'")

    # Start of fucntion
    feed = feedparser.parse('https://travel.state.gov/_res/rss/TAsTWs.xml/')
    
    country_threat_info = {}
    if feed.status == 200:    
        for entry in feed.entries:
            #print(entry)
            for tag in entry.tags:
                    
                # Fuction to get the country name directly from the travel advisory url since the threat levels can be non-standard to parse and match with COCO
                def parse_country(url):
                    pc = url.split("/")
                    # V - This is bad code but it works - V
                    parsed_country = pc[len(pc) - 1].removesuffix("-travel-advisory.html").replace('advisory', "").replace('travel', "").replace("-", " ").replace(".html", "").title()
                    #Specifically handles the "Azerbajian" naming error from the State Dept
                    if parsed_country == "Azerbajian":
                        parsed_country = 'Azerbaijan'
                        return parsed_country
                    else:
                        return parsed_country
                
                # This statement specifically handles the labeling issue with the 'Israel, the West Bank and Gaza' Travel Advisory
                if entry.title == 'See Individual Summaries -':
                    country_threat_info['IL'] = {
                        'label': 'Israel, the West Bank and Gaza - See Individual Summaries',
                        'link': entry.link,
                        'published': entry.published,
                        'summary': entry.summary,
                        'summary_cont': None,
                        'DoS_country_name': parse_country(entry.link)
                    }
                # This statement is the standard parsing code
                elif "Country-Tag" in tag.values():
                    country_threat_info[list(tag.values())[0]] = {
                        'label': entry.title,
                        'link': entry.link,
                        'published': entry.published,
                        'summary': entry.summary,
                        'summary_cont': None,
                        'DoS_country_name': parse_country(entry.link)
                    }
    
    else:
        print("Failed to retrieve the RSS feed. Status code:", feed.status, link)
    
    twa_df = pd.DataFrame(country_threat_info).transpose().reset_index().rename(columns={"index": "DoS_gen2alpha"})
    
    # ****************** PARSE OUT SECURITY REPORT *************************************************
    sec_reports = []
    for s in twa_df['summary']:
        sec_rep = "https://www.osac.gov/"
        if sec_rep in s:
            tail_url = s.split(sec_rep, 1)[1].split(">", 1)
            full_sec_rep_url = sec_rep + tail_url[0]
            sec_reports.append(full_sec_rep_url.replace('"', ""))
        else:
            sec_reports.append("https://www.osac.gov/Content/Browse/Report?subContentTypes=Country%20Security%20Report")
    
    twa_df["security_report"] = pd.Series(sec_reports)
    # ****************** PARSE OUT SECURITY REPORT *************************************************
    
    # Check if any Summary text is over the 32000 limit for exporting to csv
    for s in twa_df['summary']:
        
        # Split the summary at the midpoint using chunk_at_midpoint
        # This is not dynamic but it's likely no summary will be over 64000 characters...Mexico is the only one over 32000 by a large margin
        def chunk_at_midpoint(text):
            words = text.split()
            midpoint = int(len(words) / 2)
            return [' '.join(words[i:i+midpoint]) for i in range(0, len(words), midpoint)]
            
        if len(s) > 32000:
            # Get indexing information to chnage text using the '.loc' method 
            fltr = twa_df[twa_df['summary'] == s]
            row = fltr.index[0]
            s_clmn = twa_df.columns[twa_df.columns == "summary"][0]
            sc_clmn = twa_df.columns[twa_df.columns == "summary_cont"][0]
            
            chunk = chunk_at_midpoint(s)
    
            # Save text chunck to appropriate columns
            twa_df.loc[row, s_clmn] = chunk[0]
            twa_df.loc[row, sc_clmn] = chunk[1]
    
    # Split country/threat level and keep threat level only
    cnt = twa_df['label'].str.split(" - ", n=1, expand=True).rename(columns={1: "threat_level"}).drop(columns=0)
    twa_df= cnt.join(twa_df)
    
    # Match countries thru COCO to assign proper **3 Digit ISO Code**
    cc = coco.CountryConverter()
    countries = twa_df['DoS_country_name']
    
    country_names = cc.pandas_convert(countries, to='name_short')
    twa_df['country'] = country_names
    twa_df = twa_df.explode('country')
    
    country_iso3_codes = cc.pandas_convert(twa_df['country'], to='ISO3')
    twa_df['ISO3_CODE'] = country_iso3_codes
    twa_df = twa_df.explode('ISO3_CODE')
    
    # Remove advisories for locations without an ISO3 Code then sort alphabetically
    twa_df = twa_df[twa_df['country'] != 'not found']
    twa_df = twa_df.sort_values('country')
    
    # Put Mexico at the top for ArcGIS Pro importing
    # The longest text must be at the top so when it's imported, it automatically makes the character length 32767.
    # You may need to adjust the country below if Mexico's summary falls below 32767 and another country's summary exceeds 32767
    m = twa_df[twa_df['ISO3_CODE'] == 'MEX']
    m_df = pd.DataFrame(m)
    twa_df = twa_df.drop(m.index[0])
    twa_df = pd.concat([m_df, twa_df])
    twa_df = twa_df.reset_index().drop(columns='index')
    
    # Rearrange columns for finished dataset
    twa_df_final = twa_df
    twa_df_final = twa_df_final[['country', 'threat_level', 'published', 'security_report', 'link', 'summary', 'summary_cont', 'ISO3_CODE', 'label', 'DoS_country_name', 'DoS_gen2alpha']]
    twa_df_final.to_excel(export_path, sheet_name='travel_advisories')
~~~
### Resulting Dataset - Must be saved in Excel format due to cells containing large HTML values
[travel_advisories.xlsx](travel_advisories.xlsx)

___
# ostaGIS.py - > parse_country
[Back to top](#ostagis---open-source-threat-analysis-gis)
#### PURPOSE: Parse and geocode countries mentioned within a text to then geolocate that text using GIS software.
#### Python Librarys Used:
- Pandas
- Country_Converter (coco)
- Logging
- Typing

##### READ ME
This fuction was designed to parse many entries of text within a padas DataFrame. Another function has been provided (vals_to_df) to quickly convert a *list* to a DataFrame to use the parse_country function.

##### Description:
Use to parse country names that can be found in a string of text stored in a df cell. Geolocate the countries using regex and match to the ISO3 code. Return an exploded or unexploded df that contains all the countries ISO3 codes that were found in the text.

##### Output:
An exploded or unexploded DataFrame with the text and corrosponding ISO3 country code.

##### NOTE: This function may not catch all countries within a text.

#### See [notebook](help/parse_country_examples.ipynb) for examples

```
def parse_country(df, col_to_be_parsed, new_match_column, explode=True, log="CRITICAL"):
    """
    Args:
        df: pandas DataFrame
        col_to_be_parsed: str
        explode: True or False
        log: Can be "CRITICAL" or "INFO"
    Description:
    -- Use to parse country names that can be found in a string of text stored in a df cell. Geolocate the countries using regex and match to the ISO3 code. Return an exploded or unexploded df that contains all the countries ISO3 codes that were found in the text.
        df: pandas DataFrame.
        col_to_be_parsed: Name of column that the country(s) will be extracted from.
        explode: Default True
            True - will create a new row for each country within the list. 
            False - will keep all orginal rows; the matched countries will reman in list form within each cell.
        log: "CRITICAL" or "INFO" will denote whether the 'not found' regexes are displayed as an error.
              CRITICAL - 'not found' regexes will not be displayed.
              INFO - 'not found' regexes will be displayed.
    """
    import pandas as pd
    import country_converter as coco
    import logging
    from typing import Any
    
    # Check that 'explode' param is a bool
    if isinstance(explode, bool):
        None
    else:
        raise Exception('explode param does not have bool value.')

    # Check that the 'log' param is 'CRITICAL' or 'INFO'
    if log == "CRITICAL":
        coco_logger = coco.logging.getLogger()
        coco_logger.setLevel(logging.CRITICAL)
    elif log == "INFO":
        coco_logger = coco.logging.getLogger()
        coco_logger.setLevel(logging.INFO)
    else:
        raise Exception(f"log param cannot equal '{log}'...log must equal 'CRITICAL' or 'INFO'")
    
    # Translator to remove/correct extraneous characters
    replacements = str.maketrans({
        '–': '', 
        ',': '', 
        ';': '', 
        '.': '', 
        '(': '', 
        ')': '', 
        '-': ' '
    })
    
    df[col_to_be_parsed] = df[col_to_be_parsed].str.translate(replacements)
    
    # Add "TempText" to start of text as the first word to not match the coco regex for sorting purposes
    df['col_with_id'] = "TempText " + df[col_to_be_parsed]  
    # Fill newly created column with 'null' values as placeholder
    df[new_match_column] = None

    # Temporary column for parsing
    col_parsed_filled = df['col_with_id'].fillna("N/A")
    
    # country_converter
    cc = coco.CountryConverter()
    
    i = -1
    while i < (len(col_parsed_filled) - 1):
        i += 1
    
        # Split text at every " "...then check the regex to find any countries matching in coco and match using the ISO3 Code.
        # Any word not matching a country is labeled "AAAA" for sorting and final data cleaning
        # mc is the 'new' matching column
        mc = pd.Series(cc.convert(col_parsed_filled[i].split(), src="regex", to="ISO3", not_found='AAAA'))
        
        # Split text at every " " for comparison to coco matched column "mc"
        # og is the original column separated to creat a one for on match when concatenating "mc" and "og"
        og = pd.Series(col_parsed_filled[i].split())
    
        # Combine "mc" and "og" for comparison
        comb = pd.concat([og, mc], axis=1)
    
        # Access the 2nd column (mc) and drop duplicated countries and all words labeled as "AAAA" to leave only a single "AAAA" and countries
        comb_drop_d = comb[1].drop_duplicates()

        # Sort values alphabetically...remove "comb_drop_d[0]" (i.e. "AAAA")...reset index...remove old index column...rename ISO3 Coded column as "new_match_column"
        new_df = pd.DataFrame(comb_drop_d)[1].sort_values().drop(0).reset_index().drop(columns='index').rename(columns={1: new_match_column})
        
        # Turn "new_match_column" into list to insert values into the "df"
        new_df_list = new_df[new_match_column].to_list()

        # Replace empty df["new_match_column"] values with ISO3 Codes from "new_df_list" based on matching index number
        df.at[i, new_match_column] = new_df_list

    # explaode values by default. Do not explode with False and keep macthed country ISO 3 codes in list form wihtin the cell.
    if explode == True:
        return df.explode(new_match_column).drop(columns='col_with_id')
    else:
        return df.drop(columns='col_with_id')
```
___
# ostaGIS.py - > vals_to_df
[Back to top](#ostagis---open-source-threat-analysis-gis)
#### PURPOSE: Convert *list* to pandas DataFrame

```
def vals_to_df(entries):
    """
    Description:
        entries: list of text to be in each row of the DataFrame
    """  
    if isinstance(entries, list):
        None
    else:
        raise Exception('entries param must be a list')
    
    import pandas as pd
    df = {"values": entries}
    df = pd.DataFrame(df)
    return df
```
___
# ostaGIS.py - > wfb_country_scraper
[Back to top](#ostagis---open-source-threat-analysis-gis)
#### PURPOSE: This code is desinged to scrape each CIA World Factbook entry (link) with the matching country using the ISO3 code; this results in coded and non-coded datasets.
*The datasets can be used independently for other mapping purposes.*
#### Python libraries used:
- BeautifulSoup
- Pandas
- Country Converter (coco)
- Logging

\
**See [HOW_TO_SCRAPE_LINKS.md](link) for the best way to prepare for sraping.**
##### Example of HTML file used - NOTE: to run the code as designed, the HTML should be saved as stated above.
[CIA_wfb.html](links)
```
def wfb_country_scrape(saved_html, output_folder, log="CRITICAL"):
    """
    Description:
        Extract links for each country from the CIA World Factbook.
    Params:
        saved_html: path to the saved CIA wfb html file -- see documentation 'https://github.com/samcor33/ostaGIS/'
        output_folder: path to folder for resulting datasets
            Example - 'C:\\Users\\me\\project_folder\\saved_datasets'
        log: 'CRITICAL' or 'INFO' will denote whether the 'not found' regexes are displayed as an error
              CRITICAL - 'not found' regexes will not be displayed
              INFO - 'not found' regexes will be displayed
    """
    from bs4 import BeautifulSoup, NavigableString
    import pandas as pd
    import country_converter as coco
    import logging
    
    # Check that the 'log' param is 'CRITICAL' or 'INFO'
    if log == "CRITICAL":
        coco_logger = coco.logging.getLogger()
        coco_logger.setLevel(logging.CRITICAL)
    elif log == "INFO":
        coco_logger = coco.logging.getLogger()
        coco_logger.setLevel(logging.INFO)
    else:
        raise Exception(f"log param cannot equal '{log}'...log must equal 'CRITICAL' or 'INFO'")
    
    wfb_country_links = [] # Stores each link
    
    # Open the HTML file
    with open(saved_html, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find div elements labeled "pb30" which hold the information for each t_org
    sections = soup.find_all("a", attrs={"href": any})
    
    for a in sections:
        # Replace "file:///C:/" with the CIA url to make the "href" url valid an clickable
        wfb_country_links.append("https://www.cia.gov" + a.get("href"))
    
    #Create DataFrame using pandas
    wfb_df = pd.DataFrame(wfb_country_links)

    #Split link into new df
    wfb_df_coded = wfb_df[0].str.split("/", expand=True)
    #Get country name from split link
    wfb_df_country = wfb_df_coded[5]

    cc = coco.CountryConverter()
    #Compare country with coco and create column with matched country
    country_names = cc.pandas_convert(wfb_df_country, to='short_name')
    wfb_df_coded['country'] = country_names
    
    #Get ISO3 Code with coco based off of the matched country
    iso3_codes = cc.pandas_convert(wfb_df_coded['country'], to='ISO3')
    wfb_df_coded['ISO3_CODE'] = iso3_codes
    
    #Merge split link data with original link df...then drop & rename columns
    wfb_coded = wfb_df.merge(wfb_df_coded, left_index=True, right_index=True).drop(columns=["0_y",	1,	2,	3,	4, 6]).rename(columns={"0_x": "wfb_country_link", 5: "wfb_country_name"})
    
    #Create two separate dfs...one without coded links and one with the coded links
    wfb_code_not_found = wfb_coded[wfb_coded['country'] == "not found"].drop_duplicates().reset_index().drop(columns="index")
    wfb_coded = wfb_coded[wfb_coded['country'] != "not found"].drop_duplicates().reset_index().drop(columns="index")
    
    # Dataset of locations not found thru coco...(i.e., place.drop_duplicates()s, not official countries)
    wfb_code_not_found.to_csv(output_folder + "\\wfb_countries_not_coded.csv")
    
    # Dataset of goelocated World Fact Book links
    wfb_coded.to_csv(output_folder + "\\wfb_countries_coded.csv")

    return(print(f"finished...see {output_folder}"))
```
### Resulting Datasets
[wfb_countries_coded.csv](wfb_countries_coded.csv)
<br>
[wfb_countries_no_code.csv](wfb_countries_no_code.csv)
___
# ostaGIS.py - > wfb_tos_geoscraper
[Back to top](#ostagis---open-source-threat-analysis-gis)
#### PURPOSE: Scrape the [CIA World Factbook - Terrorist Organizations](https://www.cia.gov/the-world-factbook/references/terrorist-organizations/) from a saved .html for known area(s) of operation (AORs); resulting in a Pandas Dataframe.
###### NOTE: use with the `parse_country` function to geolocate the AORs.
#### Python libraries used:
- BeautifulSoup
- Pandas
- Country Converter (coco)

\
**See [HOW_TO_SCRAPE_T_ORGS.md](link) for the best way to prepare for sraping.**
##### Example of HTML file used - NOTE: to run the code as designed, the HTML should be saved as stated above.
[CIA_t_o.html](links)
```
def wfb_tos_geoscraper(saved_html):
    """
    saved_html: path to the saved CIA wfb html file -- see documentation 'https://github.com/samcor33/ostaGIS/'
    
    Description: scrape CIA desingated bad actors for known area(s) of operation (AORs)
    Result: a Pandas Dataframe to be used for further processing
    ___________________________________
    |    index    | area of operation |
    |---------------------------------|
    | torg (name) |  AOR description  |
    
    Designed for: use with the `parse_country` function to geolocate the AORs
    """
    from bs4 import BeautifulSoup, NavigableString
    import pandas as pd
    import country_converter as coco
    
    wfb_tos = {}
    
    # Open the HTML file
    with open(saved_html, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find div elements labeled "pb30" which hold the information for each t_org
    sections = soup.find_all('div', attrs={"class":"pb30"})
    
    # Extract information (example: all paragraph tags)
    for s in sections:    
        titles = s.find_all("h2") # Title(name) of t_org
        paragraphs = s.find_all('p') # p elements with t_org information
    
        # Get each h2 element
        for title in titles:
    
            # Get information in each p element
            for p in paragraphs:        
                
                # Find elements that contain "areas of operation" and split to extract the text to "wfb_tos" dict
                if 'areas of operation' in p.text:
                    cat_l = "area of operation"
                    cat_t = p.text.split('areas of operation – ')[1]
                
                    if title.text not in wfb_tos:
                        wfb_tos[title.text] = {}
                    wfb_tos[title.text][cat_l] = cat_t
                    break
    
                # Find elements that contain "area(s) of operation" and split to extract the text to "wfb_tos" dict
                # This is due to variation in labeling from the CIA website
                if 'area(s) of operation' in p.text:
                    cat_l = "area of operation"
                    cat_t = p.text.split('area(s) of operation – ')[1]
                
                    if title.text not in wfb_tos:
                        wfb_tos[title.text] = {}
                    wfb_tos[title.text][cat_l] = cat_t
                    break
    
    # Put "wfb_tos" into pandas dataframe
    return pd.DataFrame(wfb_tos).T.reset_index()
```
**Example when used in conjuction with `parse_country`:**
```
ostaGIS.parse_country(
    df=wfb_tos_geoscraper(saved_html = r"C:/Users/me/my_project/CIA_t_o.html"), 
    col_to_be_parsed="area of operation", 
    new_match_column="country_aor"
).to_csv("C:/Users/me/my_project/datasets/wfb_t_orgs_geolocated.csv")
```

___
# ostaGIS.py - > geomatch_and_multiply
[Back to top](#ostagis---open-source-threat-analysis-gis)
#### PURPOSE: In ArcGIS, use to match an ISO3 country coded polygon feature class, with an ISO3 coded table to geolocate table records to the associated polygon. Then, Split overlapping records within one polygon, to individual feature classes.
###### NOTE: This function is designed for use with the "wfb_t_orgs_geolocated.csv" dataset but may work with similar styled datasets.
#### Python libraries used:
- ArcPy

```
def geomatch_and_multiply(
    countries_fc, 
    iso_table,
    name_col,
    out_gdb = "country_mult.gdb", 
    countries_join_field = "ISO_CC",
    table_join_field = "country_aor",
    feature_dataset_name = "individual_fc"
):
    
    """
    Description: 
        1) Used to match an ISO3 country coded polygon feature class, with an ISO3 coded table to geolocate table records to the associated polygon.
        2) Split overlapping records within one polygon, to individual feature classes.
        NOTE: Designed for geolocating terrorist organizations from the CIA World Factbook.
    ---
    countries_fc (path):
        path to feature class with country polygons
        (preferred -- coded using the ISO3 standard)
    
    iso_table (path): 
        path to table that will be matched and replicated 
        (preferred -- coded using the ISO3 standard)
        
    name_col (str):
        column of indexed values i.e., 'Name'
        
    out_gdb (str): 
        new gdb name to store the new feature class -- 'name.gdb'
        (default -- 'country_mult.gdb')
        
    countries_join_field (str):
        column name for country fc joining (prefered -- ISO3 code column)
        (default -- "ISO_CC" -- designed for provided country fc)
        
    table_join_field (str):
        column name on table for country fc joining (prefered -- ISO3 code column)
        (default -- "country_aor" -- designed for 'wfb_t_orgs_geolocated' table -- can be used for other datasets but, must input correct column name that matches substituted dataset)
        
    feature_dataset_name (str):
        name of feature dataset that will contain the individually mapped feature classes
        (default -- "individual_fc")
    """
    
    import arcpy
    # Get CURRENT project
    aprx = arcpy.mp.ArcGISProject("CURRENT")
    
    #--------------CHECK FOR GDB-----------------------------
    # Store original gdb file path
    og_default_gdb = aprx.defaultGeodatabase
    
    tf = []
    for d in aprx.databases:
        # If the new gdb is not present...add false to the list
        if not d['databasePath'].endswith(out_gdb):
            tf.append(False)
        else:
            tf.append(True)
    
    if any(x == True for x in tf):
        # Set 'out_gdb' as default to work with
        aprx.defaultGeodatabase = f"{aprx.homeFolder}\\{out_gdb}"
    else:
        # Create new gdb to match the 'out_gdb' parameter
        arcpy.management.CreateFileGDB(aprx.homeFolder, out_gdb)
        # Set newly created gdb as default to work with and add to 'databases' list 
        aprx.defaultGeodatabase = f"{aprx.homeFolder}\\{out_gdb}"
        print(out_gdb + " created!")
    
    #_______________________PART 1___________________________________________________
    # Credit for part 1 goes to AI which helped me design the actual operation of the code. I only adjusted certain portions to integrate it with the whole function.
    mult_fc = f"{aprx.defaultGeodatabase}\\countries_multiplied",

    # Fields to copy from countries (geometry + attributes)
    countries_fields = [f.name for f in arcpy.ListFields(countries_fc) if f.type != 'Geometry']
    
    # Fields to copy from table (attributes only, no geometry)
    table_fields = [f.name for f in arcpy.ListFields(iso_table) if f.type != 'Geometry']
    
    # Full list of output fields (all from countries + all from table)
    output_fields = countries_fields + table_fields + ['SHAPE@']
    
    # Create output feature class, copying schema from countries_fc
    arcpy.CreateFeatureclass_management(
        out_path=aprx.defaultGeodatabase,
        out_name="countries_multiplied",
        geometry_type=arcpy.Describe(countries_fc).shapeType,
        template=countries_fc,
        spatial_reference=arcpy.Describe(countries_fc).spatialReference
    )
    
    # Add fields from the table to mult_fc (if they don’t already exist)
    existing_fields = [f.name for f in arcpy.ListFields("countries_multiplied")]
    for fld in table_fields:
        if fld not in existing_fields:
            field_obj = arcpy.ListFields(iso_table, fld)[0]
            arcpy.AddField_management("countries_multiplied", fld, field_obj.type, 
                                      field_obj.precision, field_obj.scale, field_obj.length)
    
    # Build a dict mapping ISO code -> list of table records
    table_dict = {}
    with arcpy.da.SearchCursor(iso_table, table_fields + [table_join_field]) as cursor:
        for row in cursor:
            # last field is the join key value
            join_val = row[-1]
            if join_val is None:
                continue
            rec_attrs = row[:-1]  # all other fields
            table_dict.setdefault(join_val, []).append(rec_attrs)
    
    # Now open insert cursor to mult_fc
    with arcpy.da.SearchCursor(countries_fc, countries_fields + ['SHAPE@']) as country_cursor, \
         arcpy.da.InsertCursor("countries_multiplied", output_fields) as insert_cursor:
        for country_row in country_cursor:
            country_code = country_row[countries_fields.index(countries_join_field)]
            if country_code in table_dict:
                for tbl_attrs in table_dict[country_code]:
                    # Combine country and table attributes plus geometry
                    out_row = list(country_row[:-1]) + list(tbl_attrs) + [country_row[-1]]
                    insert_cursor.insertRow(out_row)
                    
    print("Many-to-many replication completed!")
    
    #_______________________PART 2___________________________________________________
    # Stats table to be created - to get unique name count (i.e, index--not record count)
    stats_table = f"{aprx.defaultGeodatabase}\\stats_table"
    
    # Run stats to get count and name of each t_org
    arcpy.analysis.Statistics(iso_table, stats_table, [[name_col, "COUNT"]], case_field=name_col)
    
    # Feature layer "countries_multiplied" must be in map
    mult_lyr = aprx.activeMap.listLayers('countries_multiplied')
    # Get the unique values of each name/index from table and put in list
    names_array = arcpy.da.TableToNumPyArray(stats_table, [name_col])
    
    # Create Feature Dataset named "individual_fc" as a container to store the individual Feature Classes
    arcpy.management.CreateFeatureDataset(
        out_dataset_path=out_gdb,
        out_name=feature_dataset_name
    )
    
    # Run a loop for the entirety of the list
    i = -1
    while i < len(names_array) - 1:
        i = i + 1
        
        # Clean strings to remove forbidden characters
        fc_name = names_array[i][0].replace(" ", "_").replace("'", "_").replace("(", "").replace(")", "").replace("-", "_").replace("/", "_").replace("’", "_").replace("–", "_").replace(",", "")
        
        # Export Feature Class based on matching #s in "Field1" (number associated with the unique value)
        arcpy.conversion.ExportFeatures(
            in_features = "countries_multiplied",
            out_features = f"{out_gdb}\\{feature_dataset_name}\\{fc_name}",
            where_clause = f"Field1 = {i}"
        )
        # Name of newley created layer
        new_lyr = aprx.activeMap.listLayers(fc_name)
        
        # Delete newly created layer to save space in the "Contents" pane
        arcpy.Delete_management(new_lyr)
    
    # ---------------------RETURN GDB TO ORIGINAL DEFAULT------------------------------
    # Set default back to original gdb file path
    aprx.defaultGeodatabase = og_default_gdb

    print('Individual Mapping Complete')
```
**Example when used in conjuction with `wfb_t_orgs_geolocated.csv`:**
```
ostaGIS.geomatch_and_multiply(
    countries_fc = "World_Countries_one_poly_per_c",
    iso_table = "wfb_t_orgs_geolocated",
    name_col="index"
)
```
___
# ostaGIS.py - > apply_style_to_gp_lyr
[Back to top](#ostagis---open-source-threat-analysis-gis)
#### PURPOSE: In ArcGIS, use to add a new style to the symbology of every layer within a specified group layer.
#### Python libraries used:
- ArcPy


```
def apply_style_to_gp_lyr(gp_lyr_name, style_name):
    """
    Description:
        Add a new style to the symbology of every layer within a specified group layer.
    """
    import arcpy
    aprx = arcpy.mp.ArcGISProject("CURRENT")
    
    # get the current map
    m = aprx.activeMap
    
    # individual org layers must be grouped
    # find all layers in map
    lyrs = m.listLayers()
    
    # find the grouped layers in group
    for gp_lyr in lyrs:
        if gp_lyr.name == gp_lyr_name:
            gpd_lyrs = gp_lyr.listLayers()
            
            # run loop counting the total of layers in the group
            i = -1
            while i < len(gpd_lyrs) -1 :
                i = i + 1
                
                # get the symbology for each layer
                symbology = gpd_lyrs[i].symbology
    
                if hasattr(symbology, "renderer"):
                    symbology.updateRenderer("SimpleRenderer")
                # update symbology to desired style
                    symbology.renderer.symbol.applySymbolFromGallery(style_name)
                    gpd_lyrs[i].symbology = symbology  # Apply changes
        else:
            raise Exception("No Group Layer Found! \n Either the group layer name entered was mispelled or does not exist. \n NOTE: To apply a style to multiple feature layers, the layers must be within a group layer.")

    print("Style applied to group")
```
