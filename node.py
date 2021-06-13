import asyncio

from daniel_coin.blockchain import BlockChain
from daniel_coin.connections import ConnectionPool
from daniel_coin.peers import P2PProtocol
from daniel_coin.server import Server

blockchain = BlockChain()
connection_pool = ConnectionPool()

server = Server(blockchain, connection_pool, P2PProtocol)


async def main():
    # Start the server
    await server.listen()


asyncio.run(main())
