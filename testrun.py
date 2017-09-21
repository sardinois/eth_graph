from eth_graph.graph.Neo4J import Neo4J
from eth_graph.ethereum.geth import Geth
from tqdm import tqdm

geth = Geth()
graph = Neo4J(uri="bolt://localhost:7687", user="neo4j", password="Neo")

min_block = 0
max_block = 1000000
for block in tqdm(geth.get_blocks(min_block, max_block), total=max_block-min_block):
    graph.save_block(block)
