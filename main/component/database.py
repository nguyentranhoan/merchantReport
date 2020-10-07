import logging

from injector import inject, singleton
from starlette.config import Config

from common.database import BaseDatabase

LOGGER = logging.getLogger(__name__)


@singleton
@inject
class MasterDatabase(BaseDatabase):

    def __init__(self, config: Config) -> None:
        super().__init__(config)
        self.__database_url: str = config('MASTER_DATABASE_URL', str)

        LOGGER.debug('Master Session Maker Initialized')
        self.test_connection()

    @property
    def get_db_url(self) -> str:
        return self.__database_url


@singleton
@inject
class ReplicaDatabase(BaseDatabase):

    def __init__(self, config: Config) -> None:
        super().__init__(config)
        self.__database_url: str = config('REPLICA_DATABASE_URL', str)

        LOGGER.debug('Replica Session Maker Initialized')
        self.test_connection()

    @property
    def get_db_url(self) -> str:
        return self.__database_url
