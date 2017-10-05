from eth_graph.graph.Neo4J import Neo4J
from eth_graph.ethereum.geth import Geth
from tqdm import tqdm
from urllib3.connectionpool import xrange
import argparse

parser = argparse.ArgumentParser(description='Import geth transactions in Neo4J')
parser.add_argument('--start-block', type=int, dest='min_block', default=4220099, help='start block number')
parser.add_argument('--end-block', type=int, dest='max_block', default=4338330, help='end block number')
parser.add_argument('--batch-size', type=int, dest='minibatch_size', default=100,
                    help='amount of blocks that will be added to Neo4J in a single transaction')
parser.add_argument('--neo-address', type=str, dest='address', default="bolt://localhost:7687",
                    help='Connections string for the Neo4J server')
parser.add_argument('--neo-user', type=str, dest='user', default='neo4j', help='Neo4J Username')
parser.add_argument('--neo-password', type=str, dest='passwords', default='neo4j', help='Neo4J Password')
args = parser.parse_args()
min_block = args.min_block
max_block = args.max_block
minibatch_size = args.minibatch_size

geth = Geth()
graph = Neo4J(uri=args.address, user=args.user, password=args.password)

ranges = list((n, n + minibatch_size) for n in xrange(min_block, max_block, minibatch_size))
with tqdm(total=max_block - min_block, unit="blocks", leave=False, smoothing=0.1) as pbar:
    for block in ranges:
        blocks = geth.get_blocks(block[0], block[1])
        graph.save_blocks(blocks)
        pbar.update(minibatch_size)
