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
def get_env(key: str, raise_on_none: bool=False) -> str:
    load_dotenv(find_dotenv())
    value = os.environ.get(key)
    if value is None:
        if raise_on_none:
            raise Exception(f"export environment variable {key} or add it to .env file")
        return ""
    return value

################################################################################
# compression
################################################################################
def compress_json(json_data: dict) -> bytes:
    return brotli.compress(json.dumps(data).encode("utf-8"))

def decompress_json(compressed_data: bytes) -> dict:
    return json.loads(brotli.decompress(compressed_data))

################################################################################
# ethereum
################################################################################
def keccak256(data: bytes) -> bytes:
    hasher = keccak.new(digest_bits=256)
    hasher.update(data)
    return hasher.digest()

def log_topic(event_sig: str) -> str:
    return "0x" + keccak256(event_sig.encode("utf-8")).hex()

def fn_selector(fn_sig: str) -> str:
    return "0x" + keccak256(fn_sig.encode("utf-8"))[0:4].hex()

def decode_fn(calldata: str, arg_types: list, arg_fields: list):
    decoded_tuple = eth_abi.decode_abi(
        arg_types, codecs.decode(calldata, "hex_codec")
    )
    return { field:decoded_tuple(f) for (f, field) in enumerate(arg_fields) }

def eth_request(provider_url: str, method: str, params: list):
    return requests.post(provider_url, json={
        "id": 0,
        "jsonrpc": "2.0",
        "method": method,
        "params": params
    }).json()

def get_logs(provider_url: str, from_block: int, to_block: int, topic: str):
    params = [{
        "fromBlock": hex(from_block),
        "toBlock": hex(to_block),
        "topics": [topic]
    }]
    return eth_request(provider_url, "eth_getLogs", params)

def get_transaction_by_hash(provider_url: str, transaction_hash: str):
    params = [transaction_hash]
    return eth_request(provider_url, "eth_getTransactionByHash", params)

class Provider:
    def __init__(self, provider_url: str):
        self.provider_url = provider_url

    def get_logs(self, from_block: int, to_block: int, topic: str):
        return get_logs(self.provider_url, from_block, to_block, topic)

    def get_transaction_by_hash(self, transaction_hash: str):
        return get_transaction_by_hash(self.provider_url, transaction_hash)

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

decoders = { f"{fn_selector(signatures[i])}": lambda calldata: decode_fn(calldata, arg_types[i], arg_fields[i]) for i in range(len(signatures)) }

def decode_by_function_selector(calldata: str):
    selector = calldata[0:10]
    if decoders.get(selector) is None:
        raise Exception(f"Unrecognized function selector: {selector}")
    return decoders[selector](calldata[10:])