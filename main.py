#public API привату
# https://api.privatbank.ua/p24api/exchange_rates?json&date=01.12.2014

# EUR та USD

import platform

import aiohttp
import asyncio

from datetime import date, timedelta

from urllib.parse import urlencode

def urls(number_of_days :int) -> list[str]:
    
    today = date.today()
    urls = ['https://api.privatbank.ua/p24api/exchange_rates?json=&date=01.07.25']
    i = 0
    while i != number_of_days:

        date_for_request = (today - timedelta(days=i)).strftime("%d.%m.%Y")
        params = {"json": "", "date": date_for_request}
        url = f"https://api.privatbank.ua/p24api/exchange_rates?{urlencode(params)}"
        i = i + 1
        urls.append(url)
    print(urls)
    return urls

async def get_response (session, url):
    async with session.get(url) as resp:

        print("Status:", resp.status)
        print('Cookies: ', resp.cookies)
        print(resp.ok)
        result_of_response = await resp.json()
        return result_of_response

async def main(list_of_url):
    result=[]
    async with aiohttp.ClientSession() as session:
        task = [get_response(session,url) for url in list_of_url]
        result=await asyncio.gather(*task, return_exceptions=True)
        return result


if __name__ == "__main__":
    
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    r = asyncio.run(main(urls(3)))
    print(f"-------------------------------------\n {r}\n---------------------------------------------------------")
    for i in r:
        print(i)
    