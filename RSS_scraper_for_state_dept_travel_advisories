import feedparser
import pandas as pd
import country_converter as coco

feed = feedparser.parse('https://travel.state.gov/_res/rss/TAsTWs.xml/')

country_threat_info = {}
if feed.status == 200:    
    for entry in feed.entries:
        #print(entry)
        for tag in entry.tags:
                
            #Fuction to get the country name directly from the travel advisory url since the threat levels can be non-standard to parse and match with COCO
            def parse_country(url):
                pc = url.split("/")
                # V - This is bad code but it works - V
                parsed_country = pc[len(pc) - 1].removesuffix("-travel-advisory.html").replace('advisory', "").replace('travel', "").replace("-", " ").replace(".html", "").title()
                #Specifically handles the "Azerbajian" naming error from the State Dept...because they are shitty and suck major cocks
                if parsed_country == "Azerbajian":
                    parsed_country = 'Azerbaijan'
                    return parsed_country
                else:
                    return parsed_country
            
            #This statement specifically handles the labeling issue with the 'Israel, the West Bank and Gaza' Travel Advisory...because the State Dept is shitty and suck major cocks
            if entry.title == 'See Individual Summaries -':
                country_threat_info['IL'] = {
                    'label': 'Israel, the West Bank and Gaza - See Individual Summaries',
                    'link': entry.link,
                    'published': entry.published,
                    'summary': entry.summary,
                    'summary_cont': None,
                    'DoS_country_name': parse_country(entry.link)
                }
            #This statement is the standard parsing code
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

#Check if any Summary text is over the 32000 limit for exporting to csv
for s in twa_df['summary']:
    
    #Split the summary at the midpoint using chunk_at_midpoint
    #This is not dynamic but it's likely no summary will be over 64000 characters...Mexico is the only one over 32000 by a large margin
    def chunk_at_midpoint(text):
        words = text.split()
        midpoint = int(len(words) / 2)
        return [' '.join(words[i:i+midpoint]) for i in range(0, len(words), midpoint)]
        
    if len(s) > 32000:
        #Get indexing information to chnage text using the '.loc' method 
        fltr = twa_df[twa_df['summary'] == s]
        row = fltr.index[0]
        s_clmn = twa_df.columns[twa_df.columns == "summary"][0]
        sc_clmn = twa_df.columns[twa_df.columns == "summary_cont"][0]
        
        chunk = chunk_at_midpoint(s)

        #save text to appropriate columns
        twa_df.loc[row, s_clmn] = chunk[0]
        twa_df.loc[row, sc_clmn] = chunk[1]

#Split country/threat level and keep threat level only
cnt = twa_df['label'].str.split(" - ", n=1, expand=True).rename(columns={1: "threat_level"}).drop(columns=0)
twa_df= cnt.join(twa_df)

#Match countries thru COCO to assign proper **3 Digit ISO Code**...Not the random State Dept bullshit codest...because they are shitty and suck major cocks
cc = coco.CountryConverter()
countries = twa_df['DoS_country_name']

country_names = cc.pandas_convert(countries, to='name_short')
twa_df['country'] = country_names
twa_df = twa_df.explode('country')

country_iso3_codes = cc.pandas_convert(twa_df['country'], to='ISO3')
twa_df['ISO3_CODE'] = country_iso3_codes
twa_df = twa_df.explode('ISO3_CODE')

#remove advisories for locations without an ISO3 Code then sort alphabetically
twa_df = twa_df[twa_df['country'] != 'not found']
twa_df = twa_df.sort_values('country')

#Put Mexico at the top for ArcGIS Pro importing
#The longest text must be at the top so when it's imported, it automatically makes the character length 32767.
#You may need to adjust the country below if Mexico's summary falls below 32767 and another country's summary exceeds 32767
m = twa_df[twa_df['ISO3_CODE'] == 'MEX']
m_df = pd.DataFrame(m)
twa_df = twa_df.drop(m.index[0])
twa_df = pd.concat([m_df, twa_df])
twa_df = twa_df.reset_index().drop(columns='index')

#rearrange columns for finished dataset
twa_df_final = twa_df
twa_df_final = twa_df_final[['country', 'threat_level', 'published', 'ISO3_CODE', 'link', 'summary', 'summary_cont', 'label', 'DoS_country_name', 'DoS_gen2alpha']]
twa_df_final.to_excel(f'travel_advisories.xlsx', sheet_name='travel_advisories')
