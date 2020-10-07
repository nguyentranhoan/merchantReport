import logging
from concurrent.futures import ThreadPoolExecutor, Executor

from elasticsearch import Elasticsearch
from injector import Module, singleton, provider
from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings


# Provide ElasticSearch and ElasticSearch DSL from configurations
class ThreadExecutorProvider(Module):

    @provider
    @singleton
    def provide_executor(self) -> Executor:
        thread_executor = ThreadPoolExecutor(4)
        return thread_executor
