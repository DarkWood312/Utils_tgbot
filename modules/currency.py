import aiohttp


class Currency:
    def __init__(self, session: aiohttp.ClientSession | None = None):
        self.session = session
        self.main_url = 'https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies'

    async def __aenter__(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session is not None:
            await self.session.close()

    def endpoint(self, method: str, date: str = 'latest') -> str:
        main_url = self.main_url.replace('latest', date, 1)
        return f'{main_url}/{method}.json'

    async def get_currency(self, from_currency: str, to_currency: str = 'rub',
                           amount: float = 1, date: str = 'latest') -> float:
        async with self.session.get(self.endpoint(from_currency, date)) as response:
            data = await response.json()
            currency = data[from_currency.lower()][to_currency.lower()] * amount
            if currency > 10000:
                currency = round(currency)
            elif currency > 100:
                currency = round(currency, 2)
            elif currency > 10:
                currency = round(currency, 3)
            elif currency > 1:
                currency = round(currency, 4)
            else:
                pass
            return currency

    async def currencies(self) -> dict[str, str]:
        async with self.session.get(self.main_url) as response:
            data = await response.json()
            return data
