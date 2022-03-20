import os
import json
import codecs
import brotli
import eth_abi
import requests
from Crypto.Hash import keccak
from dotenv import (
    load_dotenv,
    find_dotenv
)


################################################################################
# os
################################################################################
def get_env(key):
    load_dotenv(find_dotenv())
    value = os.environ.get(key)
    if not value:
        raise Exception(f"set environment variable {key} or add it to .env file")
    return value

################################################################################
# compression
################################################################################
def compress_json(data):
    return brotli.compress(json.dumps(data).encode("utf-8"))

def decompress_json(compressed_data):
    return json.loads(brotli.decompress(compressed_data))

################################################################################
# ethereum
################################################################################
def event_topic(event_signature):
    hasher = keccak.new(digest_bits=256)
    hasher.update(event_signature.encode("utf-8"))
    return "0x" + hasher.hexdigest()

def function_selector(function_signature):
    return event_topic(function_signature)[0:10]

def decode_fn(calldata, arg_types, arg_fields):
    decoded_tuple = eth_abi.decode_abi(arg_types, codecs.decode(calldata, "hex_codec"))
    decoded = {}
    for f, field in enumerate(arg_fields):
        decoded[field] = decoded_tuple[f]
    return decoded

def eth_request(url_provider, method, params):
    return requests.post(url_provider, json={
        "id": 0,
        "jsonrpc": "2.0",
        "method": method,
        "params": params
    }).json()

def get_logs(url_provider, from_block, to_block, topic):
    params = [{
        "fromBlock": hex(from_block),
        "toBlock": hex(to_block),
        "topics": [topic]
    }]
    return eth_request(url_provider, "eth_getLogs", params)

def get_transaction_by_hash(url_provider, transaction_hash):
    params = [transaction_hash]
    return eth_request(url_provider, "eth_getTransactionByHash", params)

################################################################################
# sequencer
################################################################################
signatures = [
    "addSequencerL2BatchFromOriginWithGasRefunder(bytes,uint256[],uint256[],bytes32,address)",
    "addSequencerL2BatchFromOrigin(bytes,uint256[],uint256[],bytes32)"
]

arg_types = [
    ["bytes", "uint256[]", "uint256[]", "bytes32", "address"],
    ["bytes", "uint256[]", "uint256[]", "bytes32"]
]

arg_fields = [
    ["transactions", "lengths", "sectionsMetadata", "afterAcc", "gasRefunder"],
    ["transactions", "lengths", "sectionsMetadata", "afterAcc"],
]

decoders = { f"{function_selector(signatures[i])}": lambda calldata: decode_fn(calldata, arg_types[i], arg_fields[i]) for i in range(len(signatures)) }

def decode_by_function_selector(calldata):
    selector = calldata[0:10]
    if decoders.get(selector) is None:
        raise Exception(f"Unrecognized function selector: {selector}")
    return decoders[selector](calldata[10:])