import logging
from threading import Thread
from typing import List

import uvicorn
from fastapi import FastAPI
from injector import singleton, inject, Injector, Module
from kombu import Consumer
from starlette.config import Config

from common.amqp import Worker
from common.module import modules
from common.utils import InjectorUtils

LOGGER = logging.getLogger(__name__)


@singleton
@inject
class Application:
    def __init__(self,
                 fast_api: FastAPI,
                 config: Config,
                 context: Injector):
        super().__init__()
        self.config = config
        self.fast_api = fast_api
        self.context = self.fast_api.__injector__ = context

    def install(self, module: Module) -> 'Application':
        self.context.binder.install(module)
        return self

    @classmethod
    def get_instance(cls) -> 'Application':
        InjectorUtils.patch_injector()
        injector = Injector(modules)
        return injector.get(cls)

    def start_kombu_worker(self):
        worker = self.context.get(Worker)
        t = Thread(target=worker.run)
        t.daemon = True
        t.start()

    def run(self):
        # Run Kombu Worker
        number_of_consumers = len(self.context.get(List[Consumer]))
        if number_of_consumers > 0:
            self.start_kombu_worker()

        server_host = self.config('SERVER_HOST',
                                  cast=str,
                                  default='localhost')
        server_port = self.config('SERVER_PORT',
                                  cast=int,
                                  default=8080)
        log_level: str = self.config('LOG_LEVEL',
                                     cast=str,
                                     default='INFO')
        uvicorn.run(self.fast_api, host=server_host, port=server_port, log_level=log_level.lower())
