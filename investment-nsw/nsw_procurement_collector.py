#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
import pandas as pd
import numpy as np
from time import sleep
from playwright.sync_api import sync_playwright

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
years = range(2024,1999,-1)

months_dict = {
    'Dec':(1,31)
    ,'Nov':(1,30)
    ,'Oct':(1,31)
    ,'Sep':(1,30)
    ,'Aug':(1,31)
    ,'Jul':(1,31)
    ,'Jun':(1,30)
    ,'May':(1,31)
    ,'Apr':(1,30)
    ,'Mar':(1,31)
    ,'Feb':(1,28)
    ,'Jan':(1,31)}
dates_list = []
for y in years:
    for k,v in months_dict.items():
        if (k=='Feb')&(y%4 == 0)&(y!=2000): dates_list += [(f'15-{k}-{y}',f'29-{k}-{y}')]
        else: dates_list += [(f'15-{k}-{y}',f'{v[1]}-{k}-{y}')]
        dates_list += [(f'1-{k}-{y}',f'15-{k}-{y}')]

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
urls = [f'https://www.tenders.nsw.gov.au/?event=public.advancedsearch.CNRedirect&invalidEventName=public.CN.search&type=cnEvent&publishFrom={drange[0]}&publishTo={drange[1]}&valueFrom=&valueTo=&supplierABN=&supplierName=&Postcode=&agencyStatus=-1&submit=Search' for drange in dates_list][14:]
pwright = sync_playwright().start()
browser = pwright.chromium.launch(headless=False)
page = browser.new_page()

for u in urls:
    page.goto(u)
    page.wait_for_selector('a[title="Download results"]')
    dload_link = page.query_selector('a[title="Download results"]')
    with page.expect_download() as download_info:
        dload_link.click()
    download = download_info.value
    # Wait for the download process to complete and save the downloaded file somewhere
    download.save_as("C:/Users/merom/Documents/GitHub/collancer/investment-nsw/output/tenders/" + download.suggested_filename)