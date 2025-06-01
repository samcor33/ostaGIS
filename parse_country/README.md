# [parse_country.py](parse_country.py)

#### PURPOSE: Parse and geocode countries mentioned within a text to then geolocate that text using GIS software.

##### Librarys Used:
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

#### See [notebook](parse_country_description_examples.ipynb) for examples

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

## [vals_to_df.py](vals_to_df.py)

#### PURPOSE: Convert *list* to pandas DataFrame

```
def vals_to_df(entries):
    """
    Description:
        df_name: name for new DataFrame
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
