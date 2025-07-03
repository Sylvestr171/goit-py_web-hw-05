import platform
import argparse
import aiohttp
import asyncio
import json
from datetime import date, timedelta
from urllib.parse import urlencode

def urls(number_of_days :int, list_of_currency_in_urls):
    
    today = date.today()
    urls = []
    i = 0
    while i != number_of_days:

        date_for_request = (today - timedelta(days=i)).strftime("%d.%m.%Y")
        params = {"json": "", "date": date_for_request}
        url = f"https://api.privatbank.ua/p24api/exchange_rates?{urlencode(params)}"
        i = i + 1
        urls.append(url)
    # print(urls)
    return urls, list_of_currency_in_urls

async def get_response (session, url):
    async with session.get(url) as resp:
        # print("Status:", resp.status)
        # # print('Cookies: ', resp.cookies)
        # print(resp.ok)
        result_of_response = await resp.json()
        return result_of_response

async def filtering_data(data, list_of_currency_in_f_d):
    
    filter_data = {}
    for i in data:
        if isinstance(i, Exception): #обробка помилок
            continue
        date_key = i['date']
        currency_dict = {}
        for x in i['exchangeRate']:
            if x['currency'] in list_of_currency_in_f_d:
                currency_dict[x['currency']] = {
                "sale": x.get("saleRate"),
                "purchase": x.get("purchaseRate")
                }
        filter_data[date_key] = currency_dict
    return filter_data
    # print(json.dumps(filter_data, indent=2, ensure_ascii=False))   
# 
# def parse_data(list_of_json):
#     for i in list_of_json:
#         print (i['date'])
#         for x in i['exchangeRate']:
#             if x['currency'] in ("EUR", "USD"):
#                 print (f"курс: {x['currency']} - продаж:{x['saleRateNB']}, купівля:{x['purchaseRateNB']}")

async def main(params):
    list_of_url = params[0]
    list_of_currency_in_main = params[1]
    result=[]
    async with aiohttp.ClientSession() as session:
        task = [get_response(session,url) for url in list_of_url]
        data_from_url=await asyncio.gather(*task, return_exceptions=True)
        result = await filtering_data(data_from_url, list_of_currency_in_main)
        return result

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('a', type=int)
    parser.add_argument('-currency', type=str, help="-currency CHF")
    function_param = parser.parse_args().a
    list_of_currency = ["EUR", "USD"]
    list_of_currency.append(parser.parse_args().currency)
    
    if function_param < 1:
        function_param = 1
    elif function_param > 10:
        function_param = 10
    
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    r = asyncio.run(main(urls(function_param, list_of_currency)))
    
    print(json.dumps(r, indent=2, ensure_ascii=False))   
    # parse_data(r)