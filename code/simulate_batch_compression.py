from multiprocessing import Pool
import brotli
from utils import decode_by_function_selector

def count_zeros(calldata: bytes):
    total = len(calldata)
    num = 0
    for i in range(total):
        if calldata[i] == 0:
            num += 1
    return num, total - num, total

def compute_l1_cost(n_zeros, n_nonzeros):
    return (4 * n_zeros) + (16 * n_nonzeros)

def analyze_calldata(calldata_tuple: bytes, compressed: bool=False):
    calldata = calldata_tuple[0]
    fname = calldata_tuple[1]
    n_zeros, n_nonzeros, size = count_zeros(calldata)
    cost = compute_l1_cost(n_zeros, n_nonzeros)
    if not compressed:
        compressed_n_zeros, compressed_size, compressed_cost = analyze_calldata(
            (brotli.compress(calldata), fname), compressed=True
        )
        compression_ratio = size / compressed_size
        cost_ratio = cost / compressed_cost
        result = {
            "compressed_n_zeros": compressed_n_zeros,
            "compressed_size": compressed_size,
            "compressed_cost": compressed_cost,
            "uncompressed_n_zeros": n_zeros,
            "uncompressed_size": size,
            "uncompressed_cost": cost,
            "compression_ratio": compression_ratio,
            "cost_ratio": cost_ratio,
            "space_saving": 1 - 1 / compression_ratio,
            "gas_saving": 1 - 1 / cost_ratio
        }
        with open(f"../data/resultsV2/{fname}", "w+") as f:
            json.dump(result, f, indent=2)
        return result
    else:
        return n_zeros, size, cost

if __name__ == "__main__":
    import os
    import json
    import codecs
    import time

    start = time.perf_counter()

    batch_files = os.listdir("../data/transactions")
    if ".gitignore" in batch_files:
        batch_files.pop(batch_files.index(".gitignore"))

    print(f"Preparing {len(batch_files)} batches")

    n = 11
    print(f"Preparing batch data using {n} processes")
    def prepare_batch(batch_file):
        with open(f"../data/transactions/{batch_file}", "r") as f:
            batch = json.load(f)
        decoded_calldata = decode_by_function_selector(batch["input"])
        transactions = decoded_calldata["transactions"]
        if len(transactions):
            return (transactions, batch_file)
        else:
            print(f"Skipping a batch with zero transactions: {batch_file}")
            return None

    with Pool(n) as p:
        calldatas = p.map(prepare_batch, batch_files)

    for calldata in calldatas[::-1]:
        if calldata is None:
            calldatas.pop(calldatas.index(calldata))

    print(f"Beginning simulations with {n} processes")

    with Pool(n) as p:
        results = p.map(analyze_calldata, calldatas)

    print("Processing completed. Writing total results")

    with open("../data/resultsV2/_total_results.json", "w+") as f:
        json.dump(results, f, indent=2)

    elapsed = time.perf_counter() - start
    print(f"Total time to simulate: {elapsed} seconds")
    print(f"Total time to simulate: {elapsed/60.0} minutes")