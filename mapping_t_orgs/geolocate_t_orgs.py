from bs4 import BeautifulSoup, NavigableString
import pandas as pd
import country_converter as coco
from parse_country import parse_country

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

ex_tos_df = parse_country(tos_df, "area of operation", "country_aor")
ex_tos_df.to_csv("C:\\Users\\samco\\OneDrive\\Desktop\\OSINT\\Complete_datasets\\wfb_t_orgs_geolocated.csv")
