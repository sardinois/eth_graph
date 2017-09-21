from eth_graph.ethereum.block import Block
from neo4j.exceptions import ClientError
from neo4j.v1 import GraphDatabase


class Neo4J:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password), max_retry_time=1)

    def close(self):
        self._driver.close()

    def save_block(self, block: Block):
        with self._driver.session() as session:
            try:
                with session.begin_transaction() as tx:
                    tx.run("""
                            MERGE (pb:Block {hash:$parentHash})
                            MERGE (b:Block {hash:$hash})
                                SET b.number=$number, b.parentHash=$parentHash, b.timestamp=$timestamp
                              MERGE (b)<-[p:PARENT_BLOCK_OF]-(pb)""",
                           hash=block.hash, number=block.number, parentHash=block.parent_hash,
                           timestamp=block.timestamp.timestamp()*1000)
                    for trans in block.transactions:
                        tx.run("""MATCH (b:Block {hash:$block_hash})
                                    MERGE (tx:Transaction {hash:$tx_hash})
                                    SET tx.value=$value
                                  MERGE (b)<-[:TX_FROM_BLOCK]-(tx)""",
                               tx_hash=trans.hash, value=trans.value, block_hash=block.hash)

                        tx.run("""
                                MERGE (from:Address {hash:$from_address})
                                MERGE (from)<-[f:TX_FROM]-(tx)
                                """, tx_hash=trans.hash, value=trans.value, from_address=trans.from_address,
                               to_address=trans.to_address, block_hash=block.hash)
                        if trans.to_address:
                            tx.run("""
                                    MERGE (to:Address {hash:$to_address})
                                    MERGE (to)<-[f:TX_TO]-(tx)
                                    """,
                                   to_address=trans.to_address)
            except ClientError as e:
                print(e)
