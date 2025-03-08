import httpx
import asyncio
from external_api import STOCKS_API_URL

async def test_api():
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(STOCKS_API_URL)
        print("Status Code:", response.status_code)
        print("Final URL:", response.url)  # Check the final redirected URL
        print("Raw Response:", response.text)

        try:
            data = response.json()
            print("JSON Response:", data)
        except Exception as e:
            print("JSON Parse Error:", e)

asyncio.run(test_api())
