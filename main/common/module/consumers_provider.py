import inspect
import logging
from typing import List

from injector import Module, singleton, multiprovider, Injector
from kombu import Consumer

from common.amqp import is_consumer
from common.controller import is_router

LOGGER = logging.getLogger(__name__)


class ConsumerProvider(Module):

    @staticmethod
    def __is_common_module(member):
        member_name: str = member.__name__ or member['__name__']
        names = ['requests', 'chardet', 'sys', 'builtins']
        return any([member_name.startswith(name) for name in names])

    def load(self) -> List[Consumer]:
        self._tracked_members = set()
        self._consumer = []
        try:
            import consumer
            self._load_module(consumer)
            return self._consumer
        except Exception:
            return []

    def _load_module(self, module=None):
        # members = controller | module, skip common modules
        members = inspect.getmembers(module,
                                     lambda m: m is
                                               not module
                                               and (is_consumer(m) or inspect.ismodule(m))
                                               and not self.__is_common_module(m))
        for (member_name, member) in members:
            if member in self._tracked_members:
                continue
            else:
                self._tracked_members.add(member)

            if is_consumer(member):
                self._consumer.append(member)
            if inspect.ismodule(member):
                self._load_module(member)

    def __init__(self) -> None:
        super().__init__()

    @multiprovider
    @singleton
    def provide_consumers(self, injector: Injector) -> List[Consumer]:
        consumers = self.load()
        return [injector.get(Consumer) for Consumer in consumers]
