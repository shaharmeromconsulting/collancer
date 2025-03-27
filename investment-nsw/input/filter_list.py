import pandas as pd
import numpy as np
from time import sleep
from playwright.sync_api import sync_playwright
pwright = sync_playwright().start()
browser = pwright.chromium.launch(headless=False)



#-------------------------------------------------------------------------------------
# Table extractor
#-------------------------------------------------------------------------------------

def table_extractor(_page):
    table = _page.query_selector("table")
    head = table.query_selector('thead')
    cols = []
    for h in head.query_selector_all('th'):
        cols = cols+[h.text_content()]
    master_table = {}
    rows = table.query_selector('tbody').query_selector_all('tr')
    for row in rows:
        cells = row.query_selector_all('td')
        row_data ={}
        for c in range(0,len(cols)):
            if c==0: row_head = row.query_selector('th').text_content()
            else: row_data[cols[c]]=cells[c-1].text_content()
        master_table[row_head] = row_data
    return master_table

def cell_cleaner(x):
    if x == '-':
        return 0
    x = x.replace('$','')
    x = x.replace(',','')
    y = x.find('b')
    if y>0:
        x = float(x.replace('b',''))*1000000000
        return x
    y = x.find('m')
    if y>0:
        x = float(x.replace('m',''))*1000000
        return x
    y = x.find('k')
    if y>0:
        x = float(x.replace('k',''))*1000
        return x
    else: return x

temp_table = pd.DataFrame.from_dict(results_dict).transpose().reset_index()
temp_table['2000 '][13]

def table_cleaner(_table,_definitions,col_name='region'):
    new_names = {}
    new_names['index'] = col_name
    for c in _table.columns[1:]:
        new_names[c] = c.strip()
    _table = _table.rename(columns = new_names)
    for c in _table.columns[1:]:
        _table[c] = _table[c].apply(cell_cleaner)
    _table['Background'] = _definitions['Background']
    _table['Degree'] = _definitions['Degree']
    _table['Gender'] = _definitions['Gender']
    _table['Founder Experience'] = _definitions['Founder Experience']
    _table['Round'] = _definitions['Round']
    if col_name == 'region':_table['Industries'] = _definitions['Industries']
    if col_name == 'Industries':_table['region'] = _definitions['region']
    return _table

#-------------------------------------------------------------------------------------
# Row display for cross region comparisons
#-------------------------------------------------------------------------------------
# For cross region comparisons
location_rows = r"&rows=australia~canada~~victoria_1~~~new_south_wales~~%27~~ontario_7~~~united_states~~pennsylvania~texas~~state_new_york_usa~~~new_zealand~~israel~~united_kingdom~singapore" # row seperator ~
end_url = r"&sort=-2024&startYear=2000&type=amount"

# For cross industry comparisons
filter_locs = {"region":["new_south_wales","victoria_1"]} #filter seperate: ~_~
for loc in filter_locs['region']:
    location_filter = f"slug_locations/anyof_~{loc}~/"

#-------------------------------------------------------------------------------------
# Founder filters
#-------------------------------------------------------------------------------------
i=0
filter_list_founder={}
founder_technical = [{'All':''},{"Technical background":"Technical_Biology%20%26%20Earth%20Science_Medical_Chemistry_Physics_Mathematics_IT"}]
founder_degree = [{'All':''},{"PhD founder":"PhD"}]
gender_dict = [{'All':''},{"Women":"female"}]
founder_serial = [{'All':''},{"Serial":"yes"}]

for t in founder_technical:
    for tkey,tval in t.items():
        if tkey == "All": f_background_filter = ''
        else: f_background_filter = f"founders_backgrounds/anyof_{tval}/"
        for d in founder_degree:
            for dkey,dval in d.items():
                if dkey == "All": f_expertise_filter = ''
                else: f_expertise_filter = f"founders_degrees/anyof_{dval}/"
                for g in gender_dict:
                    for gkey,gval in g.items():
                        if gkey == "All": f_gender_filter = ''
                        else: f_gender_filter = f"founders_gender/anyof_~{gval}/"
                        for s in founder_serial:
                            for skey,sval in s.items():
                                if skey == "All": f_serial_filter = ''
                                else: f_serial_filter = f"founders_is_serial_founder/anyof_~{sval}/"
                                filter_list_founder[i] = {
                                    'Background':tkey,
                                    'Degree':dkey,
                                    'Gender':gkey,
                                    'Founder Experience':skey,
                                    'Round':'All',
                                    'Industries':'All',
                                    'filter':f_background_filter+f_expertise_filter+f_gender_filter+f_serial_filter
                                }
                                i+=1


for pop in [3,5,6,7,9,10,11,13,14,15]:
    filter_list_founder.pop(pop)

for i in range(0,20):
    try: 
        print(i,filter_list_founder[i])
        base_url_location = f"https://app.dealroom.co/curated-heatmaps/funding/location/f/growth_stages/not_mature/rounds/not_GRANT_SPAC%20PRIVATE%20PLACEMENT/{filter_list_founder[i]['filter']}tags/not_outside%20tech?endYear=2024&interval=yearly"
        filter_list_founder[i]['url']=base_url_location+location_rows+end_url
    except: pass

#page = browser.new_page()
t_num =0
ready = input('ready_to_go:')
tables_list = []
for metric in ['rounds','amount']:
    for i in filter_list_founder:
        page.goto(filter_list_founder[i]['url'].replace('&type=amount','&type='+metric))
        sleep(10)
        results_dict = table_extractor(page)
        temp_table = pd.DataFrame.from_dict(results_dict).transpose().reset_index()
        temp_table = table_cleaner(temp_table,_definitions=filter_list_founder[i])
        temp_table['metric']=metric
        tables_list = tables_list + [temp_table]
        t_num+=1
        sleep(np.random.randint(3,9))

#-------------------------------------------------------------------------------------
# Round filters
#-------------------------------------------------------------------------------------
i=0
filter_list_round = {}
round_list = {"round":[
    {"Early":"SEED_PRE-SEED_SEED%2B_SEED%20EXTENSION_MICRO-SEED"}
    ,{"SERIES A":"SERIES%20A_SERIES%20A%20EXTENSION"}
    ,{"SERIES B":"SERIES%20B_SERIES%20B%20EXTENSION"}
    ,{"SERIES C":"SERIES%20C_SERIES%20C%20EXTENSION"}
    ,{"SERIES D+":"SERIES%20D_SERIES%20D%20EXTENSION_SERIES%20E_SERIES%20E%20EXTENSION_SERIES%20F_SERIES%20F%20EXTENSION"}
    ,{"NOT SET":"NOT%20SET"}
    ]}
for round in round_list['round']:
    for key,val in round.items():
        print(key)
        if key == "All": round_filter = ''
        else: round_filter = f"standardised_round_label/anyof_{val}/"
        filter_list_round[i] = {
            'Background':'All',
            'Degree':'All',
            'Gender':'All',
            'Founder Experience':'All',
            'Round':key,
            'Industries':'All',
            'filter':round_filter
        }
        print(i,filter_list_round[i])
        base_url_location = f"https://app.dealroom.co/curated-heatmaps/funding/location/f/growth_stages/not_mature/rounds/not_GRANT_SPAC%20PRIVATE%20PLACEMENT/{filter_list_round[i]['filter']}tags/not_outside%20tech?endYear=2024&interval=yearly"
        filter_list_round[i]['url']=base_url_location+location_rows+end_url
        i+=1


for metric in ['rounds','amount']:
    for i in filter_list_round:
        page.goto(filter_list_round[i]['url'].replace('&type=amount','&type='+metric))
        sleep(10)
        results_dict = table_extractor(page)
        temp_table = pd.DataFrame.from_dict(results_dict).transpose().reset_index()
        temp_table = table_cleaner(temp_table,_definitions=filter_list_round[i])
        temp_table['metric']=metric
        tables_list = tables_list + [temp_table]
        t_num+=1
        sleep(np.random.randint(3,9))

pd.concat(tables_list,axis=0).to_csv(r'C:\Users\merom\Documents\GitHub\collancer\investment-nsw\output\master_data.csv')
#-------------------------------------------------------------------------------------
# Industry filters
#-------------------------------------------------------------------------------------



filters = location_filter+founder_filter

base_url_industry = f"https://app.dealroom.co/curated-heatmaps/funding/sub_industry/f/growth_stages/not_mature/rounds/not_GRANT_SPAC%20PRIVATE%20PLACEMENT/{filters}tags/not_outside%20tech?endYear=2024&interval=yearly"
end_url = r"&sort=-2024&startYear=2000&type=amount"


industry_rows = r"&rows=gaming~enterprise%2520software~health~travel~legal~security~fintech~wellness%2520beauty~music~real%2520estate~fashion~sports~food~media~dating~telecom~education~energy~kids~hosting~home%2520living~event%2520tech~robotics~jobs%2520recruitment~transportation~semiconductors~marketing"
sub_industry_rows = r"&rows=accessories~accommodation~adtech~agritech~apparel~autonomous%2520%2526%2520sensor%2520tech~banking~betting%2520%2526%2520gambling~biotechnology~board%2520games~booking%2520%2526%2520search~business%2520travel~clean%2520energy~cloud%2520%2526%2520infrastructure~console%2520%2526%2520pc%2520gaming~construction~content%2520production~crm%2520%2526%2520sales~crypto%2520and%2520defi~data%2520protection~device%2520security%2520%2526%2520antivirus~ecommerce%2520solutions~energy%2520efficiency~energy%2520providers~energy%2520storage~esports~financial%2520management%2520solutions~fitness~food%2520logistics%2520%2526%2520delivery~footwear~health%2520platform~identity%2520%2526%2520access~in-store%2520retail%2520%2526%2520restaurant%2520tech~innovative%2520food~insurance~intellectual%2520property~kitchen%2520%2526%2520cooking%2520tech~learning%2520tools%2520and%2520resources~legal%2520documents%2520management~legal%2520information~legal%2520matter%2520management~logistics%2520%2526%2520delivery~luxury~maintenance~marketing%2520analytics~medical%2520devices~mobile%2520gaming~mobility~mortgages%2520%2526%2520lending~navigation%2520%2526%2520mapping~oil%2520%2526%2520gas~online%2520travel%2520agency~payments~pharmaceutical~public%2520safety~publishing~real%2520estate%2520services~real%2520estate%2520software~regtech~regtech%2520%2526%2520compliance~search%252C%2520buy%2520%2526%2520rent~self-service%2520and%2520lawyer%2520marketplace~social%2520media~sport%2520league%2520%2526%2520club~sport%2520media~sport%2520platform%2520%2526%2520application~sport%2520supplements~sporting%2520equipment~streaming~travel%2520analytics%2520%2526%2520software~vehicle%2520production~waste%2520solution~water~wealth%2520management~workspaces"

x = base_url_industry+sub_industry_rows+end_url

#required_columns

# 
#
#
#
#
# VC_investment
# company_count

