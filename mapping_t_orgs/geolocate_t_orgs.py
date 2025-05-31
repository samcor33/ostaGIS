from bs4 import BeautifulSoup, NavigableString
import pandas as pd
import country_converter as coco

# Must save the html as a file
saved_html = r"C:/Users/samco/OneDrive/Desktop/OSINT/saved_web_pages/CIA_t_o.html"
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
tos_df = pd.DataFrame(wfb_tos).T.reset_index()

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

tos_df['area of operation'] = tos_df['area of operation'].str.translate(replacements)
# Add "AOR" to start of text as identifier and first word to not match the coco regex for sorting purposes
tos_df['area of operation'] = 'AOR ' + tos_df['area of operation'] 
tos_df['country_aor'] = None
# Add column for link to CIA WFB t_org page
tos_df['wfb_t_org_link'] = "https://www.cia.gov/the-world-factbook/references/terrorist-organizations/"

aor_full = tos_df['area of operation'].fillna("N/A")

# country_converter
cc = coco.CountryConverter()

x = []
i = -1
while i < (len(aor_full) - 1):
    i += 1

    # Split text at every " "...then check the regex to find any countries matching in coco and use the ISO3 Code.
    # Any words not matching a country is labeled "AAAA" for sorting and final data cleaning
    mc = pd.Series(cc.convert(aor_full[i].split(), src="regex", to="ISO3", not_found='AAAA'))
    
    # Split text at every " " for comparison to coco matched column "mc"
    og = pd.Series(aor_full[i].split())

    # Combine "mc" and "og" for comparison
    comb = pd.concat([og, mc], axis=1)

    # Access the 2nd column (mc) and drop duplicated countries and all words labeled as "AAAA" to leave only a single "AAAA" and countries
    aor = comb[1].drop_duplicates()

    # Sort values alphabetically...remove "aor[0]" (i.e. "AAAA")...reset index...remove old index column...rename ISO3 Coded column as "country_aor"
    caor = pd.DataFrame(aor)[1].sort_values().drop(0).reset_index().drop(columns='index').rename(columns={1: "country_aor"})
    
    # Turn "country_aor" into list to insert values into the "tos_df"
    caor_l = caor['country_aor'].to_list()

    # Replace empty tos_df["country_aor"] values with ISO3 Codes from "caor_l" based on matching index number
    tos_df.at[i, "country_aor"] = caor_l

# Explode multiple countires within the tos_df["country_aor"] column so every ISO3 Code is categprized solely to a t_org
tos_df.explode('country_aor').to_csv("C:\\Users\\samco\\OneDrive\\Desktop\\OSINT\\Complete_datasets\\wfb_t_orgs_geolocated.csv")

# Ignore "...not found in regex"...that is normal for all words not matching a coco regex match
