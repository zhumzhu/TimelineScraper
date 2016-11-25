import logging
from timelinescraper.engines.TimelineScraperEngine import TimelineScraperEngine
from timelinescraper.TimelineScraper import TimelineScraperError

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from http.client import HTTPException
import socket, codecs, base64 

class BitcoinBlockchainTsEngine(TimelineScraperEngine):

    # TODO: having troubles with genesis
    # http://bitcoin.stackexchange.com/questions/10009/why-can-t-the-genesis-block-coinbase-be-spent

    @staticmethod
    def get_config_params():
        return [{"name":"rpcserver_host", "type":"String"},
                {"name":"rpcserver_port", "type":"String"},
                {"name":"rpc_user", "type":"String"}, 
                {"name":"rpc_password", "type":"String"},
                {"name":"block_batch_size", "type":"String"}]

    def __init__(self, name, rpcserver_host, rpcserver_port, rpc_user, rpc_password, block_batch_size):
        super(self.__class__, self).__init__(name)

        self.BLOCK_BATCH_SIZE = block_batch_size
        
        self.rpc_user = rpc_user
        self.rpc_password = rpc_password
        self.rpcserver_host = rpcserver_host
        self.rpcserver_port = rpcserver_port

        self._init_rpc_connection()

    def _init_rpc_connection(self):
        self.rpc_connection = AuthServiceProxy("http://%s:%s@%s:%s" 
                            % (rpc_user, rpc_password, rpcserver_host, rpcserver_port), timeout=60)

    def seconds_to_wait_after_timeline_exhausted(self):
        return 5*60 # timeline exahusted, we need to wait for another block 5 minutes

    def seconds_to_wait_after_rate_limit_exceeded(self):
        return 5*60 # rate limit is actually never exceeded
    
    def get_next(self, request_since = None, request_to = None):
        self.logger.debug( "get_next invoked with request_since %s request_to %s" % 
            (str(request_since), str(request_to)) )

        results = []

        try:
            if not request_to:
                # request_to = None means we are now looking for the horizon, we create the connection
                self._init_rpc_connection()

                # use only confirmed transactions
                request_to = self.rpc_connection.getblockcount() - 6

            if request_since:
                request_since_plus_1 = max(request_to - self.BLOCK_BATCH_SIZE + 1, request_since+1)
            else:
                request_since_plus_1 = max(request_to - self.BLOCK_BATCH_SIZE + 1, 0)

            self.logger.debug( "getting blocks ranging from %i to %i (included)" % (request_since_plus_1, request_to) )
            
            for i in range(request_since_plus_1, request_to+1):
                block_hash = self.rpc_connection.getblockhash(i)
                block = self.rpc_connection.getblock(block_hash)
                block_txs = block['tx']

                # rpc API has issues with genesis block transaction
                if i!=0:
                    # batch support : print timestamps of blocks 0 to 99 in 2 RPC round-trips:
                    get_raw_txs_commands = [ [ "getrawtransaction", tx] for tx in block_txs]
                    raw_txs = self.rpc_connection.batch_(get_raw_txs_commands)
                else:  
                    # for genesis block we use hardcoded hash of the coinbase transaction, taken from:
                    # https://github.com/bitcoin-abe/bitcoin-abe/blob/master/Abe/genesis_tx.py
                    raw_txs = ["01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff4d04ffff001d0104455468652054696d65732030332f4a616e2f32303039204368616e63656c6c6f72206f6e206272696e6b206f66207365636f6e64206261696c6f757420666f722062616e6b73ffffffff0100f2052a01000000434104678afdb0fe5548271967f1a67130b7105cd6a828e03909a67962e0ea1f61deb649f6bc3f4cef38c4f35504e51ec112de5c384df7ba0b8d578a4c702b6bf11d5fac00000000"]

                # decode transactions with
                # codecs.encode(base64.b64decode('0V73ciL1@;'),'hex').decode("utf-8") 

                result_block = {
                    'height' :  block['height'],
                    'time' : block['time'],
                    'hash' : block['hash'],
                    'version': block['version'],
                    'merkleroot' : block['merkleroot'],
                    'tx' : [base64.b64encode(codecs.decode(tx, 'hex')).decode('utf-8') for tx in raw_txs]
                }

                results.append(result_block)
                
                # we save timestamps for interesting blocks
                if i==request_since_plus_1:
                    self.min_timestamp_from_last_response = block['time']

                if i==request_to:
                    self.max_timestamp_from_last_response = block['time']

                # print("%i, %s, %i" % (i,block_hash,len(raw_txs)) )
        
        except (socket.error, HTTPException) as e:
            self._init_rpc_connection()
            raise TimelineScraperError(e, seconds_to_wait = 10)

        # Setting the new status
        if request_since:
            self.should_continue = not (request_since_plus_1 == request_since+1)
        else:
            self.should_continue = not (request_since_plus_1 == 0)

        self.min_id_from_last_response = request_since_plus_1
        self.max_id_from_last_response = request_to
    
        return results

    def has_next(self):
        return self.should_continue
    
    # We use block height as id for responses
    def get_min_id_from_last_response(self):
        return self.min_id_from_last_response

    # Returns block height 
    def get_max_id_from_last_response(self):
        return self.max_id_from_last_response

    # We use block timestamp
    def get_max_timestamp_from_last_response(self):
        return self.max_timestamp_from_last_response

    # We use block timestamp
    def get_min_timestamp_from_last_response(self):
        return self.min_timestamp_from_last_response