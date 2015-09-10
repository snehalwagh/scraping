"""
Scrape Mobile information from junglee.com
Date : 10 September, 2015
__author__:Snehal
"""

import requests
from bs4 import BeautifulSoup
import json


def writeJson(file_name, data):
    """
    dump data in JSON
    """
    with open(file_name, 'w') as outfile:
        json.dump(data, outfile, indent=4, sort_keys=True)


def get_soup(url):
    """
    get soup for given url
    """
    html_string = requests.get(url).text
    soup = BeautifulSoup(html_string)
    return soup


def get_product_details(tables, mydict):
    """
    get product details for particular mobile phone
    """
    for table in tables:
        all_tr = table.findAll('tr')
        for tr in all_tr:
            key1 = tr.find('td', {'class':'featureName'}).text
            value1 = tr.find('td', {'class':'featureValue'}).text
            mydict[key1] = value1
    return mydict



def inner_page_scraper(inner_url):
    """
    extract all possible infoirmation of individual mobile description
    """
    mydict = {}
    soup = get_soup(inner_url)
    try:
        div = soup.find('div', {'class':'centerColumn'})
        mobile_name = div.find('div', {
            'class':'productAttributes'
        }).text.strip()

        vendor_name = div.find('div', {
            'class':'productByline'
        }).find('a').text.strip()

        out_div = div.find('div', {'id': 'ratingBar fl'})

        ratingValue = out_div.find(
            'meta', {'itemprop': 'ratingValue'}).get('content').strip()

        ratingCount = out_div.find(
            'span', {'itemprop':'ratingCount'}).text.strip()

        price = div.find('span', {
            'class':'offer-price-strikethr-text mrs'}).text.strip()

        mydict = {
            'mobile_name': mobile_name,
            'vendor_name':vendor_name,
            'ratingValue': ratingValue,
            'ratingCount': ratingCount,
            'price':price}

        try:
            tables = soup.find(
                'div', {
                    'class':'productDetailsTable'
                }).findAll('table')
            ret_dict = get_product_details(tables, mydict)
        except Exception as e:
            ret_dict = {}
            print e

    except Exception as e:
        ret_dict = {}
        #print e
        pass

    return ret_dict


def get_features_for_mobiles():
    """
    Get all mobile specification for each mobile
    """
    all_urls = json.load(
        open(
            './mobile_specifications_inner_urls_2.json'
        )
    )
    out_dict = dict()
    for url in all_urls[:100]:
        data = inner_page_scraper(url)
        if data:
            out_dict[url] = data
    print len(out_dict)
    writeJson('./mobile_info_from_junglee.com', out_dict)



def collect_specific_urls(url):
    """
    Collect individual urls from outerpage
    """
    soup = get_soup(url)
    div_results = soup.findAll('div', {'class':'results-row'})

    urls = []
    for outer_div in div_results:
        try:
            inner_divs = outer_div.findAll('div', {'class':'data'})
            for j in inner_divs:
                all_a = j.findAll('a', href=True)
                for anc_tag in all_a:
                    if str(anc_tag['href']).startswith('http://') or str(anc_tag['href']).startswith('https://'):
                        urls.append(anc_tag['href'])
        except Exception as e:
            #print e
            pass

    return list(set(urls))



def collect_outer_urls():
    """
    collect all possible innerurls from outer page
    """
    base_url = "http://www.junglee.com/Mobile-Phones/b/803073031"
    all_urls = list()
    for i in range(0, 10):
        if i == 0:
            inner_urls = collect_specific_urls(base_url)
        else:
            inner_urls = collect_specific_urls(base_url+"?page="+str(i))

        all_urls.extend(inner_urls)
        all_urls = list(set(all_urls))
    print len(all_urls)
    writeJson('./mobile_specifications_inner_urls.json', all_urls)



if __name__ == "__main__":
    collect_outer_urls()
    get_features_for_mobiles()
    print inner_page_scraper('http://www.junglee.com/Gionee-M2-Black-4GB/dp/B00JWJ1VEO/ref=lp_803073031_1_15?s=electronics&ie=UTF8&qid=1441893603&sr=1-15')
