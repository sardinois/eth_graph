import json
from eth_graph.ethereum.block import GethBlock
import requests


class Geth():
    def __init__(self,
                 url="localhost",
                 port=8545,
                 ):
        self.url = url
        self.port = port
        self.headers = {"content-type": "application/json"}

        pass

    def last_block(self):
        pass

    def get_block(self, block_num):
        """Get a specific block from the blockchain and filter the data."""
        data = self._rpc_request("eth_getBlockByNumber", [hex(block_num), True], "result")
        return GethBlock(data)

    def get_blocks(self, start_num, end_num):
        for n in range(start_num, end_num):
            yield self.get_block(n)

    def _rpc_request(self, method, params, key):
        """Make an RPC request to geth on port 8545."""
        payload = {
            "method": method,
            "params": params,
            "jsonrpc": "2.0",
            "id": 0
        }
        res = requests.post(
            "http://{}:{}".format(self.url, self.port),
            data=json.dumps(payload),
            headers=self.headers).json()
        return res[key]


