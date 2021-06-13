"""
Blockchain creates a first block or genesis and then other blocks add to the chain which is basically a list of blocks
A block usually contains an index, timestamp of when the block is created, the data in the block, the hash for that data
And then the hash for the previous block

When the Blockchain class if first instantiated the genesis block is created and other blocks are after that.

"""

import asyncio
import json
import math
import random
from time import time
import structlog
from hashlib import sha256

logger = structlog.getLogger("blockchain")


class BlockChain(object):
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.target = "0000ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"

        # Create the genesis block
        logger.info("Creating Genesis Block")
        self.chain.append(self.new_block())

    # The function that adds new blocks to the chain
    def new_block(self):
        block = self.create_block(
            height=len(self.chain),
            transactions=self.pending_transactions,
            previous_hash=self.last_block["hash"] if self.last_block else None,
            nonce=format(random.getrandbits(64), "x"),
            target=self.target,
            timestamp=time(),
        )
        # Reset the list of pending transactions
        self.pending_transactions = []
        return block

    @staticmethod
    def hash(block):
        # We ensure the dictionary is sorted or we'll have inconsistent hashes
        # Changes the json to text and then changes it to byte
        block_string = json.dumps(block, sort_keys=True).encode()
        return sha256(block_string).hexdigest()

    @property
    def last_block(self):
        # Return the last block in the chain (if there are blocks)
        return self.chain[-1] if self.chain else None

    def new_transaction(self, sender, recipient, amount):
        # Adds a new transaction to the list of pending transactions
        self.pending_transactions.append({
            "recipient": recipient,
            "sender": sender,
            "amount": amount,
        })

    def add_block(self, block):
        # TODO: Add proper validation logic here
        self.chain.append(block)

    def recalculate_target(self, block_index):
        """
        Return the number we need to get below to mine a block
        :param block_index:
        :return:
        """
        # Check if we need to recalculate the target
        if block_index % 10 == 0:
            # Expected time span of 10 blocks
            expected_timespan = 10 * 10

            # Calaculate the actual time span
            actual_timespan = self.chain[-1]["timestamp"] - self.chain[-10]["timestamp"]

            # Figure out what the offset is
            ratio = actual_timespan / expected_timespan

            # Now lets adjust the ratio to not be too extreme
            ratio = max(0.25, ratio)
            ratio = min(4.00, ratio)

            # Calculate the new target by multiplying the current one by ratio
            new_target = int(self.target, 16) * ratio
            self.target = format(math.floor(new_target), "x").zfill(64)
            logger.info(f"Calculated new mining target: {self.target}")

        return self.target

    async def get_blocks_after_timestamp(self, timestamp):
        for index, block in enumerate(self.chain):
            if timestamp < block["timestamp"]:
                return self.chain[index:]

    async def mine_new_block(self):
        self.recalculate_target(self.last_block["index"] + 1)
        while True:
            new_block = self.new_block()
            if self.valid_block(new_block):
                break

        await asyncio.sleep(0)
        self.chain.append(new_block)
        logger.info("Found a new block: ", new_block)

    @staticmethod
    def create_block(height, transactions, previous_hash, nonce, target, timestamp=None):
        block = {
            "height": height,
            "transactions": transactions,
            "previous_hash": previous_hash,
            "nonce": nonce,
            "target": target,
            "timestamp": timestamp or time(),
        }

        # Get the hash of this new block and add it to the block
        block_string = json.dumps(block, sort_keys=True).encode()
        block["hash"] = sha256(block_string).hexdigest()
        return block

    def valid_block(self, block):
        # Check if a blocks hash is less than the target
        return block["hash"] < self.target
