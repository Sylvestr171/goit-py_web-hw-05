#public API привату
# https://api.privatbank.ua/p24api/exchange_rates?json&date=01.12.2014

# EUR та USD

import platform

import aiohttp
import asyncio

from datetime import date, timedelta

from urllib.parse import urlencode

def urls(number_of_days :int) -> list[str]:
    
    today = date.today() #.strftime("%d.%m.%y")
    urls = []
    i = 0
    while i != number_of_days:

        date_for_request = (today - timedelta(days=i)).strftime("%d.%m.%Y")
        params = {"json": "", "date": date_for_request}
        url = f"https://api.privatbank.ua/p24api/exchange_rates?{urlencode(params)}"
        i = i + 1
        urls.append(url)
    print(urls)
    return urls




async def main(list_of_url):
    
    async with aiohttp.ClientSession() as session:
        result=[]
        for url in list_of_url:
            print(url)
            async with session.get(url) as response:

                print("Status:", response.status)
                print("Content-type:", response.headers['content-type'])
                print('Cookies: ', response.cookies)
                print(response.ok)
                result_of_response = await response.json()
                result.append(result_of_response)
        return result


if __name__ == "__main__":
    
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    r = asyncio.run(main(urls(3)))
    print(r)