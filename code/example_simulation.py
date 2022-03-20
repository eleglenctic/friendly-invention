from brotli import compress

def count_zeros(calldata: bytes):
    num = 0
    for i in range(len(calldata)):
        if calldata[i] == 0:
            num += 1
    return num, len(calldata) - num

def compute_l1_cost(calldata: bytes):
    n_zeros, n_nonzeros = count_zeros(calldata)
    return (4 * n_zeros) + (16 * n_nonzeros)

def print_calldata(calldata: bytes):
    size = len(calldata)
    n_words = size // 32
    remainder = size % 32
    for i in range(n_words if not remainder else n_words + 1):
        start = i * 32
        stop = start + 32
        if stop > (size - 1):
            # print(calldata[start:].hex().ljust(64, '0'))
            print(calldata[start:].hex())
        else:
            print(calldata[start:stop].hex())

def print_data(key, value, width=64):
    print(str(key) + str(value).rjust(int(width - len(key))))

def analyze_calldata(calldata: bytes, compressed: bool=False, verbose: bool=True):
    if not compressed and verbose:
        print("===================== uncompressed calldata ====================")
    elif verbose:
        print("======================= compressed calldata ====================")
    n_zeros, n_nonzeros = count_zeros(calldata)
    size = len(calldata)
    cost = compute_l1_cost(calldata)
    if verbose:
        print_data("number of zero bytes", n_zeros)
        print_data("number of non-zero bytes", n_nonzeros)
        print_data("total bytes", size)
        print_data("l1 gas cost", cost)
        # print("\ncalldata")
        # print_calldata(calldata)
    if not compressed:
        compressed_n_zeros, compressed_size, compressed_cost = analyze_calldata(
            compress(calldata), compressed=True, verbose=verbose
        )
        compression_ratio = size / compressed_size
        space_saving = 1 - 1 / compression_ratio
        cost_ratio = cost / compressed_cost
        gas_saving = 1 - 1 / cost_ratio
        if verbose:
            print("======================= ratio comparisons ======================")
            print_data("compression ratio", compression_ratio)
            print_data("space saving", space_saving)
            print_data("cost ratio", cost_ratio)
            print_data("gas saving", gas_saving)
        return {
            "compressed_n_zeros": compressed_n_zeros,
            "compressed_size": compressed_size,
            "compressed_cost": compressed_cost,
            "uncompressed_n_zeros": n_zeros,
            "uncompressed_size": size,
            "uncompressed_cost": cost,
            "compression_ratio": compression_ratio,
            "space_saving": space_saving,
            "cost_ratio": cost_ratio,
            "gas_saving": gas_saving
        }
    else:
        return n_zeros, size, cost

if __name__ == "__main__":
    from codecs import decode
    # batch from https://etherscan.io/tx/0x9e123a6dd8b707e9c6397f636da49e903083930f474fab080af8843032e82126

    with open("./example_batch.txt", "r") as f:
        batch_calldata = f.read()

    analyze_calldata(decode(batch_calldata[10:], "hex_codec"))

    # sequences = {}
    # bytewidth = 8
    # for i in range(0, len(batch_calldata) - bytewidth, bytewidth):
    #     if sequences.get(batch_calldata[i:i+bytewidth]) is not None:
    #         sequences[batch_calldata[i:i+bytewidth]] += 1
    #     else:
    #         sequences[batch_calldata[i:i+bytewidth]] = 1
    # sorted_frequencies = {k: v for k, v in sorted(sequences.items(), key=lambda item: item[1], reverse=True)}
    # k = list(sorted_frequencies.keys())
    # word = ""
    # for i in range(8):
    #     word += k[i]

    # analyze_calldata(decode(word + batch_calldata[10:], "hex_codec"))
    # analyze_calldata(decode("00000000000000000000000000000000000000000000000000000000000000" + batch_calldata[10:], "hex_codec"))