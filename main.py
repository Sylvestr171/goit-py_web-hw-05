#public API привату
# https://api.privatbank.ua/p24api/exchange_rates?json&date=01.12.2014

# EUR та USD

import platform

import aiohttp
import asyncio

from datetime import date

from urllib.parse import urlencode

def urls(number_of_days :int) -> list[str]:
    
    today = date.today() #.strftime("%d.%m.%y")
    urls = []
    i = 0
    while i != number_of_days:

        date_for_request = today.replace(day=today.day-1).strftime("%d.%m.%y")
        params = {"json": "", "date": date_for_request}
        url = f"https://api.privatbank.ua/p24api/exchange_rates?{urlencode(params)}"




async def main():
    
    date = "01.07.2025"
    params = {"json": "", "date": date}
    url = f"https://api.privatbank.ua/p24api/exchange_rates?{urlencode(params)}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:

            print("Status:", response.status)
            print("Content-type:", response.headers['content-type'])
            print('Cookies: ', response.cookies)
            print(response.ok)
            result = await response.json()
            return result


if __name__ == "__main__":
    today = date.today() #.strftime("%d.%m.%y")
    print(today.replace(day=today.day+1).strftime("%d.%m.%y"))
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    r = asyncio.run(main())
    print(r)