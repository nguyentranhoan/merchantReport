import logging

from common.utils import fullname
from injector import singleton, provider, Module
from pymongo import MongoClient
from starlette.config import Config

LOGGER = logging.getLogger(__name__)


# Provide Mongo Client from configuration
class MongoClientProvider(Module):
    @provider
    @singleton
    def provide(self, config: Config) -> MongoClient:
        host = config('MONGO_URL',
                      cast=str,
                      default='localhost')

        port = config('MONGO_PORT',
                      cast=int,
                      default=6379)

        max_pool_size = config('MONGO_MAX_POOL_SIZE',
                               cast=int,
                               default=100)

        username = config('MONGO_USER', cast=str, default='')

        password = config('MONGO_PASSWORD', cast=str, default='')

        db = config('MONGO_DB', cast=str, default='local')

        authMechanism = config('MONGO_AuthMechanism', cast=str, default='SCRAM-SHA-256')

        # LOGGER.debug('host: ' + str(host))
        # LOGGER.debug('port: ' + str(port))
        # LOGGER.debug('db: ' + str(db))
        # LOGGER.debug('pool_size: ' + str(max_pool_size))
        # LOGGER.debug('username: ' + str(username))
        # LOGGER.debug('password: ' + str(password))

        try:
            client = MongoClient(host=host, port=port, username=username, password=password, maxPoolSize=max_pool_size,
                                 authMechanism=authMechanism, authSource=db)[
                db]
            LOGGER.debug(fullname(MongoClient) + ' configurated')
        except:
            LOGGER.debug('Can not connect db')

        return client
