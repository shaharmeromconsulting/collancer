import pandas as pd
import numpy as np
from time import sleep
from playwright.sync_api import sync_playwright
pwright = sync_playwright().start()
browser = pwright.chromium.launch(headless=False)

#ENVIRONMENT
#   C:\Users\merom\Documents\GitHub\collancer\collancer_base\Scripts\Activate.ps1

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
    y = x.find('t')
    if y>0:
        x = float(x.replace('t',''))*1000000000000
        return x
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
    _table['Investor'] = _definitions['Investor']
    if col_name == 'region':_table['Industries'] = _definitions['Industries']
    if col_name == 'Industries':_table['region'] = _definitions['region']
    return _table


def table_cleaner_simple(_table,exclusions=[]):
    new_names = {}
    for c in _table.columns[1:]:
        new_names[c] = c.strip()
    _table = _table.rename(columns = new_names)
    for c in _table.columns[1:]:
        if c not in _table.columns[exclusions]:_table[c] = _table[c].apply(cell_cleaner)
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
                                    'Investor':'All',
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

page = browser.new_page()
page.goto(filter_list_founder[0]['url'])

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
            'Investor':'All',
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

        sleep(np.random.randint(3,9))

pd.concat(tables_list,axis=0).to_csv(r'C:\Users\merom\Documents\GitHub\collancer\investment-nsw\output\master_data.csv')
#-------------------------------------------------------------------------------------
# Industry filters
#-------------------------------------------------------------------------------------
industry_rows = r"&rows=enterprise%2520software~wellness%2520beauty~music~dating~telecom~kids~hosting~home%2520living~event%2520tech~robotics~jobs%2520recruitment~semiconductors"
sub_industry_rows = r"&rows=accessories~accommodation~adtech~agritech~apparel~autonomous%2520%2526%2520sensor%2520tech~banking~betting%2520%2526%2520gambling~biotechnology~board%2520games~booking%2520%2526%2520search~business%2520travel~clean%2520energy~cloud%2520%2526%2520infrastructure~console%2520%2526%2520pc%2520gaming~construction~content%2520production~crm%2520%2526%2520sales~crypto%2520and%2520defi~data%2520protection~device%2520security%2520%2526%2520antivirus~ecommerce%2520solutions~energy%2520efficiency~energy%2520providers~energy%2520storage~esports~financial%2520management%2520solutions~fitness~food%2520logistics%2520%2526%2520delivery~footwear~health%2520platform~identity%2520%2526%2520access~in-store%2520retail%2520%2526%2520restaurant%2520tech~innovative%2520food~insurance~intellectual%2520property~kitchen%2520%2526%2520cooking%2520tech~learning%2520tools%2520and%2520resources~legal%2520documents%2520management~legal%2520information~legal%2520matter%2520management~logistics%2520%2526%2520delivery~luxury~maintenance~marketing%2520analytics~medical%2520devices~mobile%2520gaming~mobility~mortgages%2520%2526%2520lending~navigation%2520%2526%2520mapping~oil%2520%2526%2520gas~online%2520travel%2520agency~payments~pharmaceutical~public%2520safety~publishing~real%2520estate%2520services~real%2520estate%2520software~regtech~regtech%2520%2526%2520compliance~search%252C%2520buy%2520%2526%2520rent~self-service%2520and%2520lawyer%2520marketplace~social%2520media~sport%2520league%2520%2526%2520club~sport%2520media~sport%2520platform%2520%2526%2520application~sport%2520supplements~sporting%2520equipment~streaming~travel%2520analytics%2520%2526%2520software~vehicle%2520production~waste%2520solution~water~wealth%2520management~workspaces"
location_filters = {
    'All':'',
    'Australia':'australia',
    'Canada':'canada',
    'Victoria':'victoria_1',
    'New South Wales':'new_south_wales',
    'Ontario':'ontario_7',
    'United States':'united_states',
    'Pennsylvania':'pennsylvania',
    'Texas':'texas',
    'New York':'state_new_york_usa',
    'New Zealand':'new_zealand',
    'Israel':'israel',
    'United Kingdom':'united_kingdom',
    'Singapore':'singapore'
    }

investor_locations = {'All':''
    ,'Australia':'Australia'
    ,'United States':'United%20States'
    ,'Canada': 'Canada'
    ,'Israel':'Israel'
    ,'Singapore':'Singapore'
    ,'New Zealand':'New%20Zealand'
    ,'United Kingdom':'United%20Kingdom'}
    
i=0
filter_list_industry={}
for rkey,rval in location_filters.items():
    if rkey == "All": f_region_filter = ''
    else: f_region_filter = f"slug_locations/anyof_~{rval}~/"
    for fukey,fuval in investor_locations.items():
        if fukey == "All": f_funds_filter = ''
        else: f_funds_filter = f"investors_locations/anyof_{fuval}/"
        filter_list_industry[i] = {
            'Background':'All',
            'Degree':'All',
            'Gender':'All',
            'Founder Experience':'All',
            'Round':'All',
            'region':rkey,
            'Investor':fukey,
            'filter':f_region_filter+f_funds_filter
        }
        base_url_industry = f"https://app.dealroom.co/curated-heatmaps/funding/sub_industry/f/growth_stages/not_mature/rounds/not_GRANT_SPAC%20PRIVATE%20PLACEMENT/{filter_list_industry[i]['filter']}tags/not_outside%20tech?endYear=2024&interval=yearly"
        base_url_missing_industry =  f"https://app.dealroom.co/curated-heatmaps/funding/industry/f/growth_stages/not_mature/rounds/not_GRANT_SPAC%20PRIVATE%20PLACEMENT/{filter_list_industry[i]['filter']}tags/not_outside%20tech?endYear=2024&interval=yearly"
        filter_list_industry[i]['url']=base_url_industry+sub_industry_rows+end_url
        filter_list_industry[i]['url_missing'] = base_url_missing_industry+industry_rows+end_url
        if ((rkey == 'New South Wales')|(rkey == 'All'))&(fukey == 'All'):
            i+=1
            filter_list_industry[i] = {
            'Background':'All',
            'Degree':'All',
            'Gender':'All',
            'Founder Experience':'All',
            'Round':'Early',
            'region':rkey,
            'Investor':fukey,
            'filter':f_region_filter+"standardised_round_label/anyof_SEED_PRE-SEED_SEED%2B_SEED%20EXTENSION_MICRO-SEED/"
            }
            base_url_industry = f"https://app.dealroom.co/curated-heatmaps/funding/sub_industry/f/growth_stages/not_mature/rounds/not_GRANT_SPAC%20PRIVATE%20PLACEMENT/{filter_list_industry[i]['filter']}tags/not_outside%20tech?endYear=2024&interval=yearly"
            base_url_missing_industry =  f"https://app.dealroom.co/curated-heatmaps/funding/industry/f/growth_stages/not_mature/rounds/not_GRANT_SPAC%20PRIVATE%20PLACEMENT/{filter_list_industry[i]['filter']}tags/not_outside%20tech?endYear=2024&interval=yearly"
            filter_list_industry[i]['url']=base_url_industry+sub_industry_rows+end_url
            filter_list_industry[i]['url_missing'] = base_url_missing_industry+industry_rows+end_url
        i+=1

#industry_tables = []
page = browser.new_page()
for metric in ['rounds']:
    for i in range(len(industry_tables),len(filter_list_industry)*2):
        if i>=100: metric = 'amount'
        page.goto(filter_list_industry[i%len(filter_list_industry)]['url'].replace('&type=amount','&type='+metric))
        sleep(20)
        results_dict = table_extractor(page)
        temp_table = pd.DataFrame.from_dict(results_dict).transpose().reset_index()
        temp_table = table_cleaner(temp_table,_definitions=filter_list_industry[i%len(filter_list_industry)],col_name = 'Industries')
        temp_table['metric']=metric
        industry_tables = industry_tables + [temp_table]
        sleep(np.random.randint(3,9))
        print(len(industry_tables))

pd.concat(industry_tables,axis=0).to_csv(r'C:\Users\merom\Documents\GitHub\collancer\investment-nsw\output\master_data_industry.csv')  

page = browser.new_page()
for metric in ['amount']:
    for i in range(len(industry_tables),len(filter_list_industry)*4):
        if i>=300: metric = 'rounds'
        page.goto(filter_list_industry[i%len(filter_list_industry)]['url_missing'].replace('&type=amount','&type='+metric))
        sleep(20)
        results_dict = table_extractor(page)
        temp_table = pd.DataFrame.from_dict(results_dict).transpose().reset_index()
        temp_table = table_cleaner(temp_table,_definitions=filter_list_industry[i%len(filter_list_industry)],col_name = 'Industries')
        temp_table['metric']=metric
        industry_tables = industry_tables + [temp_table]
        sleep(np.random.randint(1,5))
        print(len(industry_tables))

pd.concat(industry_tables,axis=0).to_csv(r'C:\Users\merom\Documents\GitHub\collancer\investment-nsw\output\master_data_industry2.csv')
    



#-------------------------------------------------------------------------------------
# Industry filters - public funds
#-------------------------------------------------------------------------------------
industry_rows = r"&rows=enterprise%2520software~wellness%2520beauty~music~dating~telecom~kids~hosting~home%2520living~event%2520tech~robotics~jobs%2520recruitment~semiconductors"
sub_industry_rows = r"&rows=accessories~accommodation~adtech~agritech~apparel~autonomous%2520%2526%2520sensor%2520tech~banking~betting%2520%2526%2520gambling~biotechnology~board%2520games~booking%2520%2526%2520search~business%2520travel~clean%2520energy~cloud%2520%2526%2520infrastructure~console%2520%2526%2520pc%2520gaming~construction~content%2520production~crm%2520%2526%2520sales~crypto%2520and%2520defi~data%2520protection~device%2520security%2520%2526%2520antivirus~ecommerce%2520solutions~energy%2520efficiency~energy%2520providers~energy%2520storage~esports~financial%2520management%2520solutions~fitness~food%2520logistics%2520%2526%2520delivery~footwear~health%2520platform~identity%2520%2526%2520access~in-store%2520retail%2520%2526%2520restaurant%2520tech~innovative%2520food~insurance~intellectual%2520property~kitchen%2520%2526%2520cooking%2520tech~learning%2520tools%2520and%2520resources~legal%2520documents%2520management~legal%2520information~legal%2520matter%2520management~logistics%2520%2526%2520delivery~luxury~maintenance~marketing%2520analytics~medical%2520devices~mobile%2520gaming~mobility~mortgages%2520%2526%2520lending~navigation%2520%2526%2520mapping~oil%2520%2526%2520gas~online%2520travel%2520agency~payments~pharmaceutical~public%2520safety~publishing~real%2520estate%2520services~real%2520estate%2520software~regtech~regtech%2520%2526%2520compliance~search%252C%2520buy%2520%2526%2520rent~self-service%2520and%2520lawyer%2520marketplace~social%2520media~sport%2520league%2520%2526%2520club~sport%2520media~sport%2520platform%2520%2526%2520application~sport%2520supplements~sporting%2520equipment~streaming~travel%2520analytics%2520%2526%2520software~vehicle%2520production~waste%2520solution~water~wealth%2520management~workspaces"
location_filters = {
    'All':'',
    'Australia':'australia',
    'Canada':'canada',
    'Victoria':'victoria_1',
    'New South Wales':'new_south_wales',
    'Ontario':'ontario_7',
    'United States':'united_states',
    'Pennsylvania':'pennsylvania',
    'Texas':'texas',
    'New York':'state_new_york_usa',
    'New Zealand':'new_zealand',
    'Israel':'israel',
    'United Kingdom':'united_kingdom',
    'Singapore':'singapore'
    }

investor_locations = {'All':''}
    
i=0
filter_list_industry={}
for rkey,rval in location_filters.items():
    if rkey == "All": f_region_filter = ''
    else: f_region_filter = f"slug_locations/anyof_~{rval}~/"

    f_funds_filter = 'investors_types/anyof_sovereign%20wealth%20fund_government%20nonprofit/'
    filter_list_industry[i] = {
        'Background':'All',
        'Degree':'All',
        'Gender':'All',
        'Founder Experience':'All',
        'Round':'All',
        'region':rkey,
        'Investor':'Public',
        'filter':f_region_filter+f_funds_filter
    }

    base_url_industry = f"https://app.dealroom.co/curated-heatmaps/funding/sub_industry/f/growth_stages/not_mature/rounds/not_GRANT_SPAC%20PRIVATE%20PLACEMENT/{filter_list_industry[i]['filter']}tags/not_outside%20tech?endYear=2024&interval=yearly"
    base_url_missing_industry =  f"https://app.dealroom.co/curated-heatmaps/funding/industry/f/growth_stages/not_mature/rounds/not_GRANT_SPAC%20PRIVATE%20PLACEMENT/{filter_list_industry[i]['filter']}tags/not_outside%20tech?endYear=2024&interval=yearly"
    filter_list_industry[i]['url']=base_url_industry+sub_industry_rows+end_url
    filter_list_industry[i]['url_missing'] = base_url_missing_industry+industry_rows+end_url
    if ((rkey == 'New South Wales')|(rkey == 'All'))&(fukey == 'All'):
        i+=1
        filter_list_industry[i] = {
        'Background':'All',
        'Degree':'All',
        'Gender':'All',
        'Founder Experience':'All',
        'Round':'Early',
        'region':rkey,
        'Investor':'Public',
        'filter':f_region_filter+"standardised_round_label/anyof_SEED_PRE-SEED_SEED%2B_SEED%20EXTENSION_MICRO-SEED/"
        }
        base_url_industry = f"https://app.dealroom.co/curated-heatmaps/funding/sub_industry/f/growth_stages/not_mature/rounds/not_GRANT_SPAC%20PRIVATE%20PLACEMENT/{filter_list_industry[i]['filter']}tags/not_outside%20tech?endYear=2024&interval=yearly"
        base_url_missing_industry =  f"https://app.dealroom.co/curated-heatmaps/funding/industry/f/growth_stages/not_mature/rounds/not_GRANT_SPAC%20PRIVATE%20PLACEMENT/{filter_list_industry[i]['filter']}tags/not_outside%20tech?endYear=2024&interval=yearly"
        filter_list_industry[i]['url']=base_url_industry+sub_industry_rows+end_url
        filter_list_industry[i]['url_missing'] = base_url_missing_industry+industry_rows+end_url
    i+=1

industry_tables_public = []
page = browser.new_page()
for metric in ['amount']:
    for i in range(len(industry_tables_public),len(filter_list_industry)*2):
        if i<len(industry_tables_public): page.goto(filter_list_industry[i%len(filter_list_industry)]['url'])
        else: page.goto(filter_list_industry[i%len(filter_list_industry)]['url_missing'])
        sleep(20)
        results_dict = table_extractor(page)
        temp_table = pd.DataFrame.from_dict(results_dict).transpose().reset_index()
        temp_table = table_cleaner(temp_table,_definitions=filter_list_industry[i%len(filter_list_industry)],col_name = 'Industries')
        temp_table['metric']=metric
        industry_tables_public = industry_tables_public + [temp_table]
        sleep(np.random.randint(3,9))
        print(len(industry_tables_public))

#pd.concat(industry_tables_public,axis=0).to_csv(r'C:\Users\merom\Documents\GitHub\collancer\investment-nsw\output\master_data_industry.csv')  

pd.concat(industry_tables_public,axis=0).to_csv(r'C:\Users\merom\Documents\GitHub\collancer\investment-nsw\output\master_data_industry2_public_funds.csv')


#--------------------------------------------------------------------------------
ecosystem_url = 'https://app.dealroom.co/metrics/ecosystem/f/year_min/anyof_2015/rows/anyof_~funding_change_12_months~_~startups_count~_~unicorns_count~_~future_unicorns_count~_~years_funding_number~_~years_funding_amount~_~years_exits_amount~_~employees_number~_~current_year_ecosystem_value~_~years_new_funds~_~startups_count_founded_since_2010~_~years_exits_gt_100m_amount~_~accelerators_count~_~workspaces_count~_~most_funded_technologies~_~top_funding_sources~_~most_funded_industries~_~years_exits_number~/location/anyof_~united_kingdom~_israel_~united_states~_singapore_~new_south_wales~_~victoria_1~_~ontario_7~_~state_new_york_usa~_pennsylvania_texas_canada_~new_zealand~_australia?sort=-employees_number&applyDefaultFilters=true+'
#page = browser.new_page()
page.goto(ecosystem_url)
table_cleaner_simple(pd.DataFrame.from_dict(table_extractor(page)).transpose().iloc[:,:-1],exclusions=[14,15,16]).\
    to_csv(r'C:\Users\merom\Documents\GitHub\collancer\investment-nsw\output\ecosystem_data2.csv')


#----------------------------------------------------------------------------------
# Technologies
#----------------------------------------------------------------------------------

location_rows = r"&rows=australia~canada~~victoria_1~~~new_south_wales~~%27~~ontario_7~~~united_states~~pennsylvania~texas~~state_new_york_usa~~~new_zealand~~israel~~united_kingdom~singapore~europe~asia~~usa_and_canada~~~latin_america~~africa~oceania" # row seperator ~
i=0
filter_list_round = {}
tech_list = {
    'Quantum':'quantum%20technologies'
    ,'AI':'artificial%20intelligence'
    ,'Deep Tech': 'deep%20tech'
    ,'Hardware':'hardware'
    ,'Mobile Apps':'mobile%20app'
    ,'Big Data': 'big%20data'
    ,'IoT':'iot%20internetofthings'
    ,'VR/AR':'virtual%20reality_augmented%20reality'
    ,'Machine Learning':'machine%20learning_natural%20language%20processing_deep%20learning_computer%20vision'
    ,'Nano-technology':'nanotech'
    ,'3D Technology': '3d%20technology'
    ,'Blockchain':'blockchain'
    ,'Autonomous Sensors':'autonomous%20%26%20sensor%20tech'
    ,'All':''
}
for key,val in tech_list.items():
    print(key)
    if key == "All": round_filter = ''
    else: round_filter = f"technologies/anyof_{val}/"
    filter_list_round[i] = {
        'Background':'All',
        'Degree':'All',
        'Gender':'All',
        'Founder Experience':'All',
        'Round':'All',
        'Investor':'All',
        'Industries':key,
        'filter':round_filter
    }
    print(i,filter_list_round[i])
    base_url_location = f"https://app.dealroom.co/curated-heatmaps/funding/location/f/growth_stages/not_mature/rounds/not_GRANT_SPAC%20PRIVATE%20PLACEMENT/{filter_list_round[i]['filter']}tags/not_outside%20tech?endYear=2024&interval=yearly"
    filter_list_round[i]['url']=base_url_location+location_rows+end_url
    i+=1

page = browser.new_page()
tech_tables_list = []
for metric in ['future_unicorns','unicorns','amount']:
    for i in filter_list_round:
        if (metric == 'future_unicorns')|(metric=='unicorns'):
            page.goto(filter_list_round[i]['url'].replace('&type=amount','&type='+metric).replace('/funding/',f'/{metric}/'))
        else: 
            page.goto(filter_list_round[i]['url'].replace('&type=amount','&type='+metric))
        sleep(15)
        results_dict = table_extractor(page)
        temp_table = pd.DataFrame.from_dict(results_dict).transpose().reset_index()
        temp_table = table_cleaner(temp_table,_definitions=filter_list_round[i])
        temp_table['metric']=metric
        tech_tables_list = tech_tables_list + [temp_table]
        sleep(np.random.randint(3,9))

pd.concat(tech_tables_list,axis=0).to_csv(r'C:\Users\merom\Documents\GitHub\collancer\investment-nsw\output\technologies_data2.csv')


#----------------------------------------------------------------------------------
# Public funds
#----------------------------------------------------------------------------------

i=0
filter_list_round = {}
tech_list = {
    'All':''
}
for key,val in tech_list.items():
    print(key)
    if key == "All": round_filter = 'investors_types/anyof_sovereign%20wealth%20fund_government%20nonprofit/'
    else: round_filter = f"technologies/anyof_{val}/"
    filter_list_round[i] = {
        'Background':'All',
        'Degree':'All',
        'Gender':'All',
        'Founder Experience':'All',
        'Round':'All',
        'Investor':'Public',
        'Industries': 'All',
        'filter':round_filter
    }
    print(i,filter_list_round[i])
    base_url_location = f"https://app.dealroom.co/curated-heatmaps/funding/location/f/growth_stages/not_mature/rounds/not_GRANT_SPAC%20PRIVATE%20PLACEMENT/{filter_list_round[i]['filter']}tags/not_outside%20tech?endYear=2024&interval=yearly"
    filter_list_round[i]['url']=base_url_location+location_rows+end_url
    i+=1

public_funds = []
for metric in ['rounds','amount']:
    for i in filter_list_round:
        page.goto(filter_list_round[i]['url'].replace('&type=amount','&type='+metric))
        sleep(10)
        results_dict = table_extractor(page)
        temp_table = pd.DataFrame.from_dict(results_dict).transpose().reset_index()
        temp_table = table_cleaner(temp_table,_definitions=filter_list_round[i])
        temp_table['metric']=metric
        public_funds = public_funds + [temp_table]
        sleep(np.random.randint(3,9))

pd.concat(public_funds,axis=0).to_csv(r'C:\Users\merom\Documents\GitHub\collancer\investment-nsw\output\public_funds_data.csv')