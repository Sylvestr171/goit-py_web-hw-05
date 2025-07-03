import asyncio
import logging
import websockets
import names
import aiohttp
import datetime
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK
from urllib.parse import urlencode
import json

logging.basicConfig(level=logging.INFO)


class Server:
    clients = set()

    async def register(self, ws: WebSocketServerProtocol):
        ws.name = names.get_full_name()
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects')

    async def unregister(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects')

    async def send_to_clients(self, message: str):
        if self.clients:
            [await client.send(message) for client in self.clients]

    async def ws_handler(self, ws: WebSocketServerProtocol):
        await self.register(ws)
        try:
            await self.distrubute(ws)
        except ConnectionClosedOK:
            pass
        finally:
            await self.unregister(ws)

    async def distrubute(self, ws: WebSocketServerProtocol):
        async for message in ws:
            if message.split()[0] == "exchange":
                if len(message.split()) > 1:
                    if message.split()[1].isdigit():
                        number_of_days = int(message.split()[1])
                        exchange = str(await get_arhive_course(urls(number_of_days)))
                        await async_log (message)
                        await self.send_to_clients(exchange)
                    else:
                        exchange = await get_exchange()
                        await async_log (message)
                        await self.send_to_clients(exchange)
                else:
                    exchange = await get_exchange()
                    await async_log (message)
                    await self.send_to_clients(exchange)
            else:
                await self.send_to_clients(f"{ws.name}: {message}")

async def async_log(message: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp} - {message}")

def urls(number_of_days :int):
    
    if number_of_days < 1:
        number_of_days = 1
    elif number_of_days > 10:
        number_of_days = 10

    today = datetime.date.today()
    urls = []
    i = 0
    while i != number_of_days:

        date_for_request = (today - datetime.timedelta(days=i)).strftime("%d.%m.%Y")
        params = {"json": "", "date": date_for_request}
        url = f"https://api.privatbank.ua/p24api/exchange_rates?{urlencode(params)}"
        i = i + 1
        urls.append(url)
    print(urls)
    return urls

async def get_arhive_course(list_of_url):
    result=[]
    async with aiohttp.ClientSession() as session:
        task = [request(url) for url in list_of_url]
        data_from_url=await asyncio.gather(*task, return_exceptions=True)
        print(data_from_url)
        result = await filtering_data(data_from_url)
        return result

async def filtering_data(data):
    
    filter_data = {}
    for i in data:
        if isinstance(i, Exception): #обробка помилок
            continue
        date_key = i['date']
        currency_dict = {}
        for x in i['exchangeRate']:
            if x['currency'] in ("EUR", "USD"):
                currency_dict[x['currency']] = {
                "sale": x.get("saleRate"),
                "purchase": x.get("purchaseRate")
                }
            filter_data[date_key] = currency_dict
    return json.dumps(filter_data)

async def request(url: str) -> dict | str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.ok:
                result_of_response = await resp.json()
                return result_of_response
            else:
                return "Збій зв'язку з сервером"

async def get_exchange():
    response = await request(f'https://api.privatbank.ua/p24api/pubinfo?exchange&coursid=5')
    exchange_message = []
    for i in response:
        exchange_message.append(f"{i["ccy"]} Продаж/Купівля: {i["sale"]}/{i["buy"]}\n")
    return exchange_message


async def main():
    server = Server()
    async with websockets.serve(server.ws_handler, 'localhost', 8080):
        await asyncio.Future()  # run forever

if __name__ == '__main__':
    asyncio.run(main())