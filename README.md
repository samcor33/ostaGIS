# ostaGIS - Open Source Threat Analysis GIS
### Methods for collecting OSINT to conduct threat analysis through GIS.

##### [Mapping CIA World Factbook links](CIA_world_fact_book_scraping/README.md)
##### [Mapping CIA World Factbook Terrorist Organizations](mapping_t_orgs/README.md)
> ##### [parse_country.py](parse_country/README.md)

##### [Parsing State Dept Travel Advisory XML Feed]()

___
# ostaGIS.py - > state_dept_twas
#### PURPOSE: Parse the [State Department travel advisory XML feed](https://travel.state.gov/_res/rss/TAsTWs.xml/) to geolocate countries into ISO3 format.
###### NOTE: This code and resulting dataset is designed for use with ArcGIS Pro to map each country's Travel Warning/Advisory using the ISO3 code.

*The dataset can be used independently for other mapping purposes.*
##### Python libraries used:
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
# [ostaGIS.py - > parse_country]()

#### PURPOSE: Parse and geocode countries mentioned within a text to then geolocate that text using GIS software.

##### Python Librarys Used:
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
# [ostaGIS.py - > vals_to_df](ostaGIS.py)

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
# [ostaGIS.py - > wfb_country_scraper](ostaGIS.py)

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
[CIA_wfb.html](CIA_wfb.html)
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
