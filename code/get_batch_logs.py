import json
from utils import (
    event_topic,
    get_logs,
    get_env
)

eth_provider_url = get_env("ETH_PROVIDER_URL")
sequencer_batch_delivered = event_topic(
    "SequencerBatchDelivered(uint256,bytes32,uint256,bytes32,bytes,uint256[],uint256[],uint256,address)"
)
sequencer_batch_delivered_from_origin = event_topic(
    "SequencerBatchDeliveredFromOrigin(uint256,bytes32,uint256,bytes32,uint256)"
)

first_block = 13318918
end_block = 14413651
step = 2000
transaction_hashes = []
total_batches = 0
offset = 0

for i in range(first_block, end_block - step, step):
    from_block = i + offset
    to_block = i + offset + step
    offset += 1
    response = get_logs(eth_provider_url, from_block, to_block, sequencer_batch_delivered_from_origin)

    if response.get("result") is not None:
        results = response["result"]
        if not len(results):
            continue
        total_batches += len(results)
        next_transaction_hashes = [result["transactionHash"] for result in results]
        for t in next_transaction_hashes:
            if t in transaction_hashes:
                print('duplicate detected', t)

        transaction_hashes += next_transaction_hashes
        with open(f"../data/logs/{i}_{i+step}.json", "w+") as f:
            json.dump(results, f, indent=2)

    print(f"total_batches: {total_batches}")

print(f"total transaction hashes: {len(transaction_hashes)}")

with open("../data/logs_info.json", "w+") as f:
    json.dump({
        "event_topic": sequencer_batch_delivered_from_origin,
        "total_batches": total_batches,
        "from_block": first_block,
        "to_block": end_block,
        "transaction_hashes": transaction_hashes
    }, f, indent=2)