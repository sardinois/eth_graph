from typing import List, Iterable
from eth_graph.ethereum.block import Block
from neo4j.exceptions import ClientError
from neo4j.v1 import GraphDatabase


class Neo4J:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password), max_retry_time=1)

    def close(self):
        self._driver.close()

    def _save_block_in_transaction(self, tx, block: Block):
        tx.run("""      MATCH (d:Day {day: $day})--(:Month {month: $month})--(:Year {year: $year})
                        MERGE (pb:Block {hash:$parentHash})
                        MERGE (b:Block {hash:$hash})
                            ON CREATE SET b.number=$number, b.parentHash=$parentHash, b.timestamp=$timestamp
                          MERGE (b)<-[p:PARENT_BLOCK_OF]-(pb)
                        MERGE (b)-[:OF_DATE]->(d)
                        """,
                       hash=block.hash, number=block.number, parentHash=block.parent_hash,
                       timestamp=block.timestamp.timestamp() * 1000, day=block.timestamp.day,
                        month=block.timestamp.month, year=block.timestamp.year)

        for trans in block.transactions:
            tx.run("""MATCH (b:Block {hash:$block_hash})
                        MERGE (tx:Transaction {hash:$tx_hash})
                        SET tx.value=$value
                      MERGE (b)<-[:TX_FROM_BLOCK]-(tx)
                      MERGE (from:Address {hash:$from_address})
                      MERGE (from)<-[f:TX_FROM]-(tx)""",
                   tx_hash=trans.hash, value=trans.value, block_hash=block.hash,
                   from_address=trans.from_address)

            if trans.to_address:
                tx.run("""
                        MATCH (tx:Transaction {hash:$tx_hash})
                        MERGE (to:Address {hash:$to_address})
                        MERGE (to)<-[f:TX_TO]-(tx)
                        """,
                       tx_hash=trans.hash, to_address=trans.to_address)

    def save_blocks(self, blocks: Iterable[Block]):
        with self._driver.session() as session:
            with session.begin_transaction() as tx:
                try:
                    for block in blocks:
                        self._save_block_in_transaction(tx, block)
                except ClientError as e:
                    print(e)
