# this script is adapted from https://blog.jonlu.ca/posts/async-python-http
import sys
import os
import json
import asyncio
import aiohttp
from utils import (
    compress_json,
    get_env
)

eth_provider_url = get_env("ETH_PROVIDER_URL")

with open("../data/logs_info.json", "r") as f:
    logs_info = json.load(f)

# Initialize connection pool
conn = aiohttp.TCPConnector(limit_per_host=100, limit=0, ttl_dns_cache=300)
PARALLEL_REQUESTS = 100
transaction_hashes = logs_info["transaction_hashes"]
results = []
data = {
    "jsonrpc": "2.0",
    "method": "eth_getTransactionByHash",
}

async def gather_with_concurrency(n):
    semaphore = asyncio.Semaphore(n)
    session = aiohttp.ClientSession(connector=conn)
    # heres the logic for the generator
    async def post(url, data):
        async with semaphore:
            async with session.post(url, json=data) as response:
                obj = json.loads(await response.read())
                results.append(obj)

    await asyncio.gather(
        *(post(eth_provider_url, data={**data, "id": t, "params": [transaction_hash]}) for t, transaction_hash in enumerate(transaction_hashes))
    )
    await session.close()

print(f"Beginning {len(transaction_hashes)} requests")
loop = asyncio.get_event_loop()
loop.run_until_complete(gather_with_concurrency(PARALLEL_REQUESTS))
conn.close()
print(f"Completed {len(transaction_hashes)} requests with {len(results)} results")

print('Writing results')
for result in results:
    index = transaction_hashes.index(result["result"]["hash"])
    if not result.get("result"):
        print(result)
    if index != result["id"]:
        print("mismatched index: ", result["result"]["hash"])
    with open(f"../data/transactions/{index}_{result['result']['hash']}.json", "w+") as f:
        json.dump(result["result"], f, indent=2)