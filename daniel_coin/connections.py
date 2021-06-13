"""
Connection pool is a class that creates dictionary of peers that the user has met in the P2P network
It add, removes and get_peers for the user and helps get the ip and port of the current user
"""
import structlog
from more_itertools import take

logger = structlog.getLogger(__name__)


class ConnectionPool:
    def __init__(self):
        self.connection_pool = dict()

    def broadcast(self, writer, message):
        """
        Broadcast a general message to the entire pool
        :param writer:
        :param message:
        :return:
        """
        for user in self.connection_pool:
            if user != writer:
                # We don't need to also broadcast to the user sending the message
                user.write(f"{message}\n".encode())

    @staticmethod
    def get_address_string(writer):
        ip = writer.address["ip"]
        port = writer.address["port"]
        return f"{ip}:{port}"

    def get_alive_peers(self, count):
        """
        TODO (Reader): Sort these by most active, but lets just the first count of them for now
        :param count:
        :return:
        """
        return take(count, self.connection_pool.items())

    def add_peer(self, writer):
        """
        Adds a new user to our existing pool
        :param writer:
        :return:
        """
        address = self.get_address_string(writer)
        self.connection_pool[address] = writer
        logger.info("Added new peer to pool", address=address)

    def remove_peer(self, writer):
        """
        Removes an existing user from our pool
        :param writer:
        :return:
        """
        address = self.get_address_string(writer)
        self.connection_pool[address] = writer
        logger.info("Removed peer to pool", address=address)
