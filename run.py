from eth_graph.graph.Neo4J import Neo4J
from eth_graph.ethereum.geth import Geth
from tqdm import tqdm
from urllib3.connectionpool import xrange
import argparse

parser = argparse.ArgumentParser(description='Import geth transactions in Neo4J')
parser.add_argument('--start-block', dest='min_block',default=1, help='start block number')
parser.add_argument('--end-block', dest='max_block',default=4272453, help='end block number')
parser.add_argument('--batch-size', dest='minibatch_size',default=100, help='amount of blocks that will be added to Neo4J in a single transaction')

args = parser.parse_args()
min_block = args.min_block
max_block = args.max_block
minibatch_size = args.minibatch_size



geth = Geth()
graph = Neo4J(uri="bolt://localhost:7687", user="neo4j", password="Neo")

ranges = list((n, n + minibatch_size) for n in xrange(min_block, max_block, minibatch_size))[::-1]
with tqdm(total=max_block - min_block, unit="blocks", leave=False, smoothing=0.1) as pbar:
    for block in ranges:
        blocks = geth.get_blocks(block[0], block[1])
        graph.save_blocks(blocks)
        pbar.update(minibatch_size)
